# Camry F33 EPS network-only recovery runbook

## Executive conclusion

The recovery effort is restricted to the existing vehicle network. Under-car,
rack, wheel, and connector work is out of scope. The previously described A30
isolation experiment is therefore shelved; it is not a prerequisite or fallback
in this runbook.

Two network avenues remain worth executing, in this order:

1. Make one finite, read-only capture on the already proven post-repin route.
   This qualifies the physical route through Brake/EPB, identifies the actual
   central-gateway endpoint, retries the primary EPS listener once, and queries
   the exact firmware's separate application-only `0x7A0 -> 0x7A8` listener
   once.
2. Use current, registered Toyota GTS+ online to perform a full Health Check and
   live CAN Bus Check, then inspect the EMPS `Configure`, `Calibration Update`,
   and `ECU Security Key` fields. If the exact VIN is offered an EMPS
   Software-as-a-Part/Restoration package, acquire the file list or download the
   package and stop before GTS+ begins reprogramming.

These are not interchangeable. The raw capture can reveal a surviving target
executor. GTS+/TIS is the supported source that may supply the missing exact
package and, only if the target is admitted, can own the manufacturer-defined
gateway preparation. Package
availability remains unproved. A response from the gateway alone cannot program
the EPS, and a factory replacement-ECU workflow is not proof that a silent
installed ECU can be revived.

Recovered current Unified host logic materially narrows the second avenue:
ordinary EPS CID discovery requires `22 F1 81 -> 62 F1 81` before
`StartPrepareWrite`, so a totally silent `0x7A1` normally never reaches gateway
preparation. Only a missing exact package could select the recovered pre-CID
local-bus flow or another package-specific admission exception; none of the 26
retained CUWs does. GTS+ is therefore an exact-package/admission experiment,
not an assumed network wake-up mechanism.

The strongest positive is conditional but real: authenticated RAM execution
was already accepted by this exact F33 before the incident, and the retained
incident package has a hash-bound inverse restore payload. If the primary
application or boot diagnostic executor responds, a network-only restoration
path exists. A secondary-listener response alone proves application execution
but cannot request the programming handoff. The unresolved question is
reachability of the primary executor after the malformed installed call, not
whether the exact target ever supported the required network writer.

No new live request, session transition, gateway preparation, reset, upload, or
flash operation was performed while preparing this runbook.

## Exact target and route

The vehicle-specific identities and routes are:

| Item | Exact value |
|---|---|
| Vehicle profile | North American Camry HV, current GTS vehicle type `12704` |
| EPS / EMPS | category 405, request `0x7A1`, response `0x7A9` |
| Preincident EPS F181 | `02 || 8965F3307000[16] || 8A3113303100[16]` |
| Preincident EPS F18C | `8965033K9011J2740743` |
| Brake/EPB | category 435, request `0x7B0`, response `0x7B8` |
| Brake/EPB F181 | `F152633K0000` |
| Central gateway | request `0x750`, response `0x758`, address extension `0x5F` |
| Secondary EPS application listener | request `0x7A0`, response `0x7A8` |
| Current installed Comma route | post-repin normal-harness Panda bus 0 |

Toyota GTS “Bus 4” and Panda bus 0 are different namespaces. The current
post-repin installation was live-proven on Panda bus 0; the August 26
pre-repin capture used Panda bus 1 and must not be copied into a current command.
The route history is pinned in
[`targets/camry-2026/README.md`](../../targets/camry-2026/README.md).

The retained postincident evidence already establishes that Brake/EPB survived
and answered on `0x7B8`, while two primary EPS TesterPresent requests received
no `0x7A9` reply. No postincident Brake DID `0x102F` or central-gateway node-`5F`
exchange was retained. Ten secondary `0x7A0` requests were retained only on the
now-wrong Panda bus 1, with no `0x7A8` reply; the application-only listener has
not been tested on the current post-repin bus 0. Those are useful coverage gaps;
another broad bus sweep is not.

## Operating boundary

Keep the car parked, ignition ON, and hybrid system READY OFF. Use a stable
12-V support supply appropriate for diagnostics. Do not clear DTCs, run Active
Tests, run EPS Initial Setting or Assist Map Clear, send ECUReset, change a
gateway mode manually, request SecurityAccess, enter a programming session, or
write memory during the first capture.

Use one owner of the diagnostic interface. If direct Panda access is selected,
stop the normal Panda-owning processes first. Do not run a separate raw
`--obd-multiplexing` client: the exact-target command owns the temporary OBD
mux switch and restoration inside one process. A positive Brake response is
required before EPS silence has meaning.

## Stage 1 — finite read-only network capture

Use the exact-target triage command. It owns one direct USB Panda for the whole
sequence, has no caller-selectable addresses or payloads, and defaults to a
hardware-free JSON plan:

```sh
tools/toyota target run camry live/f33-eps-network-triage -- --include-gateway
```

