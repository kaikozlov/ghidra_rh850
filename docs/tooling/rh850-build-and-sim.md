# RH850 build and execution testing

`tools/rh850` supports one pinned GNU `v850-elf` toolchain: GCC 16.2.0,
binutils 2.46.1, and GDB 18.1 with repository-local simulator fixes.
Builds and instruction simulation use the same image and `v850e3v5`
architecture. There is no GCC 13 compatibility path or compiler-profile selection.

Use the repository wrapper rather than assembling ad-hoc Docker commands:

```bash
tools/rh850 doctor
tools/rh850 selftest
```

`selftest` builds a full 1 MiB low-address CodeFlash section with executable
code at `0x0008F800`, plus a freestanding C function and assembly harness in
high RAM. It checks that all CodeFlash blocks remain distinct, crosses between
CodeFlash and RAM with positive and negative format-VI branches, executes the C
function, and verifies deterministic RAM results. The C function computes from
a volatile local rather than a folded constant. This exercises C compilation,
linking, full-image ELF loading, real low-address instruction fetch, far control
flow, and basic register/stack/memory execution together.

For a retained ELF, add the address ranges the program can touch and then give
ordinary GDB commands:

```bash
tools/rh850 sim build/out/example.elf \
  --memory-region 0xFEBE0000,0x20000 \
  -ex 'break rh850_sim_stop' \
  -ex run \
  -ex 'info registers'
```

## Specification-backed P1M-E machine

`tools/rh850 machine` uses Ghidra's modern `PcodeEmulator` and the vendored
RH850G3M SLEIGH language. It is separate from GNU `sim/v850`: the p-code
machine loads the exact registered CodeFlash/DataFlash identities, rejects
CodeFlash overlays, applies the SystemRDL memory/register model, and faults on
an unmapped or uninitialized read instead of supplying zero.

The canonical device source is `data/devices/p1me.rdl`.
`tools/rh850 machine model` compiles it into:

- `data/generated/p1me_machine.json`, consumed by the Ghidra machine;
- `data/p1m_sfr_labels.csv`, consumed by the Ghidra device-profile scripts;
- `data/p1me_product_memory.json`, consumed by product/memory checks.

All three projections and their code consumers are discoverable through
`tools/artifact`. The generated machine model separates public-manual regions
and registers from `target_derived` recovered register behavior. Its product
records identify `R7F701381` and `R7F701383` individually; the runtime checks
the selected target's exact MCU identity rather than treating “P1M-E” as one
undifferentiated part.

### Architecture

The machine has one owner for each layer:

1. `ghidra/ghidra_v850/data/languages/` defines RH850G3M instruction and
   system-register semantics. Synchronization opcodes share the processor
   language's ordering-boundary userop; the machine records `SYNCE`, `SYNCM`,
   `SYNCP`, and `SYNCI` separately from their decoded instruction mnemonics.
   MPU and interrupt system registers use the G3M selector map from
   R01US0123EJ0140.
2. `data/devices/p1me.rdl` defines the P1M-E address spaces, register widths,
   access policy, reset rules, evidence class, and peripheral trigger
   relationships. Generated JSON/CSV files are projections, not competing
   sources. Java dispatches generated trigger/reset metadata; it does not select
   TAUJ, RSCFD, FACI, or ICU-S behavior by register-name tables.
3. `data/analysis_targets.json` supplies exact MCU, processor language,
   CodeFlash identity, and optional DataFlash identity. It is not a capability
   whitelist.
4. A scenario supplies external state, a target-independent structural
   firmware-role selector, stop addresses, checks, and optional hash-bound RAM
   artifacts. `gpr_fill` states the general-register baseline once; `registers`
   contains only overrides and system-register state. `pre_reset_memory` exists
   only for exercising reset retention/clearing.
5. `RunP1MEMachine.java` resolves each role uniquely from the selected analyzed
   firmware, records the structural and exact-byte proof, composes the machine
   with `PcodeEmulator`, and enforces execute/read/write policy before each
   operation. One target session loads immutable images and model data once,
   then runs each scenario with fresh emulator state.
6. Reports embed the resolved run contract, explicit termination reason, first
   failing check data, fault provenance, and a bounded recent-PC window.

### Implementation plan and tracked status

