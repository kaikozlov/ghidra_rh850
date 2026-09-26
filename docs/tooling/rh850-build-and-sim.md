# RH850 build and execution testing

The repository's target-native payloads use the GNU `v850-elf` toolchain
validated against the known-working public Toyota payload lineage. The useful
detail for local testing is that the same binutils/GDB build already contains
GNU's V850/RH850 instruction simulator: `v850-elf-gdb` exposes `target sim` and
advertises `v850e3v5`, the architecture selected by our payload builders.

Use the repository wrapper rather than assembling ad-hoc Docker commands:

```bash
tools/rh850 doctor
tools/rh850 selftest
```

`selftest` compiles a freestanding `-mv850e3v5 -mno-app-regs` program, links it
at the real payload VMA `0xFEBF0000`, maps that RAM range in the simulator,
executes it, and checks a deterministic result in simulated RAM. This exercises
the compiler, linker, ELF loader, RH850 instruction decoder, and basic
register/memory execution together.

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

The pinned GNU `sim/v850` also has an instruction-coverage boundary that matters
for our real payloads: the ordinary near `jarl` form executes correctly, while
the RH850 `jarl32` extension used for far stock-function calls is misexecuted by
this simulator build. A direct probe loops on the `jarl32` instruction instead
of reaching its linked target. Simulator harnesses must therefore keep their own
calls in near-`jarl` range and test production logic that does not itself cross a
`jarl32` boundary. This is a simulator limitation, not an ECU/compiler ABI
finding.

## Rebuilding the GNU setup

The historical local image `v850-gcc-scratch` came from the public
Bk2ol/I-CAN-hack recipe. A repository-owned rebuild recipe now lives at
`tools/toolchains/v850-gcc/Dockerfile`. It pins:

- Ubuntu 22.04 by OCI digest;
- binutils/GDB `binutils-2_41-release` commit
  `675b9d612cc59446e84e2c6d89b45500cb603a8d`;
- GCC `releases/gcc-13.2.0` commit
  `c891d8dc23e1a46ad9f3e757d09e57b500d40044`.

Build or inspect it with:

```bash
tools/rh850 build-image
tools/rh850 doctor
```

`tools/rh850 exec ...` is the escape hatch for invoking any `v850-elf-*`
program with the repository mounted at `/src`; for example,
`tools/rh850 exec v850-elf-objdump -d build/out/example.elf`.

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
It is useful as a reference/secondary compiler, but it is not a drop-in
replacement for the repository's payload compiler: exact Toyota
firmware already disproves CC-RH's normal `ep` preservation rule, while the
current GCC lineage has a byte-identical reproduction of a published working
Toyota payload. Keep GCC as the deployment compiler unless a particular test
needs CC-RH comparison.

The official CS+ simulator remains valuable as an independent implementation,
especially for ISA edge cases and CC-RH differential tests. Renesas documents
[command-line Python automation of CS+](https://www.renesas.com/en/document/apn/cs-integrated-development-environment-introductory-guide-using-python-automating-debugging-cs),
so a Windows CI/VM lane is possible if we acquire/install the Renesas package.
The GNU simulator is the lower-friction default because it is already inside
the compiler image and runs the exact ELF we build.