Review that plan first. On this workstation the repository's locked Python
environment intentionally does not install Panda/opendbc. The already verified
diagnostics environment supplies those transport packages without importing
any sibling project code. The live command is therefore:

```sh
PYTHONPATH=/Users/kai/dev/inspect/repos/toyota-diagnostics/.venv/lib/python3.12/site-packages \
  tools/toyota target run camry live/f33-eps-network-triage -- \
  --execute --include-gateway \
  --confirm-stationary \
  --confirm-ignition-on-ready-off \
  --confirm-stable-12v-support \
  --confirm-openpilot-stopped \
  --arm READ_ONLY_F33_NETWORK_TRIAGE
```

Run it from a real interactive terminal and retain the complete JSON output.
The command refuses noninteractive live use, multiple/no USB Pandas, a running
`pandad`/`boardd`, missing operator attestations, unexpected route health, or
any request outside its immutable allowlist. `--include-gateway` is still
read-only; it adds the separate node-`5F` observation and its mandatory route
restoration. No raw command below needs to be entered by hand.

Immediately after opening, the tool verifies Panda `SILENT`, then replaces any
persistent prior-client controller state with 500-kbit/s nominal, 2-Mbit/s ISO
CAN-FD timing on all three buses before it enables the fixed ELM327 diagnostic
allowlist. After the final normal-route Brake control, every exit again sets
and verifies `SILENT`; failure is an urgent nonzero stop.

Immediately before each allowlisted request, it clears Panda's global receive
backlog and host-side partial-packet buffer so an old matching frame cannot be
accepted as the new reply. It also records board and all three CAN-controller
health snapshots around every exchange. A no-reply result is classified as a
clean timeout only when safety blocking, TX/RX overflow, CAN errors, frame loss,
bus-off, and controller-reset counters did not increase, no controller ended in
warning/passive/bus-off, the safety route remained correct, and CAN-FD timing
did not drift. Because a silent single-frame exchange needs no flow control, it
also requires an aggregate `total_tx_cnt` increase of exactly one across the
three physical controllers; this is invariant to harness-flip controller
mapping and proves admission to one hardware TX FIFO. Otherwise the exchange is
a transport error, not evidence that the ECU was silent.

### 1. Qualify the route through Brake/EPB

The tool first sends only `22 10 2F` and `19 02 FF` on the fixed Brake route
`0x7B0 -> 0x7B8`, Panda bus 0.

The first exchange must receive `0x7B8`. In the ten returned DID value bytes,
decode “EPS/Steering Control Actuator ECU Communication Open” as
`(value[9] & 0x20) != 0`: zero is Toyota's `Normal` label and one is
`Under intermittent`. Preserve several unmodified samples if GTS+ can display
them; do not reduce the observation to a single label.

The second exchange sends DTC read `19 02 FF`. Preserve the status byte and any
available detail/freeze-frame record for `U0131-87`. The presence of
`U0131-87` alone is not current-liveness evidence: the exact car previously
stored status `0xAC` with the current-failure bits clear.

If Brake/EPB does not answer, stop. Resolve Panda ownership, ignition state,
normal-harness routing, and the current bus-0 mapping before interpreting any
EPS timeout.

### 2. Query the ordinary EPS endpoint once

After a well-formed Brake positive control, the tool sends one `3E 00` to the
fixed `0x7A1 -> 0x7A9` primary EPS route.

Only if a native, correlated `0x7A9` response was received, it reads F186 and
F181 and classifies the pair in the output.

Any syntactically valid positive or negative reply from `0x7A9` proves
target-side diagnostic execution. Interpret the identity pair together:

| Observation | Bounded interpretation |
|---|---|
| `62 F1 86 01` or `62 F1 86 03` | Exact application F186 implementation is running. |
| `62 F1 81 02 ...8965F3307000...8A3113303100...` | Expected application identity. |
| `62 F1 81 02` plus 32 bytes `0x21`, with `7F 22 31` to F186 | Compatible with exact boot. |
| Placeholder F181 plus positive F186 | Application fallback identity, not boot. |
| Any other identity or responder ID | Stop; do not transition sessions or upload. |
| TesterPresent times out after a positive Brake control | Primary EPS listener remains silent in the tested state; do not add identity requests. |

Negative RDBI replies do not echo the DID, so request correlation must use one
outstanding request at a time. Repeating these requests adds no new condition.

### 3. Query the exact application-only listener once

Only when Brake answered and the primary EPS TesterPresent timed out, the tool
sends one `3E 00` on the fixed `0x7A0 -> 0x7A8` secondary route.

The exact F33 application contains a distinct physical diagnostic context at
`0x7A0 -> 0x7A8` with services `10`, `19`, `22`, `3E`, and `AB`. The exact boot
tables do not contain this endpoint. Any valid `0x7A8` TesterPresent reply proves
that an application diagnostic path is executing even if the primary route
remains silent. That result is sufficient; do not add identity reads. The
secondary RDBI object is permitted only in manufacturer session `0x40`, so a
default-state F181 would only be expected to return an NRC rather than useful
identity data. Its intended OEM/manufacturing role is unknown, and it likely
shares the same application DCM executor; it is a discriminator, not an assumed
bypass.