The implementation extends Ghidra's `PcodeEmulator`; it does not add a QEMU TCG
target or a second RH850 decoder. This keeps instruction semantics in the
repository's existing SLEIGH language and makes exact registered addresses,
processor contexts, and project inventories directly reusable. GNU `sim/v850`
remains a separate execution engine for differential checks; it is not the
device-model runtime.

```mermaid
flowchart LR
  Target["analysis_targets.json<br/>exact image + MCU identity"] --> Resolver["unique firmware-role resolver"]
  Scenario["scenario-v2<br/>shape + state + checks"] --> Resolver
  RDL["p1me.rdl<br/>manual + recovered evidence layers"] --> Projection["generated machine JSON"]
  SLEIGH["RH850G3M SLEIGH<br/>CPU + system registers"] --> Emulator["PcodeEmulator"]
  Resolver --> Contract["resolved run contract<br/>shape + exact-byte proof"]
  Contract --> Emulator
  Projection --> Emulator
  Emulator --> Policy["memory / alignment / MPU policy"]
  Emulator --> Scheduler["metadata-driven device events"]
  Policy --> Report["termination + checks + bounded context"]
  Scheduler --> Report
```

|Workstream|Design and invariant|Tracked status|
|---|---|---|
|CPU execution|Use the vendored RH850G3M SLEIGH language; preserve distinct decoded synchronization mnemonics while sharing one ordering-boundary p-code operation.|Implemented for the exact paths and synthetic instruction corpus. The processor fixture covers arithmetic/flags, loads/stores, branches, calls/returns, `CAXI` compare-exchange, `DI`/`EI`, system-register selectors, trap/exception return, MPU registers, and synchronization decode. This is not a claim that every G3M opcode has an independent semantic test.|
|Memory subsystem|Load registered CodeFlash/DataFlash by exact hash; map LocalRAM, GlobalRAM, SFR, and alias regions from generated data; use the target language's little-endian byte order; enforce read/write/execute policy, initialized-state provenance, alignment, and per-register access widths before side effects.|Implemented. PE1/self LocalRAM aliases are kept coherent. Unknown MMIO, illegal widths, and uninitialized reads fault.|
|Reset behavior|Initialize processor reset registers from the G3M architectural reset state; apply generated P1M-E reset-source rules; restore or retain STAC controls according to reset source before deciding which RAM regions to clear.|Implemented for `none`, `power-on`, `system-1-pin`, `system-1-cvm`, `system-2`, and `application-1`. The reset matrix and STAC relationships come from the generated model rather than Java register-name branches.|
|Peripheral scheduler|Generated trigger metadata may enqueue deterministic events keyed by retired machine ticks. Events run in insertion order at a shared tick; the report records the dispatch tick. No wall-clock polling or host sleeps participate.|Implemented. RSCFD transmit completion and TAUJ start/stop transitions use the queue. Machine ticks are deterministic ordering units, not silicon cycle timing.|
|Interrupts|Model typed EIC registers, `PSW.ID` transitions, and exact firmware pending-bit acknowledge accesses without inventing interrupt delivery.|Bounded implementation. Priority arbitration and asynchronous peripheral exception entry/delivery remain unimplemented and MUST be added before a scenario can claim those paths.|
|TAUJ|Model start/stop state, channel enable state, prescaler/mode storage, and reload-to-counter transfer used by the exact initialization path.|Implemented for the retained path. Continuous decrement, underflow, and interrupt generation remain outside the current evidence boundary.|
|RSCFD|Model the recovered channel-1 transmit-buffer layout and transmit-request completion used by the exact writer.|Implemented for buffer 16. Receive FIFOs, arbitration, error states, and bus timing are not modeled.|
|FACI / CodeFlash|CodeFlash fetches execute from immutable registered image bytes. Scenario overlays and ordinary writes are rejected. Only the exact status-clear command has a modeled FACI transition.|Bounded implementation. Unsupported FACI commands fault before side effects; erase/program, protection, sequencer timing, and cache-coherency behavior remain unimplemented.|
|ICU-S|Expose only recovered registers and exact command-five/callback transitions. Treat supplied output words as scenario state, not generated cryptography.|Implemented within that recovered boundary. No provisioned-key or AES-CMAC silicon claim.|
|Integration|Expose model generation and batched execution through `tools/rh850 machine model` and `tools/rh850 machine run`; bind identity through the existing target registry; retain one JSON report per scenario under `build/out/`.|Implemented. No parallel capability manifest, target whitelist, or project lifecycle exists.|
|Verification|Discover target-owned scenario directories deterministically, run one Ghidra session per target, and require unique dynamic role resolution before exact-byte execution. Use synthetic processor semantics for instruction-level boundaries and GNU simulator runs only where an independent differential is useful.|Implemented as narrow gates. `tools/test rh850_machine` includes Camry and Crown exact bytes; `make verify-processor` owns the synthetic processor and project audits.|

