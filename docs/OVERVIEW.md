# Firmware / project overview

This is the human-scale current-state summary for the Sienna EPS analysis. It
is intentionally shorter than the canonical subsystem reports and status
ledgers. Follow the links when you need evidence, exact addresses, or caveats.

## Target and evidence boundary

Primary analyzed calibration:

- **Toyota/Denso EPS:** `8965B4512000`
- **MCU:** Renesas RH850/P1M-E `R7F701381`
- **CodeFlash:** 1 MiB at `0x00000000..0x000FFFFF`
- **DataFlash:** 32 KiB at `0xFF200000..0xFF207FFF`
- **Application:** base `0x20000`, entry `0x20880`

The committed CodeFlash and DataFlash files in `firmware/` are the source
inputs. The current corrected project contains **6,376 structurally discovered
functions / 183,240 decoded instructions**. There are 6,376 structurally discovered functions, of which 6,257 remain unreviewed and 32 currently carry a semantic evidence grade. Structural recovery is therefore much broader than
semantic understanding; exact coverage denominators are in
[status/ANALYSIS_STATUS.md](status/ANALYSIS_STATUS.md).

Unless explicitly stated otherwise, firmware-static findings apply only to
`8965B4512000`. Related Corolla/Sienna/F3/F4/RAV4 observations are tracked under
[variants/](variants/README.md) and do not automatically transfer.

## What the firmware does

### Boot / application trust

The bootloader validates the application using CRC descriptors plus fixed
validity markers, **not an OEM signature**. The reset-to-application chain,
retry behavior, flash lifecycle, and application handoff are recovered.

The bootloader also exposes the authenticated download/RAM-execution machinery
used by Toyota programming flows. Both bootloader AES secrets and the payload
format are recovered, and the authenticated 4 KiB RAM-exec bootstrap is fully
modeled locally.

Canonical reports:
[architecture/boot-validity-and-flash-lifecycle.md](architecture/boot-validity-and-flash-lifecycle.md) ·
[security/bootloader-payload-gate.md](security/bootloader-payload-gate.md).

### Diagnostics

Bootloader and application use separate UDS stacks. The application exposes a
large configured surface including `10/11/14/19/22/23/27/28/2E/31/3E/85/AB/BA`;
`34/36/37` are present at the object-table level but do not provide an ordinary
application download path.

Important application results include:

- functional SecurityAccess level 2 (`27 03/04`) with a recovered secret;
- no configured Dcm SecurityAccess policy entries for the application service
  and DID tables in this calibration;
- SecurityAccess-free SID `0x23` ReadMemoryByAddress disclosure over large
  LocalRAM/DataFlash allow-ranges;
- persistent proprietary BA authorization state after a legitimate SA2 enable;
- a 19-entry RoutineControl surface with several persistent/state-changing
  operations;
- a verified 48-DID stale-response disclosure family;
- a closed RDBI producer-overrun question: all 196 unique configured producers
  are now audited and none writes beyond its declared length;
- RMBA address/length arithmetic closed against the targeted overflow/wrap/
  TOCTOU escape classes, without reducing its disclosure impact.

Canonical reports:
[diagnostics/application.md](diagnostics/application.md) ·
[security/application-security-access.md](security/application-security-access.md) ·
[security/memory-safety-audit.md](security/memory-safety-audit.md).

## SecOC / ICU-S state

Six application receive profiles use SecOC verification through **ICU-S slot
4**. Their roles are no longer treated as one generic protected bucket:

- `0x00F` — synchronization;
- `0x2E4` — steering torque/request command mode;
- `0x131` — LTA angle/request command mode;
- `0x132` — bounded snapshot-only/dead-end role in this calibration;
- `0x090` — protected rear-wheel-speed / steering-angle-speed family;
- `0x0D7` — protected vehicle-speed / validity family.

Command 7 is the recovered MAC-verification primitive. Command 5 is the paired
MAC-generation path. Stock application code can activate its command-5 crypto
test with RID `0x100F`; the generated 16-byte value is normally compared
locally rather than used by a production SecOC sender. Whether **live slot 4**
permits command 5 is still a hardware question.

The application also has **two command-8 authenticated key-update clients**:

1. diagnostic RID `0x1010`, carrying a 64-byte M1/M2/M3-shaped request and
   returning a 48-byte M4/M5-shaped result;
2. RID `0x100E` + ordinary CAN `0x13..0x1A`, which independently stabilizes
   eight 8-byte chunks and forms another 64-byte command-8 envelope.

The shared command-8 completion callback has a verified attribution flaw:
completion is routed according to the diagnostic-active byte at completion
time, not remembered submitter identity. A bank-0 completion can therefore make
RID `0x1010` report a false terminal success with its own untouched zero result
bank. **This does not bypass SHE authentication**; ICU-S still decides whether
the supplied M1/M2/M3 package is valid.