Do not poll it repeatedly. Its SID-10 object supports only subfunctions `0x01`
and `0x40`; it does not expose the primary endpoint's `0x03`/`0x02`
application-to-boot ladder. Do not enter session `0x40` merely to obtain F181,
and do not send SID `0xAB`. Preserve any reply and move to the conditional
decision below.

### 4. Identify the exact central-gateway endpoint on its separate OBD route

This query is not made on the post-repin EPS/Brake path. With
`--include-gateway`, the same process temporarily selects the OBD mux, verifies
ELM327 safety mode/parameter `3/0`, and sends `3E 00` on Panda bus 1 to
`0x750/0x758`, extension `0x5F`. It makes the read-only F186 query only after a
native gateway reply. A receive prefilter discards the unrelated extensions
`0x0F` and `0x6D` before ISO-TP sees the shared response ID.

Extensions `0x0F` and `0x6D` on the same arbitration IDs are other logical
nodes. A reply proves the node-`5F` gateway route, not EPS liveness. F186 is
session state, not gateway firmware identity.

Every ordinary exit, transport error, and handled interrupt from the gateway
block attempts ELM327 parameter `1` restoration three times, verifies safety
mode/parameter `3/1` and disabled controls through Panda health, and then
requires the final Brake `22 10 2F` positive control. Host power loss and
`SIGKILL` cannot be caught, and USB loss or repeated board-control failure can
defeat cleanup; after any such event, manually restore parameter `1` before
another diagnostic action.

If that final Brake read fails, stop and restore the known route before any
other work. Do not translate a gateway reply into hand-built `27`, `28`, or
`31` traffic. The exact CUW package selects the gateway family, authorization,
routines, result checks, periodic messages, and cleanup behavior.

## Stage 1 interpretation

| Result | Next action |
|---|---|
| No Brake reply | Stop and repair the test route; no EPS conclusion. |
| Brake bit 74 clear and/or passive EPS-origin traffic exists | Preserve traffic and reconcile routing before calling the rack silent. |
| Brake bit 74 set; both EPS listeners silent | Proceed to official GTS+ discovery and exact-package lookup. |
| Gateway node `5F` silent through the explicit OBD route | Preserve this as a gateway-route result; use official GTS+ CAN Bus Check rather than guessing another gateway family. |
| Primary EPS application reply | Stop raw probing; classify identity/DTCs/supply DIDs, then use the validated application-to-boot restore path. |
| Primary exact-boot reply | Stop raw probing; use only the hash-bound direct-boot restore controller. |
| Correlated NRC `0x78` or partial ISO-TP followed by timeout | Target activity was observed but did not complete. Stop; the tool does not misclassify this as silence or unlock a later endpoint. |
| Any valid secondary `0x7A8` reply | Preserve it. The primary route was already tested once; continue to OEM gateway/package discovery because the secondary endpoint has no programming handoff. |

If the application answers, preserve DTC status before any clear and read the
exact power/history DIDs useful to the incident: `1034`, `1038`, `1039`,
`1061`, `1062`, `1064`, `1065`, `1067`, `1068`, `11B1`, `11B7`, `11B8`,
`11BC`, `11BE`, `11C3`, `11C4`, and `11C8`. Their labels are available through
`tools/gts did EMPS_P5 DID --json`. Do not turn family-only EPS DTC names into
exact incident facts without an actual response.

If both listeners remain silent, the network capture alone cannot distinguish
an unpowered/transceiver-isolated EPS from a powered application stopped before
DCM main. Pair that result with GTS snapshots of Power Source Control `1005`
and `1003`, then Central Gateway `1001` and Power Distribution Box `5011` where
available. Those values bound logical OFF/ACC/IGP/relay/request state; they do
not prove removal or restoration of EPS +B.

## Stage 2 — official GTS+ and TIS discovery

The installed current catalog supplies no registered peer-ECU wake or power
shortcut. Exact Camry categories 405 EMPS, 475 Power Distribution Box, 454
Power Source Control, and 443 Central Gateway each have zero Active Tests and
zero utilities. Main Body has 147 Active Tests and Entry & Start has 10, but a
case-insensitive scan of every label finds no EPS/power-steering supply,
ignition/IGP/IGR relay, ECU wake/sleep, or ECU reset control. Their superficially
similar power entries are limited to power-window permission, lighting/wiper
relays, tuners, and seat/door sensors. This is an installed-catalog absence, not
proof against a VIN/server-delivered function.