Progress:

- [x] Select and integrate the Ghidra p-code execution framework.
- [x] Establish strict registered-image, memory-map, alias, and fault behavior.
- [x] Generate the device specification from SystemRDL and bind reset metadata.
- [x] Implement architectural processor reset state, STAC-controlled RAM reset,
  alignment, MMIO width, and MPU enforcement.
- [x] Add deterministic peripheral scheduling and the exact TAUJ, RSCFD, FACI,
  INTC-register, and recovered ICU-S paths required by retained scenarios.
- [x] Add exact-firmware and negative regression scenarios and CLI integration.
- [ ] Add interrupt arbitration/exception delivery only when an exact target path
  and manual-backed acceptance case require it.
- [ ] Add mutating FACI commands and CodeFlash coherency only with an exact
  programming path and byte-level postconditions.
- [ ] Extend peripherals and instruction tests incrementally from failing exact
  paths; never fill undocumented behavior with permissive stubs.

The functional model currently covers PE1/self LocalRAM aliasing,
STAC-controlled Application/System reset RAM rules, G3M alignment and MPU
overlap permissions, per-register MMIO access widths, TAUJ0 control state, EIC
register accesses, recovered RSCFD transmit buffers, the FACI status-clear
command, and the explicitly recovered ICU-S register surface. Unknown MMIO,
illegal widths, uninitialized state, and unsupported FACI commands are hard
faults carrying PC, address, size, access kind, and evidence provenance.
A known register without a behavior model remains ordinary typed storage; it
does not acquire invented side effects.

ICU-S is intentionally marked `recovered`: the public P1M-E manual names the
block but does not publish its full register or cryptographic semantics. The
model executes the stock command-five submit and native input/output callbacks,
but supplied ICU-S data words are scenario inputs. It does not claim to derive
a provisioned key or emulate the hardware AES-CMAC implementation.

Check that all projections match the source without rewriting them:

```bash
tools/rh850 machine model --check
```

Run one or more deterministic scenarios by registered target name:

```bash
tools/rh850 machine run camry-8965F3307000 \
  tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_ring_producer.json \
  tests/fixtures/rh850/machine/camry-8965F3307000/camry_f33_rscfd_tx.json
```

The command writes one report per scenario. Each report embeds the resolved run
contract: unique candidate count, resolved entry, structural signature, exact
matched-code hash, exact entry-instruction hash, image/model identities, initial
state contract, stop addresses, checks, and termination reason. Scenario RAM
initialization is explicit; RAM artifacts require SHA-256 identities.
Unsupported fields and all attempts to initialize registered
CodeFlash/DataFlash directly are rejected before execution.

The default functional profile establishes instruction, register, memory, and
modeled-device behavior only. It makes no cycle-timing, silicon, vehicle, or
physical-safety claim. Register rules tagged `manual` come from the public
Renesas manuals. Rules tagged `recovered`, notably ICU-S behavior, remain
exact-firmware-derived rather than public silicon specifications.

The retained scenarios use semantic structural selectors, not fixed entry
addresses. For the tracked Camry image the resolver currently produces:

|Domain|Resolved Camry entry|Exercised machine boundary|
|---|---|---|
|Ring publication|`0x00080A4A`|producer record, `SYNCP`, cursor advance|
|RSCFD transmit|`0x000852FE`|buffer-16 identifier/data and transmit request|
|TAUJ0 setup|`0x0006639C`|mode, prescaler, and calibrated reload values|
|INTC acknowledge|`0x00066062`|EIC136 pending-bit poll and clear|
|FACI command|`0x00078AE6`|status-clear command and ready state|
|ICU-S command five|`0x0008A720`|validated command submission and recovered state|
|ICU-S input callback|`0x0008A538`|four input words fed to the ICU-S data register|
|ICU-S output callback|`0x0008A5AE`|four supplied output words copied to RAM|
|Reset and MPU|`0x00078AEA` / `0x00078AE6`|RAM clearing, aliases, deny, and overlap-grant rules|

