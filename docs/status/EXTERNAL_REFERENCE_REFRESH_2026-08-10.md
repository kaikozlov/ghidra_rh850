# Stage 8 external-reference and missing-artifact refresh

> **Date:** 2026-08-10
>
> **Scope:** bounded refresh required by Stage 8 of
> `REFERENCE/ghidra_rh850_codex_static_analysis_handoff.md`
>
> **Purpose:** determine whether a previously blocked static task became
> unblocked. This is not an open-ended literature or firmware search.

## 1. Upstream delta census

The six repositories already pinned by `external-references.lock.json` were
fetched before comparison. Only the tracked research branch for each source is
used to decide whether its existing pin should advance.

| Source | Pinned revision | Current tracked upstream | Delta | Stage-8 disposition |
|---|---|---|---:|---|
| `lochuan/RH850_P1m-E` | `b8c6bcf...` | same `main` | 0 | keep pin |
| `I-CAN-hack/secoc` | `4ce19cc3...` | same `main` | 0 | keep pin |
| `calvinpark/openpilot` | `eeb87f4f...` | same `span` | 0 | keep pin |
| `Bk2ol/tsk_extraction_by_can_log` | `db453752...` | same `main` | 0 | keep pin |
| `Vance425/ToyotaSienna2024OpenpilotAnalysis-_Note` | `3333453f...` | same `main` | 0 | keep pin |
| `commaai/opendbc` | `c9b31d21...` | `e677024b...` `master` | 51 commits | keep pin; no SecOC-core/DBC change |

The `opendbc` delta was filtered by path and content. Since the pinned revision:

- `opendbc/car/secoc.py` is unchanged;
- `opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc` is unchanged;
- `opendbc/car/toyota/toyotacan.py` is unchanged;
- the Toyota controller change is a `Platforms.with_flags`/flag-refactor; and
- the other relevant Toyota change is firmware-query cleanup.

There is therefore no SecOC sender/profile reason to advance the existing
`opendbc` evidence pin.

## 2. Newly pinned optskug evidence

`optskug/docs` was explicitly named by the Stage-8 handoff but was not
previously revision-pinned. Its current `main` revision is now pinned as:

```text
2c7184122d3f1644dfc9f32e98daaa45df653098
```

`README.md` is also hash-pinned in `external-references.lock.json`.

The material new item is the July 2026 rekey report retained by that source:
Toyota's official key-configuration software reportedly requires **both an MCU
ID and VIN**, and a VIN-only request is rejected. This independently establishes
that an MCU identity is a distinct required input in the observed official
rekey workflow.

It does **not** establish that Techstream MACKey Registration's 16-byte
`SafekeyNumber` (`22 10 10`) is that MCU ID. No retained public transcript joins
the label `MCU ID` to DID `0x1010`, and the pinned Techstream binaries themselves
still contain no such naming edge. The correct Stage-8 refinement is therefore:

```text
an MCU ID is externally observed as a required rekey input
!=
SafekeyNumber / DID 0x1010 is proved to be that MCU ID
```

The same pinned optskug revision also corroborates two results already modeled
locally rather than creating new findings:

- the Toyota-B physical CAN0/CAN1 swap can change programming/dump behavior in
  ways not reproduced by simply selecting another Panda logical bus; and
- the 2024 RAV4 Prime persistent-patch experiment produced U023A87 / Missing
  Message after forcing the old SecOC profile, consistent with the bounded
  routing analysis already recorded in this repository.

## 3. Non-default branch triage

This pass also checked high-signal non-default public branches because binary
acquisition work can land there without changing the pinned main branch.

| Source / branch | Tip | Relevant content | Result |
|---|---|---|---|
| `Bk2ol/...:research` | `69167798...` | C shellcode/build source, widened DataFlash range | already incorporated as source-family evidence; no target firmware |
| `I-CAN-hack/secoc:tundra` | `b80d9104...` | Tundra/HSM adaptation | different target; no Sienna/Corolla missing artifact |
| `calvinpark/openpilot:tskm` | `28ff8452...` | generic range dumper plus CodeFlash/DataFlash/Global-RAM/Local-RAM payloads | useful future acquisition tooling; no target dump bundled |
| `Vance425/..._EN:main` | `13d4ce4b...` | public English reports, logs, scripts, June-1 capture archive | no `4514000` CodeFlash or completed partner dump/capture output |

The Calvin `tskm` branch is worth remembering for future bench acquisition: it
contains authenticated payloads for wider memory classes rather than only the
historical key-dump path. It does not itself unblock a firmware-static task.

## 4. Missing-artifact acquisition matrix

The search was deliberately exact and bounded. It included:

- local sibling-repository and ignored-file census;
- `git fetch`/branch comparison for all named sources;
- GitHub code searches using exact part identifiers and path/extension filters;
- GitHub repository and issue/PR searches;
- release-asset and fork-tree inspection for Vance, Bk2ol, and I-CAN-hack;
- exact web searches for the part identifiers, firmware/dump terms, and the
  Sienna EPS calibration-file lead.

A negative result means "not found in this bounded public/indexed search," not
"does not exist anywhere."

| Target | Stage-8 result | Evidence boundary / next action |
|---|---|---|
| `8965B4514000` CodeFlash | **not found** | exact identifier appears in docs/tooling only; no `.bin/.hex/.s19/.mot/.cuw` path hit, release asset, or fork artifact |
| Completed `4514000` partner DataFlash/CAN outputs | **not found** | Vance public-safe and English trees contain reports/tools/logs, but not the completed partner dump/capture corpus needed for independent replay |
| `8965F1208000` Corolla firmware | **not found** | exact public GitHub identifier search returns only this repository's analysis pages; firmware-static comparison remains blocked |
| Sienna EPS `.cuw` calibration | **not found** | no `4512000`/`4514000` `.cuw` path hit; public `T-0035-22.cuw` references remain documentation about a Tundra update, not a retained file |
| Same-vehicle protected-traffic producer firmware | **not found** | no newly surfaced camera/radar/PCS/ADAS image can be tied to the partner Sienna security domain |
| Physical producer of CAN `0x344` | **not identified** | no public artifact converts the inherited DBC logical node into physical-ECU proof; isolation/capture/producer firmware is still required |

## 5. `4514000` exception check

The Stage-8 handoff required immediate differential triage if
`8965B4514000` CodeFlash appeared. It did **not** appear, so no second Ghidra
program or speculative cross-calibration RE was started.

The existing differential checklist remains ready for the first real image:

1. image layout / split geometry;
2. bootloader similarity;
3. object-15 xrefs and restore path;
4. ICU-S command driver;
5. command-7 verification path;
6. DataFlash/NvM descriptor bank;
7. `0x344` receive/transmit profiles; and
8. runtime RAM mirrors.

## 6. Result

Stage 8 did not unblock a missing-firmware static-analysis project.

It did produce one durable evidence refinement: **MCU ID is now externally
corroborated as a required input to an official Toyota rekey request, but the
mapping `SafekeyNumber == MCU ID` remains unproved.** That distinction is pinned
and tested rather than left as a community-memory claim.

The remaining high-value acquisition queue is unchanged in priority:

1. `8965B4514000` CodeFlash;
2. completed partner `4514000` DataFlash/CAN artifacts;
3. `8965F1208000` CodeFlash;
4. matching Sienna EPS `.cuw`;
5. firmware from a same-vehicle protected-traffic producer / physical `0x344`
   source.