Toyota's public replacement-ECU procedure explicitly lists 2025 Camry HV EMPS
as requiring configuration software and says GTS+ adds a `Configure` column to
Health Check. Procedure A is the CUW reprogramming path. The published UI also
shows an EMPS `Restoration` row whose current calibration is `-`, demonstrating
that the product has a restoration-shaped workflow rather than only a
current-CID update workflow.^1

That evidence is not enough to claim support for this case. The bulletin is for
2025 vehicles and begins after ECU replacement; the incident vehicle is a 2026
Camry with its original, corrupted ECU. A factory blank replacement can still
be diagnostically responsive. The recovered host search normally obtains
`ecuAssyNo` and `baseSwNo` from target reads `22 01 05` and `22 F1 81`; a fully
silent installed EPS cannot supply them. Current VIN/TIS behavior therefore
decides whether GTS+ exposes an applicable restoration route.

### Read-only official capture

Use current registered GTS+ online and a supported VIM/J2534 interface. Toyota
requires a Professional Diagnostic TIS subscription for Techstream and ECU
calibrations; the current public price is $80 for two days.^2 Toyota separately
states that recalibration requires a validated J2534 interface, Professional
TIS, and CUW, and warns that an interrupted reflash can permanently damage a
controller.^3

No new interface purchase is needed for the read-only discovery pass: the
already-present XHorse Mini-VCI has completed local enumeration, firmware
bootstrap, and raw-CAN channel initialization. It has not yet been validated on
this vehicle bus and is not Toyota's validated reprogramming hardware. Use it,
if GTS+ accepts its registered provider, only for Health Check/CAN Bus Check and
package selection at this stage. Enumeration alone does not satisfy the Stage 3
reprogramming gate. Toyota's April 2026 Techstream Lite FAQ says other J2534
devices will *likely* work, but Toyota validates and recommends only the
Mongoose-Plus/MongoosePro family for diagnostic functions; other approved
devices are described as reprogramming-only.^11 The Mini-VCI attempt is
therefore a no-purchase discovery experiment, not a supported-interface claim.

Perform:

1. Connect by the exact VIN and correct vehicle options.
2. Run a full Health Check and save the native `.TSE` session plus screenshots.
3. Run live CAN Bus Check and save the topology/result.
4. Preserve the EMPS row even if it is “not responding”: detected state,
   current CID, `Calibration Update`, `Configure`, and `ECU Security Key`.
5. Preserve Brake/EPB DID `102F`, Brake `U0131-87` status/detail/freeze frame,
   and any live-identified central-gateway or power-supply participant.
6. If their current Data Lists are supported, record Central Gateway DID `1001`
   (+B/IGP/IGR/ACC), Power Source Control DIDs `1003`, `1005`, and `2001`, and
   Power Distribution Box DID `5011`. These are supply/routing observations,
   not EPS wake or reset controls; leave them to GTS+ rather than extending the
   raw Panda allowlist.
7. Do not clear codes, run an Active Test, run Initial Setting, or write a key.

### Record the OEM attempt independently from the EPS-side network

Do not rely only on the GTS+ progress bar or error text to decide how far the
operation reached. The installed Comma Panda can remain on the normal harness
route as a CAN-transmit-disabled witness while GTS+ owns the separate Mini-VCI at
the OBD connector. This avoids sharing one J2534 device and reveals whether an
OEM request actually reached target-side `0x7A1` and whether the EPS returned
anything on `0x7A9`. It does **not** directly witness the Mini-VCI-to-gateway
OBD segment: `NOOUTPUT` selects Panda's normal harness route, while node `0x5F`
was separately proved only through the OBD mux. Any `0x750/0x758` node-`5F`-
shaped frame seen here is incidental until a mirror/forward path is proved.

In a second terminal, review the hardware-free plan:

```sh
tools/toyota target run camry capture/f33-eps-gts-passive-capture -- \
  --duration-seconds 900
```

Then, before starting Health Check or the CUW preparation screen, run:

```sh
PYTHONPATH=/Users/kai/dev/inspect/repos/toyota-diagnostics/.venv/lib/python3.12/site-packages \
  tools/toyota target run camry capture/f33-eps-gts-passive-capture -- \
  --execute --duration-seconds 900 \
  --confirm-stationary \
  --confirm-ignition-on-ready-off \
  --confirm-stable-12v-support \
  --confirm-openpilot-stopped \
  --confirm-gts-separate-vci \
  --arm PASSIVE_F33_GTS_WITNESS
```

