# RH850 build and execution testing

`tools/rh850` supports one pinned GNU `v850-elf` toolchain: GCC 16.2.0,
binutils 2.46.1, and GDB 18.1 with the repository-local simulator fix.
Builds and instruction simulation use the same image and `v850e3v5`
architecture. There is no GCC 13 compatibility path or compiler-profile selection.

Use the repository wrapper rather than assembling ad-hoc Docker commands:

```bash
tools/rh850 doctor
tools/rh850 selftest
```

`selftest` compiles a freestanding C function and assembly harness with
`-mv850e3v5 -mno-app-regs`, links them starting at `0xFEBF0000`, maps RAM in
the simulator, executes far branches and the C function, and checks a
deterministic result in simulated RAM. The C function computes from a volatile
local rather than a folded constant. This exercises C compilation, linking,
ELF loading, far control flow, and basic register/stack/memory execution together.

For a retained ELF, add the address ranges the program can touch and then give
ordinary GDB commands:

```bash
tools/rh850 sim build/out/example.elf \
  --memory-region 0xFEBE0000,0x20000 \
  -ex 'break rh850_sim_stop' \
  -ex run \
  -ex 'info registers'
```

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

The repository-owned toolchain applies
`tools/toolchains/v850-gcc/patches/binutils-v850-sim-imm32.patch` while building
GNU binutils/GDB. `tools/rh850 selftest` exercises positive and negative far
`jarl32` and `jr32` displacements with nonzero upper words before accepting the
simulator. This fixes CPU control-flow simulation only; it is not evidence for
P1M-E peripherals or for unmodeled stock/MMIO behavior.

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
