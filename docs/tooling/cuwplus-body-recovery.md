# Current CP-protected body recovery: CUWPlus and GTS+ auxiliaries

## Result

The current GTS+ `CUWPlus` executable corpus is recoverable offline from the
installed CP stub + `._` sidecar pairs. Unlike the main `GTSPlus` tree, CUWPlus
does not have same-path plaintext installer twins, so recovery executes the
protector itself in a constrained 32-bit emulator and rebuilds a clean analysis
PE from the protector's own restored-memory state.

For the pinned GTS+ `2026.03.002.02` corpus under:

```text
software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/CUWPlus/
```

the census is complete:

| input class | protected bodies | recovered |
|---|---:|---:|
| native PE32 | 127 | 127 |
| CLR-labeled PE32 | 16 | 16 |
| **total** | **143** | **143** |

The 16 CLR-labeled inputs comprise 12 ordinary managed images and four mixed
native/CLR wrappers. All 143 rebuilt outputs parse as PE files; all 16 CLR
outputs additionally parse through `dnfile` with intact CLR metadata/tables.

Run:

```sh
tools/gts recover-cuw-bodies
```

The default output is:

```text
build/out/cuwplus-unprotected/
```

`manifest.json` records each protected stub and sidecar SHA-256, the recovered
classification, final protector section map, import/entrypoint evidence, and
clean-output identity.

## Full `Toyota Diagnostics` protected-body census

The CP format is not CUWPlus-specific. The same decoder applies to every
remaining protected 32-bit PE in the current `Toyota Diagnostics` tree. The
release contains **249** stub + `._` body pairs, all x86 PE32:

| tree | protected bodies | recovery path |
|---|---:|---|
| `GTSPlus` | 54 | exact same-release plaintext installer twins via `tools/gts recover-bodies` |
| `CUWPlus` | 143 | CP emulation + clean PE rebuild via `tools/gts recover-cuw-bodies` |
| auxiliary products | 52 | the same CP emulation + rebuild via `tools/gts recover-aux-bodies` |
| **total** | **249** | **249 recoverable** |

For a single complete materialization, run:

```sh
tools/gts recover-all-bodies
```

This writes the three component corpora and an aggregate 249/249 manifest under
`build/out/gts-all-unprotected/`. The component commands remain useful when
only one product family is needed.

The auxiliary 52 are `DS-4` 14, `ContentServer` 10,
`GTSPlusCSVConverter` 10, `GTSPlus DataSync` 8, `GTSPlusTSEConverter` 5,
`GTSPlusGraphViewer` 2, and one each in `DiagMessageInput`, `GTSE`, and
`PCS Data Viewer`. Their input split is 18 native and 34 CLR-labeled PEs.
`tools/gts recover-aux-bodies` preserves those top-level product paths under
`build/out/gts-aux-unprotected/`.

The main `GTSPlus` tree intentionally keeps the installer-twin path because it
produces Toyota's exact original files without emulation. The generic decoder
is used where no such plaintext packaging shortcut exists; the common CP
mechanics below were established from CUWPlus and then verified across the
auxiliary product families.

## What is recovered versus regenerated

The output files are **clean analysis PEs**, not a claim of byte-identical
reproduction of Toyota's never-retained plaintext disk files.

The recovered evidence is stronger than merely producing a parseable wrapper:

- the application code/IL and metadata are restored by the CP loader itself;
- native original entrypoints are observed at the protector handoff;
- original native import symbols are decrypted by CP phase `0x5C0` and their
  real IAT writes are captured as they occur;
- the protector's final `VirtualProtect` pass supplies the authoritative
  original application section RVAs and virtual sizes;
- resources and relocation bodies are taken from those restored ranges; and
- six separately retained runtime-unpacked native DLLs independently match the
  new decoder's entrypoint and complete restored `.text` **byte-for-byte**.

The rebuilder intentionally drops CP loader/workspace residue, CP-only TLS and
security structures, transient resolved IAT values, and the protector's second
import representation. Therefore a clean output can be smaller than a prior
runtime memory dump without losing application code.

Two reconstruction details are explicitly analysis normalizations:

1. `TCUWControlCommPhase.dll` is the single native seven-range layout with a
   genuine `.idata` and `.00cfg`. Its original import IAT/name RVAs are
   recovered in place, but its restored `.rdata` ends at the export directory,
   so the rebuilt PE uses a small `.impfix` section only for reconstructed
   import descriptors.
2. Within CUWPlus, `CuwBackendServiceConsoleApp.exe` is the lone managed EXE. CP removes the
   normal CLR native trampoline before the captured final state. The rebuilder
   inserts the standard six-byte `jmp [IAT]` `_CorExeMain` bootstrap into
   verified zero padding after the restored managed body. Its IL/metadata and
   CLR header are recovered; the tiny bootstrap is regenerated.

Those boundaries are represented in tooling and tests rather than hidden by a
whole-file-equality claim.

## Protector format and stages

### `KONN` sidecar header

The first 32 bytes of each native CP sidecar are an eight-dword encoded header.
The first dword is both retained and used as state; dword 1 must decode to
little-endian `KONN` (`0x4E4E4F4B`):

```text
out[0] = src[0]
state = src[0]
for i = 0..6:
    raw = src[i + 1]
    out[i + 1] = raw ^ state
    state = ((raw - i + state) mod 2^32) ^ (i * i)
```

For current `CUW.dll` this produces:

```text
0b1f390e 4e4e4f4b 0000196c 00096000
000004e0 0001d9d0 00098400 000000a0
```

