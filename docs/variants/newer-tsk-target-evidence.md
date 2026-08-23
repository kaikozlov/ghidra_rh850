# Newer-TSK EPS target evidence plan

> **Document type:** target variant evidence contract
>
> **Status:** artifact- and bench-blocked
>
> **Evidence grade:** hypothesis until exact target bytes or labeled traces exist

“Newer TSK EPS” is not yet an identified calibration. This page defines the
minimum evidence needed before transferring any `8965B4512000` conclusion to a
new target. It deliberately has no guessed part number, MCU, bootloader family,
SecOC profile, or Techstream route.

## Required target identity and artifacts

A reviewable target bundle requires all of the following:

1. exact calibration/part number and raw `F181` identity response;
2. complete CodeFlash, with byte length and SHA-256;
3. complete DataFlash, with byte length and SHA-256;
4. matching Techstream application version and regional DDB set, each pinned by
   hash;
5. the exact matching `.cuw`/calibration package, retained privately and
   represented in Git only by metadata and hash;
6. six separately labeled J2534 captures: health check, data list, active
   test/customization, MACKey Registration, CUW preparation, and reflash
   authorization/programming;
7. pseudonymous vehicle/session metadata sufficient to correlate the artifacts
   without committing VIN, account, license, or server-session identifiers.

The machine-readable contract is
[target-artifact-manifest.schema.json](target-artifact-manifest.schema.json),
with a redacted all-missing specimen in
[target-artifact-manifest.example.json](target-artifact-manifest.example.json).
Instantiate it only under an ignored path such as
`build/out/target-evidence/target-artifacts.local.json`. When a CodeFlash image is
in hand, bind it first with the offline readiness checker
([../tooling/variant-acquisition-readiness.md](../tooling/variant-acquisition-readiness.md)):
the readiness artifact records geometry, SHA, run-record provenance, and the
resolver handoff state that this bundle then pins by hash.

## Claims that must be re-proved

| Sienna lead | Exact target discriminator | Transfer state |
|---|---|---|
| MEM-SAFE-001 partial-block raw write | target TransferData length gate, decrypt block-count arithmetic, authorization lifetime, RAM window, callback location | hypothesis |
| MEM-SAFE-003 equality oracle | target RID registration, compare-mode RequestDownload, accepted address range, response behavior | hypothesis |
| Boot/application SecurityAccess | target service tables, secrets/derivation, session and policy gates | hypothesis |
| Function/callback graph | fresh target-native function discovery and indirect-table audit | hypothesis |
| SecOC receive profile | target PDU tables, freshness layout, tag width, ICU selector, acceptance gates | hypothesis |
| ICU-S command-5 signing | target command adapter plus live slot permission/latency/contention | hypothesis |
| Techstream/CUW route | matching `.cuw` factory metadata joined to a labeled host trace | hypothesis |
| MACKey/TSK behavior | labeled request/response traffic plus target implementation or exact DDB/host consumer | hypothesis |

Similarity of SIDs, DIDs, function bytes, or DDB vocabulary is useful for
prioritization but cannot upgrade a transferred claim above hypothesis without
the target-specific discriminator in the table.

## Capture and privacy boundary

Use the isolated-bench procedure in
[../tooling/techstream-capture-procedure.md](../tooling/techstream-capture-procedure.md).
Raw logs and proprietary artifacts remain private/ignored. A committed
derivative may include normalized diagnostic bytes only after reviewing every
record for VIN, account, license, key material, server tokens, and session IDs;
otherwise commit only hashes, counts, operation labels, and bounded findings.

## Current disposition

No exact newer-TSK part number, target CodeFlash/DataFlash, matching `.cuw`, or
labeled official Techstream capture is present. Therefore:

- V18's zero `SecOC`/`VehSec` vocabulary supports only “no named/static path
  recovered in pinned V18”; it does not prove generic J2534 traffic never
  carries secured runtime frames;
- Sienna firmware findings remain Sienna-specific;
- target-generation transfer remains **hypothesis**, with zero verified exact
  transfers in [../status/ANALYSIS_STATUS.md](../status/ANALYSIS_STATUS.md).


## Ephemeral runtime transfer boundary

The reported newer-EPS `FEBE0000` shellcode link VMA is not sufficient to
transfer the Sienna RAM scheduler. `tools/resolve_ephemeral_runtime_image.sh`
separates the application/SecOC semantic contract from authenticated-download and
application-retention geometry. Until a specific foreign CodeFlash SHA has
verified callback/download bounds plus retained application-RWX memory, the target
manifest remains non-buildable even if the scheduler and Gate-2 shapes match.

This is intentional: `data/variant_ram_exec_requirements.json` retains the
external `FEBE0000` observation but leaves callback-cell and retained-RWX fields
null. No target is allowed to inherit Sienna `FEBF0000` geometry from that report.