The Crown fixture resolves the same portable byte-store role from the Crown
image to `0x00077F16`; the equivalent Camry entry is `0x00078AE6`. This proves
cross-target role resolution and exact execution, not semantic equivalence of
the complete firmware images.

Run the narrow gate with:

```bash
tools/test rh850_machine
```

This gate also proves strict schema rejection, unknown-MMIO faults, executable
CodeFlash-overlay rejection, and unique role resolution on Camry and Crown
bytes. It does not promote recovered ICU-S behavior to a manual silicon claim.

## CodeFlash simulation

`codeflash-sim` executes a raw CodeFlash image at its real addresses, with
optional RAM residents loaded at exact addresses:

```bash
tools/rh850 codeflash-sim path/to/CodeFlash.bin \
  --entry 0x00012340 \
  --load 0xFEBF0000=path/to/resident.bin \
  --memory-region 0xFEBE0000,0x20000 \
  -ex run \
  -ex 'printf "RESULT=0x%x\n", *(unsigned int *)0xFEBF0100'
```

This is the fast viability check for a newly acquired binary: no target
knowledge required, entry may point into CodeFlash or any `--load` range,
`--expect STR` (repeatable) requires strings in the output, and `-ex` commands
append to the execution script. `--output-dir` retains the linked ELF,
modeled image, and output for debugging.

### Specs

Once a target's execution contract is understood, capture it as a spec and
everything becomes byte-pinned:

```bash
tools/rh850 codeflash-sim firmware/camry-8965F3307000/CodeFlash.bin \
  --spec tests/fixtures/rh850/camry_f33_gate2_codeflash_sim.json \
  --expect 'GATE2_RESULT=0x222 FRESHNESS_ARG=1 ROOT_BOOL=1'
```

A spec (see the JSON files in `tests/fixtures/rh850/`) pins the image size and
SHA-256, an assembly harness (stock GP/TP/SP context, call-boundary stubs),
RAM-load pockets (address + maximum size), memory regions, one ordered GDB
script, and instruction overlays. Each overlay replaces bytes at a known
address — but only after verifying the original bytes still match, so any
image drift aborts before execution. The harness models privileged
boot/context installation and hardware-heavy callees; everything else (stock
startup JARLs, RAM-clear, scheduler, foreground) runs unmodified at its
original address.

The TSS3 signer does not use a Camry-only checked-in spec. The dump onboarding
workflow generates byte-pinned overlays and a GP/TP/SP harness from each
resolved firmware contract, then executes the same universal payload against
that exact CodeFlash:

```bash
tools/toyota ram onboard path/to/CodeFlash.bin
```

Its two clean simulator processes share one linked ELF: one reaches the
GlobalRAM helper through the complete post-foreground fallback, the other
through the timer-bounded idle branch. Boot, context, startup-final, and
hardware-heavy foreground callees are explicit generated overlays; their
preimages remain bound to the supplied dump.

One gate runs every modeled scenario — generic synthetic image, the F33
Gate-2 stock/root-only/stage-2/stage-3 differential, the F33 and Corolla
H/F RAM residents, and the universal signer fallback/idle paths on every
registered Camry, Crown, and Corolla H/F CodeFlash:

```bash
tools/test codeflash_sim
```

These executions found a real pre-deployment defect: a non-inlined `call0`
helper linked at VMA zero became an absolute call to `0x46` after loading the
resident at `0xFEBF0000`. Both the F33 and Corolla canaries/proxies now
inline target calls.

### Proof boundary

