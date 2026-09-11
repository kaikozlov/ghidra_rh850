# TSS 3.0 Corolla port — architecture & change reference

Companion to `README.md` (narrative) and `NOTES.md` (chronology). Four sections:

1. **Conceptual problems** — what makes a TSS 3.0 car hard, and how each was solved.
2. **opendbc changes** — vs `b4ef5e1c`, with code.
3. **sunnypilot changes** — vs staging, with code.
4. **panda firmware changes** — vs `75aa44be`, with code.

Changes are additive; existing Toyota behavior is unchanged (panda regression
`test_toyota.py`, 1118 tests, still passes).

================================================================================
# SECTION 1 — THE CONCEPTUAL PROBLEMS
================================================================================

**1.1 CAN FD.** The ADAS bus is CAN FD (32-byte frames, ~2 Mbit/s data phase,
BRS). Classic Toyota support assumes 8-byte/500 kbps. → new 32-byte DBC; panda
already forwards/transmits FD natively (Section 4).

**1.2 Bus topology.** Measured (stock Toyota-B harness): powertrain on **bus 1**
(unrelayed); ADAS CAN FD on **bus 0/2** (relayed; camera on bus 2, radar+gateway
on bus 0). Classic Toyota reads bus 0. → `TSS3_PT_BUS = 1`; interception only on
the relayed pair. Verified by camera-unplug (only 0x020/0x160/0x230/0x440 vanished).

**1.3 SecOC.** Safety-critical messages carry a truncated AES-CMAC + freshness
counter; forging needs the key. → the *acceleration request* (0x160) is NOT SecOC
(1.4); for steering, the **owner's EPS is patched to accept any MAC ("always-yes")**,
removing the key as a blocker (lateral, in progress).

**1.4 AUTOSAR E2E (the crack).** 0x160 is protected by a keyless CRC, not SecOC:
`CRC-16/CCITT poly 0x1021 init 0 over payload[2:]+DataID(0x444A LE)`, counter in
byte 2. **Keyless ⇒ forgeable** — this is *why* longitudinal was possible. →
`e2e.py` (2.6).

**1.5 Fingerprint.** The sub-0x800 byte fingerprint doesn't cleanly ID this car.
→ force the platform via `CarPlatformBundle` (3.1); no `fingerprints.py` entry.

**1.6 Interception model.** The powertrain accel command (0x13C) is downstream on
the unrelayed bus 1. The camera's *request* (0x160) is on the relayed bus. →
**modify-and-forward**: overwrite 0x160's accel, recompute counter+CRC, tx on bus 0.

