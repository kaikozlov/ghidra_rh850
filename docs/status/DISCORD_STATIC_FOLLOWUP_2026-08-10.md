# Discord static follow-up — 2026-08-10

Focused static-analysis sprint prompted by recent comma `#toyota-security`
discussion supplied as screenshots in the active research session. The
screenshots are **external-source observations**, not primary firmware evidence;
they are not archived as binary artifacts in this repository. This document
tracks what can be established from already pinned/local artifacts before
requesting new files from participants.

## Input observations to test, not assume

The screenshots report or discuss:

- a 2023 US Corolla route where genuine incoming SecOC-like traffic was
  identified on `0x00F`, `0x116`, and `0x24D`, while apparent steering traffic
  on `0x2E4`/`0x191` was later recognized as Panda-returned openpilot traffic;
- a successful 32 KiB Corolla EPS DataFlash dump after changing the physical
  CAN pair presented as Panda bus 0, followed by `0/30 protected` from the
  current extraction workflow;
- ordinary UDS responses when targeting the EPS on Panda bus 1 but programming
  timeout, versus successful programming after a physical CAN0/CAN1 harness
  pair swap and use of bus 0;
- persistent community EPS patch application on a live 2024 RAV4 Prime and
  2025 bZ4X, with the RAV4 Prime openpilot experiment later reporting
  `U023A87` / missing Image Processing Module message;
- concern that forcing an older RAV4/Corolla profile may itself be invalid for
  the newer TSS3 network regardless of SecOC bypass status.

No vehicle-specific conclusion is promoted from those screenshots alone.

## Step checklist

- [x] Step 1 — audit the current DataFlash/SecOC extractor and build a generic
  classic-Toyota offline oracle
- [x] Step 2 — statically resolve Panda ELM327/bus-routing assumptions and build
  a non-destructive bus-discovery plan/tool
- [ ] Step 3 — statically audit the forced RAV4 Prime openpilot profile and
  decode the `U023A87` Techstream context
- [ ] Step 4 — prepare an automated F3/F4 community patch-predicate analyzer
- [ ] Step 5 — split the new 2023 US Corolla evidence from the existing
  `8965F1208000` variant and reconcile status/requests

## Step 1 — community extractor and generic SecOC oracle

### Primary/pinned inputs

- `Bk2ol/tsk_extraction_by_can_log` at
  `db453752beeb7cdd024a1a9c38c6711c981e75ad`
- commaai/opendbc at `c9b31d21bc396e8958891e271936bdbdf1a6ca93`
- `opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc`
- `opendbc/car/secoc.py`
- repository firmware-derived classic SecOC construction

### Static findings

The Bk2ol workflow's **dump bootstrap** and its **post-dump oracle** have
separate portability boundaries. The current oracle is hardcoded to:

```text
collector buses:       {0, 2}
collector IDs:         {0x00F, 0x131, 0x2E4, 0x344}
protected verify IDs:  {0x131, 0x2E4, 0x344}
verify buses:          {0, 2}
EPS probe/dump bus:    0
```

Pinned opendbc defines the same classic 28-bit authenticator/reset/message-low2
trailer family on eight ordinary protected IDs:

```text
0x116  GAS_PEDAL
0x131  STEERING_LTA_2
0x177  PCM_CRUISE_3
0x183  ACC_CONTROL_2
0x24D  PCM_CRUISE_4
0x283  PRE_COLLISION
0x2E4  STEERING_LKA
0x344  PRE_COLLISION_2
```

with `0x00F` synchronization.

Therefore a literal `0 protected` result from the unmodified Bk2ol verifier
means only that no samples from **its three protected IDs on its two accepted
buses** reached verification. It cannot establish that another variant has no
SecOC traffic.

### Durable work

Added:

- `data/toyota_classic_secoc_profile.csv`
- `tools/toyota_secoc_oracle.py`
- `tests/verify_toyota_secoc_oracle.py`
- `docs/tooling/community-dataflash-secoc.md`

The local oracle tracks synchronization per arbitrary bus, recognizes the full
pinned classic profile, verifies each observed protected ID independently, and
sliding-scans 16-byte DataFlash windows after a sync-CMAC prefilter. Synthetic
coverage deliberately uses bus 1 and `0x116`/`0x24D`.

### Verification

- `tests/verify_toyota_secoc_oracle.py` — 37/37 pass
- optional pinned-source `verify_external_corroboration.py` — 222/222 pass
- finding: `SECOC-032`

### Boundary

The tool is now ready to process a future Corolla dump/capture, but no Corolla
key/storage conclusion is possible without those artifacts. The eight-ID DBC
profile is a known Toyota classic-SecOC vocabulary, not proof that every listed
ID appears on the 2023 Corolla or shares one production key.

### Commit

- `64f582f9426cc4095aa6e278035fc32c4738d1b1 analysis: generalize Toyota SecOC offline oracle`

## Step 2 — Panda ELM327 and Toyota diagnostic bus routing

### Primary/pinned inputs

- Calvin Park openpilot/Panda checkout at
  `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822`
- `panda/board/main.c`
- `panda/board/boards/tres.h`
- `panda/board/drivers/can_common.h`
- `opendbc_repo/opendbc/safety/modes/elm327.h`
- Bk2ol probe/dump source from Step 1

### Static findings

Pinned safety/Panda source establishes:

```text
ELM327 param 0     -> CAN_MODE_OBD_CAN2
                    -> logical bus 1 multiplexed to OBD-II CAN
ELM327 param != 0  -> CAN_MODE_NORMAL
harness flipped    -> logical bus 0/2 orientation swaps
logical bus 1      -> remains MCU CAN2
```

Tres/Red board code additionally shows that `CAN_MODE_NORMAL` versus
`CAN_MODE_OBD_CAN2` changes the physical FDCAN2 pin/transceiver selection. The
current Bk2ol dumper combines implicit ELM327 parameter 0 with hardcoded logical
bus 0; changing only its `BUS` constant does not keep the physical-routing
context fixed.

This is enough to reject a premature conclusion that the observed bus-1
programming timeout is necessarily ECU behavior. It is **not** enough to prove
that software configuration can replace the physical repin, because live ACK,
reset, gateway, and harness behavior remain unmeasured.

### Durable work

Added:

- `docs/tooling/panda-toyota-routing.md`
- `tools/toyota_eps_bus_probe.py`
- `tests/verify_toyota_eps_bus_probe.py`

The probe defaults to a dry run. With explicit `--execute`, it selects ELM327
parameter 1 (normal routing) and sends only `22 F1 81` to `0x7A1 -> 0x7A9` on
logical buses 0/1/2. It never enters programming, requests SecurityAccess,
writes a DID, downloads code, starts a routine, or resets the ECU.

### Verification

- `tests/verify_toyota_eps_bus_probe.py` — 17/17 pass
- optional pinned-source `verify_external_corroboration.py` — 247/247 pass;
  locks Panda ELM327, CAN orientation, Tres mux, and Bk2ol call-site semantics
- finding: `SECOC-033`

### Boundary

The next live routing experiment can now be a read-only `(ELM327 param, logical
bus) -> F181 response` matrix rather than another harness repin. Programming
behavior should only be retested after the physical/logical route is known.

### Commit

- pending