A passing simulation proves the executed CPU instructions, exact low user-area
CodeFlash preimages, call targets, RAM placement, and modeled state transitions
— nothing else. GNU `sim/v850` does **not** model P1M-E LocalRAM aliases,
instruction-cache state or the RAM publication effect of dummy-read /
`SYNCP` / `SYNCI`, MPU/IPG access checks, ECC, reset-class RAM initialization,
interrupts, peripherals, watchdogs, command-5 hardware permission, or timing.
It also does not prove `MCTL.MA=0` misalignment exceptions unless a specific
CPU model implements and exercises them. MMIO-heavy payloads need explicit
register models; do not treat simulator success as evidence for RSCFD, ICU-S,
FACI, ECM, or timing behavior. An isolated bench or in-vehicle canary remains
required per target.

### Simulator fixes

Upstream GNU `sim/v850` has a long-standing format-VI 32-bit-immediate decoder
bug affecting `jarl32`/`jr32`/`jmp32` (the `imm32` cache in `v850.igen` used a
relational `<` where a shift was intended, and assembled the encoded halfwords
in the wrong order; still present on upstream master). The repository toolchain
applies two patches:

- `binutils-v850-sim-imm32.patch` fixes format-VI immediate word assembly;
- `binutils-v850-sim-codeflash-map.patch` replaces the legacy 32 KiB mirrored
  backing store for `0x00000000..0x000FFFFF` with a complete 1 MiB store —
  without it every `0x8000`-byte block overwrites the previous alias.

`tools/rh850 selftest` covers both fixes before accepting the simulator.

## Rebuilding the GNU setup

`tools/toolchains/v850-gcc/Dockerfile` owns the Ubuntu digest and GCC,
binutils, and GDB source revisions. Each cloned release is checked against its
pinned commit. `tools/rh850` owns the single image tag used by every command.

Build and verify it with:

```bash
tools/rh850 build-image
tools/rh850 doctor
tools/rh850 selftest
```

`tools/rh850 image` prints the canonical tag without requiring Docker.
Generic callers should use the wrapper rather than copying version strings
into argument defaults. `--toolchain`, `--image`, and `build-compat-image` are
not supported; `RH850_TOOLCHAIN_IMAGE` no longer changes image selection.

Historical compiler outputs and audit records remain immutable evidence, not
a reason to retain a second supported compiler. Current ECU payload builders
all enter the pinned toolchain through `tools/rh850`; builder CLIs do not accept
an image or compiler override. A compiler upgrade can change bytes without
changing behavior, so field-qualified historical binaries remain separate from
newly built artifacts until the new artifacts receive their own qualification.

`tools/rh850 exec ...` is the escape hatch for invoking any `v850-elf-*`
program with the repository mounted at `/src`; for example,
`tools/rh850 exec v850-elf-objdump -d build/out/example.elf`. Builders use
`tools/rh850 exec --work-dir PATH ...` when they need a scratch directory
mounted at `/out`; dependent compile, conversion, and inspection commands are
batched into one container invocation. `tools/rh850_toolchain.py` provides the
canonical command construction and provenance to Python callers.

## Official Renesas options

Renesas also ships two useful but separate products:

1. **[CS+ RH850 instruction simulator](https://www.renesas.com/en/software-tool/simulator-cs-rh850-family).**
   It models RH850 CPU instructions, registers, and address space. It is not a
   P1M-E peripheral emulator.
2. **[Cycle-Accurate Simulator for RH850](https://www.renesas.com/en/software-tool/cycle-accurate-simulator-rh850).**
   P1M-E is explicitly listed among the supported devices. It is an optional
   licensed CS+ component and is the official path when cycle timing matters.
   Renesas currently advertises executable-file support for CC-RH and GHS, not
   GNU `v850-elf`, so this is not a drop-in executor for our deployment ELF.

The current **CC-RH V2.08.00** compiler has a Linux x86-64 distribution in
addition to Windows; Renesas publishes it through the
[compiler installation guide](https://www.renesas.com/en/software-tool/compiler-installation-guide).
CC-RH is an external reference tool, not an alternative compiler selected by
`tools/rh850` or part of the supported GNU build path.

The official CS+ simulator remains valuable as an independent implementation,
especially for ISA edge cases and CC-RH differential tests. Renesas documents
[command-line Python automation of CS+](https://www.renesas.com/en/document/apn/cs-integrated-development-environment-introductory-guide-using-python-automating-debugging-cs),
so a Windows CI/VM lane is possible if we acquire/install the Renesas package.
The GNU simulator is the lower-friction default because it is already inside
the compiler image and runs the exact ELF we build.