The live slot-4 key is still not known from this image. The embedded apparent
`FF*16` KAT is compiled out, and object-15 state in this dump does not establish
the live ICU-S slot contents.

Start here:
[security/secoc/README.md](security/secoc/README.md).

## XCP / calibration surface

The application contains an XCP-like command channel on CAN `0x7F7/0x7F8`.
Static analysis recovers:

- unauthenticated reads;
- DAQ configuration and event-driven observation;
- a direct 32 KiB LocalRAM write window via DOWNLOAD / MODIFY_BITS;
- hardware MPU permissions that make that RAM supervisor-executable.

No recovered callback, return-address, vector, DMA, or other control-transfer
consumer currently turns that write window into a demonstrated execution
primitive. Physical vehicle/bench reachability of `0x7F7/0x7F8` is also still
unobserved. A CONNECT-only reachability probe and read-only DAQ tooling are ready
under `exploit/followups/`.

Canonical report:
[communications/xcp-command-dispatch.md](communications/xcp-command-dispatch.md).

## Steering / motor-control boundary

Protected `0x2E4` torque/request state and protected `0x131` LTA angle/request
state are both recovered through their application conditioning chains and
converge in a common late command-mode region. We also recovered the separate
TAUJ0 CH0 current-control/PWM chain from ADC/DMAC phase samples through d/q-like
feedback and TSG3 compare writes.

The static analysis **does not recover a direct transfer** from the authenticated
command state into the identified d/q reference cells. That negative is much
stronger than an initial xref search—it includes producer cones, RAM-bank
censuses, pointer scans, generic-copy audits, and both command modes—but it is
still not a physical-independence proof. A live actuation discriminator remains
the right next step if the XCP observer route is reachable.

Canonical report:
[architecture/control-partition.md](architecture/control-partition.md).

## Exploit engineering status

The repo now separates a firmware finding from a runnable experiment. The
`exploit/` tree contains bounded tooling for:

- authenticated RAM-exec and read-only CodeFlash acquisition;
- manifest-driven persistent Gate-2 patching / restore construction;
- the MAC28-only causal bypass trial;
- the application command-5 selector-4 experiment;
- RMBA/RDBI/CommunicationControl/SecOC freshness follow-ups;
- XCP CONNECT/read/DAQ observation.

`exploit/findings_coverage.json` dispositions every canonical finding so new
analysis cannot silently fail to reach the exploit-engineering layer.

See [../exploit/README.md](../exploit/README.md).

## What is actually blocking progress

Most high-value unknowns are no longer “decompile another random function.” The
current blockers are:

1. **Live slot-4 command-5 permission and timing.** If generation is allowed,
   an application-resident signing proxy becomes practical without extracting
   the key.
2. **XCP physical reachability.** A positive result gives a powerful read-only
   dynamic observer and exposes the existing unauthenticated write surface.
3. **Gate-2 causal hardware proof.** The host harness is ready; the remaining
   result is behavioral on matching hardware.
4. **Another CodeFlash calibration.** A real F3/F4/Corolla/`4514000` image is
   the fastest way to test which structural/exploit findings transfer.
5. **Live command→actuation discriminator.** Static work has reached diminishing
   returns; dynamic observation is now more informative.

The short actionable queue, including what *not* to spend time on, is
[status/PRIORITIES.md](status/PRIORITIES.md). The exhaustive unresolved ledger is
[status/OPEN_QUESTIONS.md](status/OPEN_QUESTIONS.md).

## External / variant evidence

Toyota Techstream, Renesas RFP, community tooling, and related-vehicle artifacts
have been analyzed as **corroboration and acquisition context**, not silently
promoted to Sienna firmware truth. The strongest external work includes:

- Techstream diagnostic/DDB vocabulary and MACKey registration analysis;
- Renesas RV40F host protocol recovery;
- community RAM-exec, DataFlash, patching, and SecOC-oracle workflows;
- Corolla/RAV4/Sienna-related field observations.

See [tooling/README.md](tooling/README.md), [variants/README.md](variants/README.md),
and [../community/README.md](../community/README.md).

## How to navigate from here

- Need a **claim ID / confidence** → [status/FINDINGS.md](status/FINDINGS.md)
- Need a **current task** → [status/PRIORITIES.md](status/PRIORITIES.md)
- Need an **unresolved detail** → [status/OPEN_QUESTIONS.md](status/OPEN_QUESTIONS.md)
- Need a **past investigation journal** → [history/](history/README.md)
- Need **exact machine evidence** → `data/`, `tests/`, firmware bytes
- Need **Ghidra mechanics** → [WORKFLOW.md](WORKFLOW.md)