The witness sets and verifies Panda safety `NOOUTPUT` immediately after the
USB client opens and again at the capture boundary; that safety mode selects
the normal harness CAN routing. It records physical Panda buses 0 through 2
and makes **zero CAN data-frame submissions**—including no ISO-TP flow control.
`NOOUTPUT` remains electrically ACK-capable; this is a data-frame-transmit-
disabled witness, not a claim of listen-only electrical behavior. Panda client
initialization still resets its host communications and reapplies local CAN-
controller settings over USB. It explicitly pins all three controllers to the
exact installation's 500-kbit/s nominal, 2-Mbit/s ISO CAN-FD data timing so a
prior direct client's persistent data-rate/non-ISO state cannot manufacture
silence. The tool clears the complete board RX queue at
the evidence boundary and explicitly leaves/verifies `SILENT` on exit. GTS+/CUW
remains the only diagnostic client. Do not run the active Stage-1 triage command
at the same time. The capture retains every frame decoded by Panda in `can.bin`,
indexes diagnostic-range frames
in `diagnostic.ndjson`, and writes a finite `summary.json` below
`build/out/camry-f33-gts-passive-<timestamp>/`.

Classify the result offline:

```sh
tools/toyota target run camry analysis/f33-eps-gts-passive-capture -- \
  /absolute/path/to/camry-f33-gts-passive-<timestamp>
```

The classifier derives its verdict from `can.bin`, verifies the NDJSON index
against those bytes, and accepts EPS evidence only on the current Panda bus 0.
It distinguishes: no target-side request; a primary `0x7A1` request with no
`0x7A9`; any EPS-origin response; and an ordered same-bus `10 02 -> 50 02`
exchange within the conservative three-second evidence-correlation window. A
lone, earlier, stale-bus, or later `50 02` remains only recorded traffic. It
also invalidates absence claims on Panda RX loss, bus-off, controller reset,
capture/index mismatch, or unsafe-state drift. Even a valid ordered positive
proves executor liveness, not a completed repair or package compatibility.

The supported Software-as-a-Part UI does not expose a manual assembly/base-
software tuple entry. Standard TIS **Diagnostics -> Calibrations** is a separate
vehicle/current-CAL-ID and bulletin search, not a documented blank-ECU
restoration lookup.^9 It can still be searched without transmitting to the car,
but an empty result there does not decide whether Software as a Part has a
VIN-selected package. The exact saved preincident tuple to preserve for package
review or dealer/Toyota technical escalation is:

| Search input | Saved exact value |
|---|---|
| ECU assembly / DID 0105 backing object | `8965033K90` |
| Base software 1 | `8965F3307000` |
| Base software 2 | `8A3113303100` |

These are explicitly historical, identity-bound values from the saved image and
preincident F181—not a fabricated current live response, a supported manual
server request, or enough information to infer a CUW filename. Preserve any TIS
current-CID search result, including a no-result page. An anonymous URL redirect
or a search hit for only one identifier is not package compatibility. The
firmware source chain for this tuple is preserved in
[`camry-f33-calibration-lookup-from-saved-image.md`](camry-f33-calibration-lookup-from-saved-image.md).

The separate Security Key bulletin says this feature commissions certain
replacement ECUs so they can communicate on the vehicle network and exposes a
Health Check indicator of `Necessary`.^4 It is not a recovery key for corrupted
CodeFlash and must not be run unless GTS+ identifies the exact requirement.

### Software-as-a-Part / Restoration acquisition

If the exact VIN offers `Configure = Yes`, `Software as a Part (Blank ECU)`, or
an EMPS `Restoration` row:

1. Record the entire selected row and every current/new calibration ID.
2. Use `Output` to create the server-selected local list
   `L_<VIN>_<yyyyMMddHHmmss>.txt` under
   `C:\Users\Public\Documents\GTSPlus\SoftwareAsaPart`.
3. Preserve that list. It exists only after server selection has populated the
   candidates; `Output` does not derive filenames from the saved tuple.
4. Continue through the authenticated download/login step and download the
   selected package.
5. Stop on the screen where the required calibration has been downloaded.
6. Do **not** press the final `Next` that the Toyota procedure labels “begin
   reprogramming the ECU.”^1

An older official GTS+ known-bug notice calls this function “Blank ECU
Calibration Download” and confirms that identifying and downloading a needed
calibration file is a first-class Software-as-a-Part operation.^5 Another
official Techstream known-bug record confirms that Software as a Part is part of
Health Check.^6 Neither source says that the function can identify this exact
silent original ECU.

There is no exact F33 package in the retained local CUW corpus:

```sh
tools/gts cuw 8965F3307000 --json
tools/gts cuw 8A3113303100 --json
```

Both currently return an empty list. The local Camry `T-0051-26` package is
Engine/MG at diagnostic ID `0724`; the local `07A1` packages are other Toyota
EPS calibrations. None may be substituted.

If silent `0x7A1` prevents Health Check from offering `Configure = Yes`, the
supported UI has not produced a package. Give the exact VIN and retained tuple
above to a Toyota dealer/technical channel and ask specifically for the
server-generated EMPS Software-as-a-Part output list or package. Do not hand-
construct the legacy server XML or a package URL. Toyota's public TIS customer-
support contact explicitly does not provide vehicle repair or technical
assistance; it is not a substitute for that escalation.^10

### Exact-package acceptance gate

Inspect any downloaded package without running it:

```sh
sha256sum /absolute/path/to/downloaded-package.cuw
tools/gts cuw /absolute/path/to/downloaded-package.cuw --validate --verbose --json
```

Retain the raw package and SHA-256 before extraction. At minimum, reconcile:

| Field | Required interpretation |
|---|---|
| Vehicle/model/VIN selection | Current TIS returned it for this exact 2026 Camry configuration. |
| `Node01/DiagID` | EPS physical diagnostic ID `07A1`. |
| `ContactType` | Must match the actual package-selected writer; likely `P5-Unified`, never assumed from a different CUW. |
| Gateway list | If present, reconcile exact `07505F` rather than borrowing `0751`, `0786`, `0F`, or `6D`. |
| Target/current CIDs | Reconcile `8965F3307000` and `8A3113303100`, or document the explicit blank/restoration rule that legitimately omits them. |
| New CIDs and CPU/image count | Preserve exactly; do not infer a one-CPU image from a two-record F181. |
| `IsBlankECU`, restore/update flags, timeout fields | Treat as host/package controls, not proof of an ECU-side recovery mode. |
| CID-getter exception fields | Preserve `FlagToSupportGetCID`, `RequestCANIDAllowingTimeout`, and any blank-target rule. The retained P5 rows leave the first two empty; do not assume the absent exact package does. |
| `ChargeLocalBusEcuReprogrammingFlow` | Preserve its controller diagnostic ID, timing, and enable value. It is the only package-selected flow recovered before ordinary EPS CID discovery; its presence and EPS-power semantics are unproved here. |

If any identity is for another model, ECU, diagnostic ID, or gateway family,
stop. Do not edit a descriptor to make it pass.

## Stage 3 — the only justified state-changing network attempt

Run the Toyota CUW job only if all of the following are true:

- current GTS+/TIS selected the package for the exact VIN;
- the offline package inspection passes;
- the interface and power supply satisfy the applicable Toyota procedure;
- the complete raw J2534 log and GTS session can be retained;
- there is a clear abort/escalation plan if the frontend cannot admit the
  silent ECU; and
- no custom sender is racing GTS+/CUW.

The purpose of this one OEM-owned attempt is not blind reflashing. First
determine whether the exact package can admit the target at all. In the stock
Unified pipeline, the ordinary CID getter's first target request is
`7A1: 22 F1 81`, and it requires `7A9: 62 F1 81 ...`. Its fallback still sends
target routines/services and cannot admit a totally silent ECU; native common
eligibility rejects an empty received-CID vector before a later blank-target
flag can help. The only recovered pre-CID exception is an optional, package-
selected `ChargeLocalBusEcuReprogrammingFlow` against a package-named
controller. All 26 retained CUWs leave that flow absent/zero, and neither its
presence nor EPS power-control semantics can be projected onto the missing F33
package.

Only after CID/admission does `StartPrepareWrite` own the manufacturer gateway
preparation. In the current P5 branch, the preparer's optional EPS F181 occurs
*after* initial gateway work; a caught timeout there does not bypass the later
mandatory target exchange `7A1: 10 02 -> 7A9: 50 02`. Gateway replies never
synthesize `0x7A9` or flash the EPS by proxy. Preserve these distinct outcomes:

| Outcome | Meaning |
|---|---|
| Frontend stops at EPS F181/CID discovery | The ordinary supported pipeline did not admit this silent original ECU and did not reach `StartPrepareWrite`. |
| Exact package runs a pre-CID local-bus flow but EPS remains silent | Preserve the package-selected controller exchange; it did not supply a target executor. Do not generalize its power semantics. |
| `StartPrepareWrite` is reached, gateway work completes, but mandatory EPS `10 02` receives no `50 02` | Prepared routing did not create an EPS executor; the gateway cannot flash the target by proxy. |
| EPS supplies a native reply | Stop and identify the exact response/application-versus-boot state before erase or programming. This is the positive recovery branch. |

Depending on the missing package, traffic before CID could include the optional
local-bus flow; otherwise ordinary target F181 is first. State-changing gateway
authorization, RoutineControl, communication masking, and periodic fanout are
downstream of admission. Their exact branch cannot be named without the exact
package. In the recovered current P5-shaped branch, gateway routines `1011`
and `1012` require their result value, not merely a `71` start response. This
incomplete package selection, abort, and cleanup knowledge is why those frames
must not be recreated in the raw CLI.

Toyota's general GTS+ flash bulletin recommends IG ON/READY OFF for hybrids,
accessories off, a connected battery support device, and battery voltage above
12 V.^7 That bulletin's published applicability does not include Camry HV, so
it is supporting power-practice evidence only; the exact VIN's current TIS
procedure controls.

## Conditional network restoration after an EPS response

An EPS-origin reply changes the situation materially:

- **Expected application response:** the exact target already accepted the
  application-to-boot transition, boot SecurityAccess, authenticated
  `FEBF0000/0x1000` RAM download, and callback execution before the incident.
