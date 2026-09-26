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

## Target-neutral raw images

`--spec` is optional. Point `codeflash-sim` at any raw RH850 CodeFlash binary
to package and execute it without a known target, image hash, manifest, or
Camry-specific configuration:

```bash
tools/rh850 codeflash-sim path/to/CodeFlash.bin
```

Without `--spec`, the image base and entry default to `0x00000000`; the command
starts one instruction and prints the entry disassembly and PC. Override those
facts and drive an execution episode with ordinary GDB commands:

```bash
tools/rh850 codeflash-sim path/to/CodeFlash.bin \
  --base 0x00000000 \
  --entry 0x00012340 \
  --memory-region 0xFEBF0000,0x1000 \
  --load 0xFEBF0200=path/to/resident.bin \
  -ex 'break *0x00012354' \
  -ex run \
  -ex 'printf "RESULT=0x%x\n", *(unsigned int *)0xFEBF0100'
```

`--entry` may point into CodeFlash or any `--load` range. This permits direct
resident execution without constructing a target spec first.

The image may have any nonzero size that fits the 32-bit address space.
`--load ADDRESS=PATH` accepts arbitrary raw resident/helper artifacts,
records their actual SHA-256 identities, and rejects overlaps with CodeFlash or
other loads. `--output-dir` retains the linked ELF and
`rh850-raw-codeflash-sim-result-v1` audit.

Without `--spec`, there is deliberately no image allowlist: this is the path
for a newly acquired binary. The command cannot infer that binary's reset
entry, GP/TP/SP context, RAM map, or peripherals. Supplying the correct entry
and memory regions makes CPU and ordinary-memory execution target-neutral;
booting through hardware still requires explicit MMIO models. Once an
execution contract is understood, capture it as a SHA-bound spec for
deterministic regression testing.

## Strict execution specs

Add `--spec` to enforce a known image's execution contract:

```bash
tools/rh850 codeflash-sim \
  firmware/camry-8965F3307000/CodeFlash.bin \
  --spec tests/fixtures/rh850/camry_f33_gate2_codeflash_sim.json \
  --expect 'GATE2_RESULT=0x222 FRESHNESS_ARG=1 ROOT_BOOL=1'
```

A spec binds accepted image SHA-256 identities and size, an RH850 assembly
harness, RAM/MMIO regions and initialization commands, result commands,
optional SHA-bound raw RAM artifacts, and explicit call-boundary overlays. The
runner:

1. compiles the harness and overlay stubs with the pinned `v850e3v5` toolchain;
2. verifies every overwritten callee preimage against the input firmware;
3. verifies each `--load ADDRESS=PATH` against its declared SHA-256, address,
   and size limit, and rejects overlaps with CodeFlash, the harness, or another
   load;
4. applies stubs only to a private image copy;
5. links CodeFlash at `0x00000000`, each resident/helper at its actual RAM VMA,
   and the harness at its declared address;
6. executes either to the spec stop symbol or through an explicit sequence of
   GDB break/run/continue commands, then checks each `--expect` string.

`--memory-region` adds mappings to either form. With `--spec`, any supplied
`-ex` commands replace the spec's execution sequence while retaining its setup
and result commands.

Use `--output-dir build/out/NAME` to retain `model.bin`, `scenario.elf`, and
`simulation.json`; without it, intermediate files are removed. The Gate-2
regression is registered as:

```bash
tools/test camry_f33_gate2_codeflash_sim
```

That suite executes stock, root-only, live stage-2, and stage-3 images. The
firmware function, prologue/epilogue, branches, and direct calls execute at
their original CodeFlash addresses. Only the declared external callees are
replaced with ABI boundary models, and their original bytes are checked first.

### CodeFlash plus an exact RAM resident

The F33 canary scenario builds the normal deployment artifact, loads it at
`0xFEBF0000`, starts through its real entry, and executes one foreground tick:

```bash
uv run python exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py \
  --output-dir build/out/f33-carrier

tools/rh850 codeflash-sim \
  firmware/camry-8965F3307000/CodeFlash.bin \
  --spec tests/fixtures/rh850/camry_f33_runtime_canary_sim.json \
  --load 0xFEBF0000=build/out/f33-carrier/camry_f33_runtime_canary.bin \
  --expect 'RAM_HEARTBEAT=0x45504844 TICK=1 FLAG=0x0 CONTEXT=0x43545831 STARTUP=0x53544152 FOREGROUND=0x46475231 STOCK_ZERO=0x0'
```

The scenario models privileged boot/context and unrelated hardware-heavy call
boundaries. The resident itself is unmodified. It reads the stock startup JARLs
from CodeFlash, invokes their decoded targets, executes the original stock
`0x632B2` RAM-clear function, runs its scheduler, crosses the modeled stock
foreground boundaries, clears the tick flag, increments the stock tick counter,
and updates its heartbeat. The exact breakpoint after that first episode makes
the infinite scheduler deterministic.

This execution found a real pre-deployment defect in the former F33 canary: a
non-inlined local `call0` linked at VMA zero became an absolute call to `0x46`
after loading at `0xFEBF0000`. The F33 builder now uses
`camry_f33_runtime_canary.c`, whose always-inlined call boundary leaves only the
intended indirect calls to stock CodeFlash targets.

Run the retained behavior gate with:

```bash
tools/test camry_f33_runtime_canary_codeflash_sim
```

The same gate now covers both tracked Corolla H/F images and the target-native
resident:

```bash
tools/test corolla_hf_runtime_canary_codeflash_sim
```

That regression found the same VMA-zero helper-call defect in both the Corolla
canary and command-5 proxy. Both now inline target calls; the corrected canary
executes the target-specific boot/context/startup sequence and one foreground
tick against `8965H1202000` and `8965F1208000`.

### Proof boundary

A passing CodeFlash simulation is not 100% proof that a resident will load or
work in a vehicle. CodeFlash alone cannot observe the bootloader transport,
DataFlash/calibration state, live RAM retention, MPU state at the actual handoff,
interrupt and peripheral behavior, watchdogs, command-5 hardware permission, or
production timing. The simulator proves the checked CPU instructions, exact
CodeFlash preimages, call targets, RAM placement, and modeled state transitions.
An isolated bench or in-vehicle canary remains required to prove upload,
retention, hardware interaction, and timing on each target.


The simulator does **not** make P1M-E peripherals magically exist. Code that
only needs CPU state and ordinary memory is a good candidate for direct
execution. MMIO-heavy payloads need one of three treatments: stop before the
MMIO boundary and inspect state, factor pure logic behind a narrow hardware
interface and test that logic in the simulator, or add an explicit test model
for the specific registers being exercised. Do not treat instruction-simulator
success as evidence for RSCFD, ICU-S, FCU, interrupt-controller, or timing
behavior.

Upstream GNU `sim/v850` has a long-standing format-VI 32-bit-immediate decoder
bug that affects `jarl32`, `jr32`, and `jmp32`. The `imm32` cache in
`sim/v850/v850.igen` used a relational `<` where a shift was intended and also
assembled the two encoded halfwords in the wrong order. The same expression is
still present on current upstream master, so merely upgrading binutils/GDB does
not fix it.

The repository-owned toolchain applies two patches while building GNU
binutils/GDB:

- `binutils-v850-sim-imm32.patch` fixes format-VI immediate word assembly.
- `binutils-v850-sim-codeflash-map.patch` replaces the simulator's legacy
  32 KiB mirrored backing store for `0x00000000..0x000FFFFF` with a complete
  1 MiB backing store. Without it, loading a P1M-E image makes every
  `0x8000`-byte block overwrite the previous alias.

`tools/rh850 selftest` covers both fixes before accepting the simulator. These
are CPU/address-space fixes only; they are not evidence for P1M-E peripherals
or unmodeled stock/MMIO behavior.

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
mounted at `/out`; `tools/rh850_toolchain.py` provides that command construction
and canonical provenance to Python callers.

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
