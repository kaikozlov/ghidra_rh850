# Variant acquisition readiness checker

> **Scope:** offline, read-only evidence-chain check for an acquired RH850/P1M-E
> CodeFlash artifact and its handoff to structural triage and the semantic
> resolver
>
> **Document type:** tooling
>
> **Status:** active
>
> **Evidence source:** generated artifact over the acquired image bytes
>
> **Confidence:** readiness statement only — it binds provenance, it does not
> validate any mechanism on the target
>
> **Tool:** `tools/check_variant_acquisition.py`
>
> **Verification:** `tests/verify_variant_acquisition_readiness.py`
> (`make verify-one SUITE=variant_acquisition_readiness`)

## Purpose

When a CodeFlash image arrives from a new target (the newer-TSK/Corolla-class
cases in [../variants/README.md](../variants/README.md)), the first hour should
not be spent re-deriving what "usable artifact" means. The checker turns the
acquisition→triage→resolver handoff into one command and one machine-readable
artifact:

```sh
uv run --locked python tools/check_variant_acquisition.py CodeFlash.bin \
  --run-json CodeFlash.bin.run.json --notes "target X, bench Y" \
  -o build/out/target-evidence/acquisition-readiness.json
```

Exit code `0` means ready-for-triage; any failure mode prints the exact reason
and exits nonzero. The tool never mutates the image, never opens Ghidra, and
never requires hardware.

## Stages

| Stage | Checks | Failure mode |
|---|---|---|
| **acquisition** | exact bare 1 MiB geometry via the shared `validate_codeflash_geometry` gate (rejects the `0x108000` DataFlash+CodeFlash concatenation and truncated/oversized images with the strip-prefix instruction); recomputed SHA-256/size; optional binding of the dumper `.run.json` (`p1me-codeflash-live-acquisition-v1`): run-record SHA must equal the bytes on disk, and the run must report a complete, non-interrupted acquisition | exit `1`, `problems[]` names each disagreement |
| **structure triage** | runs the calibration-independent structural scanner ([rh850-codeflash-structure-scanner.md](rh850-codeflash-structure-scanner.md)) and summarizes boot-CRC descriptors, RAM-exec gate anchors, XCP `0x7F7/0x7F8` route/map anchors, and SecOC resolver prefilter site counts | informational — absence is weak evidence only |
| **resolver readiness** | whether `tools/resolve_secoc_patch_image.sh` will accept the image in its current state, plus optional patch-manifest (`toyota-secoc-patch-manifest-v1`) SHA binding; emits the exact next command | `ready: false` with the blocking reason |

## Output contract

One JSON artifact (`variant-acquisition-readiness-v1`):

- `acquisition` — geometry verdict, recomputed SHA/size, optional run-record
  cross-checks, `problems[]`;
- `structure_triage` — the scanner summary described above;
- `resolver_readiness` — geometry/manifest gates and the literal next command;
- `ready` — top-level conjunction;
- `readiness_boundary` — standing text: ready-for-triage binds the artifact, it
  does **not** validate any Sienna-recovered mechanism on the target. Every
  transfer claim stays **hypothesis** until verified against the target's own
  bytes.

The artifact is designed to slot into the newer-TSK evidence bundle as the
CodeFlash half of the target manifest
([../variants/target-artifact-manifest.schema.json](../variants/target-artifact-manifest.schema.json)):
the manifest pins the artifact by hash; this report proves what the artifact is
and what safely runs next against it.

## Boundary

- The checker is deliberately offline: it cannot run the semantic resolver
  itself, because resolution requires a disposable Ghidra import
  ([secoc-semantic-patch-resolver.md](secoc-semantic-patch-resolver.md)).
- It performs no per-calibration software-ID lookup; identity is hash + structure
  only, matching the scanner's provenance rule.
- A `ready: true` report on a foreign image authorizes nothing beyond triage;
  it is not evidence that the XCP surface, RAM-exec gate, or SecOC gate function
  on that calibration.