- **Exact boot-compatible response:** the existing restore controller supports
  a direct-boot start guarded by the exact boot F181.
- **Secondary application response only:** do not request a handoff there. Its
  SID-10 table lacks programming session `0x02`; use the observation to justify
  one primary retry and exact-VIN OEM package/admission discovery.

The retained rollback is not a guessed stock image. It applies the archived
stage-7 inverse to the complete incident reconstruction, restores the damaged
call and its CRC fixup, and reproduces the prior stage-6 image byte-for-byte.
Its evidence and boundaries are in
[`camry-f33-gateway-recovery-lifecycle.md`](camry-f33-gateway-recovery-lifecycle.md).
The executable controller is
[`exploit/patcher/restore.py`](../../exploit/patcher/restore.py), and its normal
operator wrapper is the incident package's `hook-remove` action.

Do not launch that writer merely because Brake or the gateway answers. Before
execution, require the exact EPS identity classification, current route, exact
boot placeholder, archived restore artifact/hash validation, stable power, and
a fresh run directory. After a reported restore, a real power cycle and renewed
application F181/native EPS traffic are separate completion requirements.

## Exhausted or rejected network candidates

| Candidate | Result |
|---|---|
| More primary `7A1` polling or broad bus sweeps | No new condition; exact route and two postincident timeouts already exist. |
| Pre-sent request/session race | Exact RX rules can queue `0x7A1`, `0x777`, or `0x7A0`; a precisely timed single frame can even complete ISO-TP reception and enqueue DCM protocol state. SID inspection/dispatch still occurs only in DCM main, after the first-tick path that enters the malformed `0x7A272` transfer. The interrupt-time communication helper calls only the receive/transport workers and never DCM or the boot handoff, so interrupt interleaving or flooding cannot advance the queued request into a service. |
| CAN wake / network-management catch at ignition | The CRC-valid image takes the application branch. Stock boot CAN initializes only on validation failure; the application has no pre-fault DCM service window and contains no HALT/SNOOZE instruction to resume through CAN. After the bad fetch, the exception path records error state and spins without `FERET` while further interrupts are blocked. Ordinary OFF/ACC/IG/READY reset classes therefore do not select the loader. |
| Deliberate bus-off, CAN-error injection, or RX flooding | Exact CAN1 uses `BOM=01`, which auto-halts the channel on bus-off; its bus-off/error recovery interrupts are disabled, and the software recovery path is reached only after the incident fault. This worsens reachability and does not select boot. |
| Functional `0x777` probing | Broad recipient scope and no independent executor; not justified while physical routes are known. |
| XCP | Exact application dispatch is blocked by fixed CodeFlash byte `0x30D68 = 0x5A`; no boot XCP service. |
| Boot DID/memory alternatives | Exact boot SIDs `23`, `2C`, `14`, `19`, `2F`, `AB`, `BA`, and `BB` resolve to the unsupported-service path. |
| ECUReset, ordinary cabin power cycle, or watchdog | Re-enters the still-valid malformed application image; no repaired byte source or reset-class boot selector was recovered. |
| Peer ECU Active Test / power control | EMPS, Central Gateway, Power Source Control, and Power Distribution Box expose no such controls. Entry/Start and Main Body do have body/lighting/lock/load tests, but exhaustive candidate review found no EPS supply, IGP/IGR/ACC main-supply, network-routing, wake/sleep, or ECU-reset operation. No cataloged peer control power-cycles or programs EPS by proxy. |
| EPS Initial Setting / Assist Map Clear | Scheduled application/DataFlash work; cannot repair the malformed CodeFlash path and may discard useful state. |
| Telematics/OTA | Recovered operations target DCM/NAD or a different Phase-6 writer family, not the P5 F33 EPS executor. |
| Hand-built gateway prep | Package/family selection, authorization, success checks, periodic traffic, and P5 abort normalization are incomplete; use exact OEM CUW only. |
| Other local `07A1` CUW | Wrong calibration/vehicle identity; shared address and protocol family are insufficient. |
| Security Key writing | Replacement-ECU commissioning, not CodeFlash recovery. |
| Historical Panda Windows J2534 driver | Removed upstream in January 2024.^12 The last source forces `SAFETY_ALLOUTPUT`, hardcodes ISO-15765 to Panda CAN1/bus 0, and has no current ELM327 safety parameter or OBD-mux selection. Unmodified, it cannot reach this installation's node-`5F` OBD route and is not an acceptable GTS/CUW interface. Do not install or register it for this attempt. |

The public NHTSA manufacturer-communications corpus was searched for 2025–2026
Camry Hybrid EPS, software, recovery, OTA, and failed-reflash material. It
returned the replacement configuration and Security Key bulletins cited here,
but no public exact-ID failed-flash or silent-EPS recovery bulletin. NHTSA
publishes manufacturer communications as a distinct dataset.^8 This is a
bounded public-dataset absence as of September 12, 2026, not evidence that the
authenticated current TIS service has no VIN-specific package or instruction.