This identifies the initial loader entry, second-stage destination/source and
entry geometry rather than treating the `._` file as opaque entropy.

### Stage-1 rolling dword transform

The sidecar chunk used to materialize the next protector stage is transformed
as:

```text
state = seed + ~length            # modulo 2^32
for i over 32-bit words:
    raw = src[i]
    dst[i] = raw ^ state
    state = (raw + i + state) ^ (i * i)   # modulo 2^32
```

For `CUW.dll`, stage 1 materializes the next protector at RVA `0x96000` and
redirects to RVA `0x98400`.

### Exception-heavy byte transform

The later code transform deliberately uses single-step/SEH behavior. Its byte
operation was recovered exactly and is accelerated by the emulator rather than
executing millions of exception round trips:

```text
dx = 1
for byte in buffer:
    for bit = 0..7:
        byte ^= (dx & 1) << bit
        dx = (dx << 1) & 0xffff
        if dx & 0x8000:
            dx ^= 0x8003
```

This reproduces the native protector's output exactly on observed fixtures.

## Restore lifecycle

The meaningful CP phases are visible through its own status records:

| phase | recovered role |
|---|---|
| `0x590` | maps/consumes the real sibling `._` sidecar and performs the first large body restoration |
| `0x5A0` | completes the application-code transform; native `.text` becomes plaintext |
| `0x5C0` | decrypts original import names, calls `GetProcAddress`, and writes resolved addresses into the real application IAT |
| final protection pass | assigns page protections to the restored application sections, exposing their original RVA/size geometry |
| DLL `000-000-000` | normal protector-success boundary |
| managed EXE `ExitProcess(0)` | EXE success boundary after its final protection map |

The import recovery is particularly useful for RE. The installed CP stub may
contain only one placeholder import per dependency, while phase `0x5C0` reveals
the full original decorated C++ symbol corpus. `CUW.dll`, for example, recovers
293 imports across 27 DLLs, including the full Toyota `TCUW*` helper surface.
The IAT slot is captured from the write itself, not inferred later by scanning
for a duplicated resolved pointer.

## Windows/anti-debug model

`tools/techstream/cp_body_decode.py` currently hosts the generic CP worker and emulates the narrow Windows/NT surface
actually exercised by this protector. That includes its TEB/PEB/LDR view,
file/mapping APIs for the real stub and sidecar, memory protection/allocation,
and the protector's process/thread audits.

The normal audit path uses:

- `NtQuerySystemInformation(SystemProcessInformation)`;
- `OpenThread(0x40)`; and
- `NtQueryInformationThread` class 9 (`ThreadQuerySetWin32StartAddress`).

Those calls are anti-debug/process checks; they are not payload crypto.

Managed EXE protector variants additionally enter phase `0x520`; they check
`IsDebuggerPresent` / `CheckRemoteDebuggerPresent`, query
`ProcessDebugPort`, execute `INT 2D` under the protector's own SEH frame, and
perform further process/module/registry checks. This branch is observed in the
CUW backend console as well as auxiliary Windows-service/viewer executables;
the local `NtQueryInformationProcess` dispatch slot moves between protector
layouts, so the emulator recognizes its ABI rather than a hard-coded module
name or RVA. The emulator supplies a normal
non-debugged synthetic process and dispatches `INT 2D` as Windows
`EXCEPTION_BREAKPOINT`, allowing the protector's own handler to choose the
continuation. No decrypted body bytes are substituted by hand.

## Independent native oracle

Six runtime-unpacked DLLs retained from the earlier Windows experiment provide
an independent oracle under:

```text
software/Techstream/gtsplus/cuwplus/CUWPlus/unpack/
```

The tracked recovery reproduces the original entrypoint and entire application
`.text` byte-for-byte for all six:

| module | entry RVA | recovered imports |
|---|---:|---:|
| `CUW.dll` | `0x6C7D9` | 293 |
| `TCUWCalibrationFile.dll` | `0x70CD` | 44 |
| `TCUWCanCommonPrepareWriter.dll` | `0x20DB` | 58 |
| `TCUWCanReproStdFlashWriter.dll` | `0x449F` | 86 |
| `TCUWCanReproStdPrepareWriter.dll` | `0x393B` | 96 |
| `TCUWP6CanReprostdFlashWriter.dll` | `0x63CF` | 131 |

For five modules the recovered import list also equals the old unpacker's list
exactly. `CUW.dll` differs only in presentation for three `OLEAUT32` imports:
CP resolves ordinals `#2/#9/#6`, while the older dump named those same exports;
the IAT RVAs are identical.

`tests/verify_cuwplus_body_recovery.py` keeps the verification fast by pinning
the full external census but actively re-running one representative of every
rebuild path: ordinary native, seven-section native, pure managed DLL, mixed
native/CLR, and managed EXE. It also compares a newly decoded native `.text`
against the independent runtime-unpacked oracle.

## Relationship to GTS+ proper

Do not replace the simpler GTS+ recovery with protector emulation. The main
`GTSPlus` installers already ship complete same-release plaintext `GTSPlus`
twins beside the installed `GTSPlusCP` representations; `tools/gts
recover-bodies` extracts those directly and is the preferable path.

CUWPlus is different: its installer does not expose equivalent plaintext twins,
which is why `tools/gts recover-cuw-bodies` performs the CP emulation documented
here. Together, the two paths remove the current executable-body availability
boundary across both major GTS+ host trees.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-083](../reference/index.md#finding-tms-083)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
