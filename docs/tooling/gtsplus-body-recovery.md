# Current GTS+ protected-body recovery

## Result

The current GTS+ executable bodies are recoverable offline. The installed
`GTSPlus` tree contains selected PE files in a CP-protected representation:

- a valid `.dll` / `.exe` whose protector/loader remains materialized while the
  original application body is absent or transformed; and
- a sibling `.dll._` / `.exe._` containing the protected payload.

For **every such file in the installed GTS+ tree**, Toyota's AgentLite-downloaded
installer set also carries the same relative path as a complete, original PE in
an unprotected `GTSPlus` InstallShield group beside the protected `GTSPlusCP`
group. Runtime decryption is therefore unnecessary for GTS+ itself.

Run:

```sh
tools/gts recover-bodies
```

The recovered files are written by default under:

```text
build/out/gtsplus-unprotected/
```

with their installed GTS+ relative paths preserved. `manifest.json` records the
installer source, SHA-256 identities, protected stub/sidecar identities, and PE
`.text` geometry for every recovered binary.

## Provenance chain

The pinned corpus is GTS+ `2026.03.002.02` under
`software/Techstream/gtsplus`. AgentLite downloaded the installer archive now
retained as:

```text
software/Techstream/gtsplus/unpacked/gtsplus/gtsplus_msi.7z
```

Two installers cover the protected files present under the installed
`Toyota Diagnostics/GTSPlus` tree:

| Installer | Unprotected group | Protected group | protected body pairs |
|---|---|---|---:|
| `Setup_PF.exe` | `GTSPlus` | `GTSPlusCP` | 45 |
| `Setup_InfoCenter.exe` | `GTSPlus` | `GTSPlusCP` | 9 |
| **Total** | | | **54** |

For all 54 paths:

1. the installer contains `GTSPlusCP\<path>` and
   `GTSPlusCP\<path>._`;
2. the installer contains `GTSPlus\<path>` at the same relative path;
3. the extracted CP stub is byte-identical to the installed stub;
4. the extracted CP sidecar is byte-identical to the installed `._` sidecar;
5. the `GTSPlus` twin is a complete parseable PE; and
6. the installed protected-tree census and recovered-path census are exactly
   equal: **54/54**.

The only `GTSPlusCP` PE files without an unprotected same-path twin are
`GTSPluscoree32.dll` and `GTSPluscoree64.dll`. They are tiny protector runtime
helpers and do **not** have `._` body sidecars, so they are outside the protected
body census.

### `CommandCommon.dll` witness

The old current-GTS+ limitation was especially visible in
`bin/CommandCommon.dll`:

| representation | size | `.text` raw | `.text` virtual | SHA-256 |
|---|---:|---:|---:|---|
| installed / `GTSPlusCP` stub | 356,368 | `0x1000` | `0xD4000` | `89fe3c1f17d7ec58e659a099fc4fc96b55d30534d813c2a4c26211c4d30284c2` |
| CP sidecar `.dll._` | 792,048 | — | — | `2fd7211088bee794d56239d3f2960d03f5747dbe7c20097fca6c34559f80d6da` |
| recovered `GTSPlus` original | 1,280,016 | `0xD3600` | `0xD34BC` | `98e313d197eb7115d037a2d46e71343b4b44862356e9d772c8f2f03d96e638d3` |

Thus the statement that the current helper bodies are absent **from the
installed CP stub** remains true, but it is no longer a corpus limitation. The
same release's original `CommandCommon.dll` is available directly from the
installer and can be imported into Ghidra.

Managed assemblies are not required to show native-style `.text` growth after
recovery. For example, a CP loader can have a larger `.text` than the original
CLR image. The proof is the same-path installer twin plus exact CP-to-installed
identity, not a universal section-size heuristic.

## How the extractor works

`tools/techstream/recover_gtsplus_bodies.py` is intentionally an installer
extractor rather than a protector emulator:

1. locate the single release containing `Setup_PF.exe` in `gtsplus_msi.7z`;
2. extract each relevant InstallShield SFX with `7zz`/`7z`;
3. expose its `[0]` payload;
4. locate concatenated InstallShield cabinets by their `ISc(` signatures;
5. use `unshield` to select the cabinet containing both `GTSPlus` and
   `GTSPlusCP`;
6. enumerate every `GTSPlusCP\*.dll._` / `*.exe._` entry and require a
   same-relative-path `GTSPlus` twin;
7. extract both groups;
8. require the CP stub and sidecar to hash exactly to the installed files; and
9. copy the original `GTSPlus` PE to the output tree and write the manifest.

No GTS+ executable is run. No Windows environment, debugger, memory dump, or
protector key is required.

`tests/verify_gtsplus_body_recovery.py` repeats the recovery against the pinned
external corpus and pins the 54/54 coverage plus the `CommandCommon.dll`
witness identity.

## What `AgentLite protected` means here

The evidence supports a more precise vocabulary than the earlier shorthand.
AgentLite is the update/download/install orchestrator. The actual installer
layout calls the transformed executable group **`GTSPlusCP`** and retains the
untransformed group as **`GTSPlus`**. We can therefore say that AgentLite
delivers/installs the CP-protected representation; the current evidence does
not require attributing the body transformation algorithm itself to the
AgentLite service executable.

This distinction matters because the protection is defeated for analysis at
the packaging boundary: recover `GTSPlus`, do not attack the installed
`GTSPlusCP` payload unless the protector itself is the research target.

## CUWPlus boundary and recovered protector mechanics

Do not silently generalize the GTS+ installer-twin shortcut to CUWPlus.
`CUWPlusPF.exe` exposes the protected CUW DLL + `._` pairs in its main cabinet,
but no adjacent plaintext CUW group was found. During this investigation the
first CP loader layer was nevertheless decoded far enough to make the boundary
concrete.

The protected CUW stub keeps a small executable `.text` loader. It dynamically
resolves the usual Windows file/mapping/protection APIs and opens its sibling
`._` payload. The first 32-byte sidecar record decodes to eight dwords; dword 1
must be little-endian `KONN` (`0x4E4E4F4B`). Header decoding is:

```text
out[0] = src[0]
state = src[0]
for i = 0..6:
    raw = src[i + 1]
    out[i + 1] = raw ^ state
    state = ((raw - i + state) mod 2^32) ^ (i * i)
```

For current `CUW.dll`, mode-0 decodes to:

```text
0b1f390e 4e4e4f4b 0000196c 00096000
000004e0 0001d9d0 00098400 000000a0
```

The first loader stage restores a second-stage protector blob at RVA `0x96000`
and redirects to RVA `0x98400`. Its rolling 32-bit transform is:

```text
state = seed + ~length          # modulo 2^32
for i over 32-bit words:
    raw = src[i]
    dst[i] = raw ^ state
    state = (raw + i + state) ^ (i * i)   # modulo 2^32
```

The decoded second-stage entry bytes were checked against the retained
runtime-unpacked CUW specimens and match exactly. Emulation also showed the
second stage resolving `VirtualProtect`, `VirtualAlloc`, `VirtualQuery`,
`OpenProcess`, `WriteProcessMemory`, file/time/process APIs, and writing a
protector fingerprint record headed by timestamp, module paths, and version
`003-003-000`. It returns without eagerly rewriting the hollow application
`.text` in the synthetic DllMain environment, consistent with additional
protector state/on-demand behavior.

That CUW work is retained here because it establishes that `._` is a real
multi-stage CP container rather than arbitrary missing-file data. It is **not**
needed to recover GTS+ bodies, and this document does not claim a complete
offline CUWPlus body decoder.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-081](../reference/index.md#finding-tms-081)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