## Evidence packet to retain

Return one packet containing:

- complete output of every command actually reached in the finite
  Brake/primary-EPS/secondary-EPS/gateway sequence;
- the complete passive GTS witness directory (`can.bin`,
  `diagnostic.ndjson`, `summary.json`) and its offline classification;
- ignition/READY state, battery voltage, interface owner, Panda safety/mux
  state, and exact timestamps;
- GTS+ `.TSE`, Health Check and CAN Bus Check screenshots;
- Brake DID `102F` raw bytes and U0131-87 status/detail/freeze frame;
- complete EMPS row including Update, Configure, Security Key, current CID, and
  any error text;
- Software-as-a-Part `Output` list and downloaded package, if offered;
- package SHA-256 and `tools/gts cuw ... --json` output; and
- raw J2534 log if CUW is later authorized to launch.

Do not include a public VIN, TIS credential, security token, or unredacted
account identifier in the repository.

## Sources

1. Toyota Motor Sales, USA. “[Replacement ECU Software Configure Process, T-SB-0015-25](https://static.nhtsa.gov/odi/tsbs/2025/MC-11014209-0001.pdf).” January 29, 2025, pp. 1–14.
2. Toyota Motor Sales, USA. “[The TIS Library — Subscription Options](https://techinfo.toyota.com/techInfoPortal/appmanager/t3/ti?_nfpb=true&_pageLabel=ti_whats_tis).” Accessed September 12, 2026.
3. Toyota Motor Sales, USA. “[J2534 Reprogramming](https://techinfo.toyota.com/techInfoPortal/appmanager/t3/ti?_nfpb=true&_pageLabel=ti_j2534_device).” Accessed September 12, 2026.
4. Toyota Motor Sales, USA. “[ECU Security Key Writing, T-SB-0011-25](https://static.nhtsa.gov/odi/tsbs/2025/MC-11014190-0001.pdf).” January 23, 2025, pp. 1–7.
5. Toyota Motor Sales, USA. “[Global Techstream Plus Known Bugs, Version 2023.04.003.02](https://techinfo.toyota.com/techInfoPortal/staticcontent/en/techinfo/html/prelogin/docs/GTS%2B_Known_Bugs_V2023.04.003.02_Techinfo.pdf).” Updated November 29, 2023, p. 20.
6. Toyota Motor Sales, USA. “[Techstream Known Bugs, Version 18.00.008](https://techinfo.toyota.com/techInfoPortal/staticcontent/en/techinfo/html/prelogin/tsrss/ts_known_bugs.html).” Updated March 15, 2023.
7. Toyota Motor Sales, USA. “[GTS+ ECU Flash Reprogramming With Security Signature, T-SB-0021-25](https://static.nhtsa.gov/odi/tsbs/2025/MC-11015496-0001.pdf).” February 10, 2025.
8. National Highway Traffic Safety Administration. “[NHTSA Datasets and APIs — Manufacturer Communications](https://www.nhtsa.gov/nhtsa-datasets-and-apis).” Accessed September 12, 2026.
9. Toyota Motor Sales, USA. “[Accessing Calibration File Information in TIS](https://www.techinfo.toyota.com/techInfoPortal/staticcontent/en/techinfo/html/prelogin/docs/accesstocalfiles.pdf).” November 17, 2009.
10. Toyota Motor Sales, USA. “[TIS Contact Us](https://techinfo.toyota.com/techInfoPortal/appmanager/t3/ti?_nfpb=true&_pageLabel=ti_contact_us).” Accessed September 12, 2026.
11. Toyota Motor Sales, USA. “[Techinfo Techstream Lite AM FAQ v4.0](https://one.tis.toyota.com/techInfoPortal/staticcontent/en/techinfo/html/prelogin/docs/tslfaqtinfo.pdf).” Updated April 28, 2026, pp. 8–9.
12. comma.ai. “[Remove Windows Driver, panda commit `3ef9c3f`](https://github.com/commaai/panda/commit/3ef9c3f9efbbdb6d69467ffddc2d2607b103605f).” January 13, 2024. The removed `PandaJ2534Device.cpp` and `J2534Connection_ISO15765.cpp` are the source for the safety-mode and fixed-port observations.

Repository evidence: exact target firmware and generated decompiler corpus;
[`camry-f33-network-gateway-evaluation.md`](camry-f33-network-gateway-evaluation.md),
[`camry-f33-recovery-exception-followup.md`](camry-f33-recovery-exception-followup.md),
[`camry-f33-gateway-recovery-lifecycle.md`](camry-f33-gateway-recovery-lifecycle.md),
[`camry-f33-calibration-lookup-from-saved-image.md`](camry-f33-calibration-lookup-from-saved-image.md),
[`application.md`](../diagnostics/application.md), and the retained vehicle
records under `targets/camry-2026/`.