**1.7 The handoff seam.** Early LIVE tripped "System Malfunction" at transitions
(stops, low-speed engage): control passing between openpilot and the camera left a
gap or an E2E counter jump. → (a) openpilot is the **sole emitter whenever
engaged** (relays the camera's frame when not actively controlling); (b) **stamp
the camera's own counter**; (c) align the emit / block / tx-permit gates on one
`longitudinal_allowed` state.

**1.8 Standstill / no-lead authority.** The 0-mph hold uses the camera's own
mechanism (not a plain 0x160 accel), so openpilot relays below ~1 mph and TSS
holds. The stock ACC keeps openpilot authorized to 0 mph *with a lead* but drops
~19 mph *without* one — the open question for future no-lead (red-light) stops.

================================================================================
# SECTION 2 — CHANGES TO OPENDBC (vs b4ef5e1c)
================================================================================

## 2.1 opendbc/car/toyota/values.py — ADDED

```python
class ToyotaFlags(IntFlag):
    ...
    CAN_FD = 4096                       # ADDED: marks the TSS3 CAN FD platform

class ToyotaSafetyFlags(IntFlag):
    ...
    TSS3 = (16 << 8)                    # ADDED: panda safety-param flag

# ADDED: TSS3 is CAN FD + SecOC, distinct from the 8-byte SecOC config
class ToyotaCanFDSecOCPlatformConfig(PlatformConfig):
  dbc_dict: dict = field(default_factory=lambda: {Bus.pt: 'toyota_corolla_tss3_pt'})
  def init(self):
    self.flags |= ToyotaFlags.TSS2 | ToyotaFlags.NO_DSU | ToyotaFlags.SECOC | ToyotaFlags.CAN_FD

class CAR(Platforms):
  ...
  TOYOTA_COROLLA_TSS3 = ToyotaCanFDSecOCPlatformConfig(   # ADDED
    [ToyotaSecOcCarDocs("Toyota Corolla 2023", min_enable_speed=MIN_ACC_SPEED)],
    CarSpecs(mass=..., wheelbase=2.64, steerRatio=13.9, tireStiffnessFactor=0.444),
  )

# ADDED: the longitudinal switch + tuning constants
class TSS3LongMode:
  OFF = 0; SHADOW = 1; LIVE = 2
TSS3_LONG_MODE = TSS3LongMode.OFF
TSS3_PT_BUS = 1                         # powertrain bus (not bus 0!)
TSS3_MIN_OVERRIDE_SPEED = 0.45         # m/s (~1 mph); below it, relay to camera
```

## 2.2 opendbc/car/toyota/carstate.py — ADDED

New read-only decode path + parser wiring on the correct buses:

```python
def update_tss3(self, can_parsers):        # ADDED (read-only)
    cp = can_parsers[Bus.pt]
    ret = structs.CarState()
    self.parse_wheel_speeds(ret, cp.vl["WHEEL_SPEEDS"][...], ...)
    ret.steeringAngleDeg = cp.vl["STEER_ANGLE_ACC_STATUS"]["STEER_ANGLE"]
    ret.brakePressed = cp.vl["BRAKE_MODULE"]["BRAKE_PRESSED"] != 0
    ret.gasPressed   = cp.vl["GAS_PEDAL"]["GAS_PEDAL_USER"] != 0      # 0x116 b1
    ret.cruiseState.enabled     = bool(cp.vl["STEER_ANGLE_ACC_STATUS"]["ACC_ENGAGED"])
    ret.cruiseState.standstill  = bool(cp.vl["STEER_ANGLE_ACC_STATUS"]["ACC_STANDSTILL"])
    # capture the camera's live 0x160 (from the cam parser) as the tx template
    self.tss3_accel_template   = <32 raw bytes from ADAS_ACC_REQUEST on bus 2>
    self.tss3_stock_lon_active = bool(cp.vl["ACC_CONTROL"]["LON_ACTIVE"])
    return ret, ret_sp

# get_can_parsers TSS3 branch — pt on bus 1, cam (ADAS request) on bus 2
Bus.pt:  CANParser(dbc, tss3_messages, TSS3_PT_BUS),
Bus.cam: CANParser(dbc, [("ADAS_ACC_REQUEST", 40)], 2),
```

## 2.3 opendbc/car/toyota/carcontroller.py — ADDED (the no-handoff tx block)

```python
if self.CP.flags & ToyotaFlags.CAN_FD.value:
    tss3_sends = []
    template = CS.tss3_accel_template
    cam_counter = template[2] if template is not None else None

    # openpilot is the SOLE emitter of 0x160 whenever engaged (no camera handoff).
    engaged = (TSS3_LONG_MODE == TSS3LongMode.LIVE
               and self.CP.openpilotLongitudinalControl
               and CS.out.cruiseState.enabled          # == panda controls_allowed (0x8A)
               and not CS.out.gasPressed
               and template is not None)
    controlling = engaged and CC.longActive and CS.out.vEgo > TSS3_MIN_OVERRIDE_SPEED

    if engaged and cam_counter != self.tss3_last_cam_counter:   # one per camera frame
        self.tss3_last_cam_counter = cam_counter
        accel = float(np.clip(actuators.accel, -1.5, 1.5)) if controlling else None  # None = relay
        tss3_sends.append(toyotacan.modify_accel_160(template, accel, cam_counter))
    elif not engaged:
        self.tss3_last_cam_counter = cam_counter

    new_actuators = actuators.as_builder()
    new_actuators.accel = float(np.clip(actuators.accel, -1.5, 1.5)) if controlling else 0.
    self.frame += 1
    return new_actuators, tss3_sends      # returns BEFORE any classic-Toyota tx
```

## 2.4 opendbc/car/toyota/toyotacan.py — ADDED

```python
def modify_accel_160(template: bytes, accel, counter: int):
    buf = bytearray(template)
    if accel is not None:                                   # None => RELAY camera's accel
        raw = max(-16384, min(16383, int(round(accel / 0.001)))) & 0x7FFF
        buf[4] = (buf[4] & 0x80) | ((raw >> 8) & 0x7F)      # preserve byte4 bit7 flag
        buf[5] = raw & 0xFF
    buf[2] = counter & 0xFF                                  # camera's own counter
    return CanData(0x160, apply_e2e_160(bytes(buf)), 0)     # recompute E2E CRC, bus 0
```

## 2.5 opendbc/car/toyota/interface.py `_get_params` — ADDED (TSS3 branch)

```python
if ret.flags & ToyotaFlags.CAN_FD.value:
    ret.minEnableSpeed = MIN_ACC_SPEED
    ret.alphaLongitudinalAvailable = TSS3_LONG_MODE != TSS3LongMode.OFF
    ret.openpilotLongitudinalControl = TSS3_LONG_MODE != TSS3LongMode.OFF   # param-independent
    if not ret.openpilotLongitudinalControl or TSS3_LONG_MODE == TSS3LongMode.SHADOW:
        ret.safetyConfigs = [get_safety_config(SafetyModel.noOutput)]        # OFF/SHADOW: no tx
    else:
        ret.safetyConfigs[0].safetyParam &= ~ToyotaSafetyFlags.STOCK_LONGITUDINAL.value
        ret.safetyConfigs[0].safetyParam |= ToyotaSafetyFlags.TSS3.value     # LIVE: permit tx
```
(The authoritative second pass, `_get_params_sp`, is in 3.2.)

## 2.6 opendbc/car/toyota/e2e.py — NEW FILE

```python
E2E_160_DATA_ID = 0x444A
def _crc16_ccitt(data):
    reg = 0
    for b in data:
        reg ^= b << 8
        for _ in range(8):
            reg = ((reg << 1) ^ 0x1021) & 0xFFFF if reg & 0x8000 else (reg << 1) & 0xFFFF
    return reg & 0xFFFF
def e2e_160_checksum(p, data_id=E2E_160_DATA_ID):
    return _crc16_ccitt(bytes(p[2:]) + bytes([data_id & 0xFF, data_id >> 8]))
def apply_e2e_160(p, counter=None):
    buf = bytearray(p)
    if counter is not None: buf[2] = counter & 0xFF
    c = e2e_160_checksum(buf); buf[0] = c & 0xFF; buf[1] = (c >> 8) & 0xFF
    return bytes(buf)
def e2e_160_valid(p):
    return e2e_160_checksum(p) == ((p[1] << 8) | p[0])
```

## 2.7 opendbc/dbc/toyota_corolla_tss3_pt.dbc — NEW FILE

Powertrain (bus 1) + the camera's ADAS request (0x160). Key message:

```
BO_ 352 ADAS_ACC_REQUEST: 32 XXX         # 0x160, 32-byte CAN FD, camera
 SG_ ACCEL_REQ : 38|15@0- (0.001,0) [-16.384|16.383] "m/s^2" XXX
 SG_ COUNTER   : 23|8@0+ (1,0) [0|255] "" XXX
 SG_ BYTE00 .. BYTE31 : (raw bytes, so carState reconstructs the exact template)
```
Plus WHEEL_SPEEDS(0xAA), STEER_ANGLE_ACC_STATUS(0x8A), STEER_TORQUE_SENSOR(0xDA),
BRAKE_MODULE(0x101), GAS_PEDAL(0x116), ACC_CONTROL(0x13C), GEAR_PACKET, etc.

================================================================================
# SECTION 3 — CHANGES TO SUNNYPILOT (vs staging)
================================================================================

Fork-specific machinery (some in the same files, but sunnypilot additions).

## 3.1 Forced platform via CarPlatformBundle (fixed_fingerprint) — no code change
sunnypilot's `card.py` applies `CarPlatformBundle` as `fixed_fingerprint`. Set on
the device (not code):
```
CarPlatformBundle = {"platform":"TOYOTA_COROLLA_TSS3","make":"Toyota",
  "brand":"toyota","model":"Corolla","year":["2023"],"package":"All",
  "name":"Toyota Corolla 2023"}
```

## 3.2 interface.py `_get_params_sp` — ADDED (the AUTHORITATIVE pass)
sunnypilot's second pass overwrites `openpilotLongitudinalControl` for every
`TSS2_CAR - RADAR_ACC_CAR`, clobbering the first-pass config — so TSS3 had to be
handled here too, and this is the value that actually takes effect:

```python
if stock_cp.flags & ToyotaFlags.CAN_FD.value:                       # ADDED
    stock_cp.alphaLongitudinalAvailable   = TSS3_LONG_MODE != TSS3LongMode.OFF
    stock_cp.openpilotLongitudinalControl = TSS3_LONG_MODE != TSS3LongMode.OFF
    stock_cp.minEnableSpeed = MIN_ACC_SPEED
    if not stock_cp.openpilotLongitudinalControl or TSS3_LONG_MODE == TSS3LongMode.SHADOW:
        stock_cp.safetyConfigs = [get_safety_config(SafetyModel.noOutput)]
    else:
        cfg = get_safety_config(SafetyModel.toyota)
        cfg.safetyParam = (EPS_SCALE[candidate] | ToyotaSafetyFlags.SECOC.value
                           | ToyotaSafetyFlags.TSS3.value)
        stock_cp.safetyConfigs = [cfg]
```

## 3.3 Param-independent SHADOW/LIVE (AlphaLongitudinalEnabled workaround)
sunnypilot's UI auto-deletes `AlphaLongitudinalEnabled` whenever the car is
offroad or `alphaLongitudinalAvailable` is False:
```python
# openpilot/selfdrive/ui/sunnypilot/ui_state.py (baseline sunnypilot behavior)
if not CP.alphaLongitudinalAvailable:
    self.params.remove("AlphaLongitudinalEnabled")
```
Gating the planner on that param therefore silently disabled SHADOW. **Fix (in
both interface passes):** drive control off `TSS3_LONG_MODE`, not the param —
```python
ret.openpilotLongitudinalControl = (TSS3_LONG_MODE != TSS3LongMode.OFF)   # not `alpha_long`
```

## 3.4 sunnypilot SP imports — reused unchanged
`interface.py`/`carstate.py` import `ToyotaFlagsSP`, `ToyotaSafetyFlagsSP`,
`CarStateExt` from `opendbc/sunnypilot/car/toyota/`. TSS3 reuses them as-is; the
TSS3 safety flag lives in the base `ToyotaSafetyFlags`, not the SP set. No change.

## 3.5 Device params / operational — no code change
- `DisableUpdates = 1` so manual file edits persist (sunnypilot would re-sync and revert).
- Firmware must be a DEBUG build (`ALLOW_DEBUG`) for the TSS3 safety param.

## 3.6 Not changed
No `fingerprints.py`, `car_list.json`, `substitute.toml`, or sunnypilot UI change
is required for function.

================================================================================
# SECTION 4 — CHANGES TO PANDA FIRMWARE (vs 75aa44be)
================================================================================

All in `opendbc/safety/modes/toyota.h` (full diff in `panda-safety-tss3.patch`),
additive, gated behind `ALLOW_DEBUG`. Because the powertrain is on bus 1, the TSS3
safety reads bus 1 — unlike every other Toyota, which reads bus 0.

## 4.1 Param + TX allowlist — ADDED
```c
static bool toyota_tss3 = false;                 // ADDED
// in toyota_init (under ALLOW_DEBUG):
const uint32_t TOYOTA_PARAM_TSS3 = 16UL << TOYOTA_PARAM_OFFSET;
toyota_tss3 = GET_FLAG(param, TOYOTA_PARAM_TSS3);

// only message openpilot may send; no lateral tx.
#define TOYOTA_TSS3_LONG_TX_MSGS \
  {0x160, 0, 32, .check_relay = true, .disable_static_blocking = true},
```
`disable_static_blocking` hands the camera-copy decision to the fwd hook (4.4).

## 4.2 TX accel check on 0x160 — ADDED (in toyota_tx_hook)
```c
const LongitudinalLimits TOYOTA_TSS3_LONG_LIMITS = {  // STOCK range: relayed
  .max_accel = 2000,   // 2.0 m/s2                     // camera stops reach ~-3.3
  .min_accel = -3500,  // -3.5 m/s2                     // (op's own accel self-clamped +/-1.5)
};
if (toyota_tss3 && (msg->addr == 0x160U)) {
  int desired_accel = ((msg->data[4] & 0x7FU) << 8) | msg->data[5];
  desired_accel = to_signed(desired_accel, 15);
  tx = !longitudinal_accel_checks(desired_accel, TOYOTA_TSS3_LONG_LIMITS);
}
```

## 4.3 RX on bus 1 — ADDED (in toyota_rx_hook; classic Toyota only reads bus 0)
```c
if (toyota_tss3 && (msg->bus == 1U)) {
  if (msg->addr == 0x8AU) {                       // cruise engaged (byte22 mask 0x10)
    pcm_cruise_check(GET_BIT(msg, 180U));
    acc_main_on = msg->data[7] != 0U;
  }
  if (msg->addr == 0xAAU) { /* sum 4 wheel speeds -> UPDATE_VEHICLE_SPEED */ }
  if (msg->addr == 0x101U) { brake_pressed = GET_BIT(msg, 3U); }   // 0x101 b3
  if (msg->addr == 0x116U) { gas_pressed  = msg->data[1] != 0U; }  // 0x116 b1
}
```
Plus TSS3 RX_CHECKS (0xaa, 0x8a, 0x101, 0x116) on bus 1, selected in toyota_init.

## 4.4 Forwarding hook — ADDED (gap-free selective pass-through)
```c
static bool toyota_fwd_hook(int bus_num, int addr) {   // ADDED; toyota had no .fwd
  bool block = false;
  if (toyota_tss3 && (bus_num == 2) && (addr == 0x160)) {
    block = get_longitudinal_allowed();   // block camera's 0x160 iff openpilot is emitting
  }
  return block;
}
const safety_hooks toyota_hooks = {
  .init = toyota_init, .rx = toyota_rx_hook, .tx = toyota_tx_hook,
  .fwd = toyota_fwd_hook,                  // ADDED
  ...
};
```
Keying the block on `get_longitudinal_allowed()` (controls_allowed && !gas) — the
same state openpilot uses to emit — is what makes the handoff (and gas override)
gap-free: the camera forwards the instant openpilot stops, never both, never neither.

## 4.5 Init wiring — MODIFIED
```c
// toyota_init: TSS3 takes precedence over the SecOC table (this car is both)
if (toyota_tss3) { SET_TX_MSGS(TOYOTA_TSS3_LONG_TX_MSGS_ARR, ret);
                   SET_RX_CHECKS(toyota_tss3_rx_checks, ret); }
else if (toyota_secoc) { ... }   // unchanged
```

## 4.6 CAN FD forwarding/transmit — NO CHANGE NEEDED
`fdcan.h` already preserves the FD flag, DLC, and full 64-byte payload when
forwarding, and buses auto-enable FD+BRS on the first FD frame. Verified by
reading the firmware; no edit required for FD itself.

## 4.7 Build/flash
DEBUG build (auto-defines `ALLOW_DEBUG`). Flash by replacing the device's
`panda/board/obj/panda_h7.bin.signed` and restarting — pandad reflashes on the
signature mismatch and refuses to boot if they differ, so it sticks.

================================================================================
# STATUS (2026-09-10)
================================================================================
- Fingerprint + Phase 1 (read-only): DONE on car.
- Longitudinal (follow, speed, stop-and-go to 0 + hold, resume): VALIDATED on car;
  TSS does only the 0-1 mph hold (1 mph floor deployed, awaiting a confirming drive).
- Lateral: IN PROGRESS. EPS SecOC is owner-patched (always-yes), so the key is not
  a blocker. Next: a stock-LTA-active log to find the steering command's message,
  bus, angle encoding, and framing.
