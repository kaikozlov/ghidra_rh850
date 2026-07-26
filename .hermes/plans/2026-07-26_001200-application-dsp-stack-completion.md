# Application Dcm DSP Stack Completion Plan

> **For Hermes:** This is reverse-engineering work, not greenfield software. The
> TDD cycle here is: trace in Ghidra → extract instruction-level evidence → encode
> as a raw-byte `verify_*.py` assertion → document in `docs/`. Every finding must
> be machine-checked against the committed CodeFlash image.

**Goal:** Close the three remaining static-RE gaps in the Sienna application
diagnostic stack (null-callback DSP path, application SecurityAccess algorithm,
proprietary `0xAB` semantics), plus two reproducibility items (variant matrix,
Calvin reference pin).

**Architecture:** All analysis derives from the committed CodeFlash image
(`firmware/RH850_P1M-E_CodeFlash.bin`). Interactive decompilation uses the
`ghidra` CLI against `build/project/`. New findings land as (a) updated rows in
`data/application_diagnostic_map.csv` (via
`tools/generate_application_diagnostic_map.py`), (b) new or extended
`tests/verify_*.py` assertions, (c) doc updates in
`docs/APPLICATION_DIAGNOSTICS.md` or new docs, and (d) `AGENTS.md` verified-
findings entries.

**Tech Stack:** Ghidra 12.1.2 + vendored RH850 SLEIGH module; Python 3 verify
suites via `uv`/`make verify`; CSV data artifacts.

---

## Prerequisites

```bash
# 1. Firmware evidence suite must pass before starting
make verify

# 2. Working project must exist for interactive decompilation
make work-project   # if build/project/ is missing

# 3. Verify ghidra CLI resolves the RH850 language
source build/ghidra-processor.env  # or set JAVA_TOOL_OPTIONS
ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin stats
```

If `make verify` fails, stop and fix the regression before adding new work.

---

## Task Group A: Recover the null-callback Dcm DSP path

**This is the highest-leverage item.** SIDs `0x14/0x23/0x31/0x34/0x36/0x37/0xBA`
have valid service records and session policies but `w3 == 0` (null callback).
They route through generated AUTOSAR Dcm DSP indirection that this image does not
bind through the service-record callback word.

### Task A1: Map the shared service gate at `0x8F282`

**Objective:** Trace how a matched 24-byte service record with `w3 == 0` reaches
its DSP implementation. Establish the dispatch path from session-gate to DSP.

**Files:**
- Decompile: `0x8F282` (shared service gate), `0x8F202` (session check callee)
- Investigate: `ghidra/scripts/investigate/FindOperandRefs.java` (search for
  references to the null-callback record addresses)
- Output: findings notes (scratch)

**Steps:**

1. Open the working project and decompile `0x8F282`:
   ```bash
   ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
          --program RH850_P1M-E_CodeFlash.bin decompile 0x8F282
   ```

2. Trace the post-session-check path: after `0x8F202` succeeds (session is
   allowed), what does the gate do with `w3 == 0`? Look for:
   - TP-relative global service configuration pointers
   - SID-indexed dispatch (e.g. `switch` or table jump on the SID byte)
   - Calls to `0x8F202` return value consumption
   - Indirect calls whose target is loaded from a second table

3. Decompile `0x8F202` and understand the session allow-list enforcement. Confirm
   it returns success/failure and how the gate consumes that return.

4. Search for TP-relative config structures. Application `tp = 0x23EE4`. Look for
   `tp + offset` loads near the gate that could point to SID-indexed handler
   families or DSP tables.

5. **Checkpoint:** Document the gate's dispatch tree from matched record → DSP
   entry. Identify where `w3 == 0` diverges from `w3 != 0` (the callback path).

### Task A2: Trace the SID-indexed DSP handler families

**Objective:** Find the generated DSP dispatch tables for each service class
(memory, transfer, routine, proprietary).

**Steps:**

1. From A1's dispatch tree, identify the SID-indexed lookup. If it's a table,
   dump it. If it's a switch, use `RecoverSwitchTables.java` patterns.

2. For each null-callback SID, trace to its DSP entry point:
   - `0x14` (ClearDTC) → likely a DTC-clear DSP
   - `0x23` (ReadMemoryByAddress) → likely a memory-range-check + read DSP
   - `0x31` (RoutineControl) → must bind to the RID table at `0x25768`
   - `0x34/0x36/0x37` (download/transfer/exit) → likely the application-side
     download sequence DSP
   - `0xBA` (proprietary) → trace to its handler

3. For `0x31` specifically: the 32-entry RID table at `0x25768` is already
   recovered. Find the DSP path that parses `RID || subfunction` and looks up
   `start_cb`/`result_cb` from that table. This resolves the "SID-to-table
   binding" gap.

4. For `0x34/0x36/0x37`: trace the download/transfer/exit state machine. Look for
   memory-range tables, block counters, and the application-side equivalent of the
   bootloader payload gate. This may resolve the Corolla's observed `0x34` silent
   / `0x36`→NRC 0x7F / `0x37`→NRC 0x7F behavior.

5. **Checkpoint:** For each SID, document: `SID → parser → policy → worker →
   request format → response/NRC`.

### Task A3: Encode DSP findings as verify-test assertions

**Objective:** Lock the recovered DSP dispatch paths as machine-checked evidence.

**Files:**
- Modify: `tests/verify_application_diagnostics.py` (add DSP assertions)
- Modify: `tools/generate_application_diagnostic_map.py` (update evidence_status
  and notes for resolved SIDs)
- Regenerate: `data/application_diagnostic_map.csv`

**Steps:**

1. For each resolved SID, add assertions to
   `tests/verify_application_diagnostics.py` that check:
   - The DSP dispatch table address and entry count
   - The SID-to-DSP-entry mapping (instruction-level: e.g. `assert CF[addr:addr+4]
     == expected_dsp_ptr`)
   - Key instruction sequences (like the existing pattern in the test)

2. Update `tools/generate_application_diagnostic_map.py` `SEMANTICS` dict for
   resolved SIDs: change evidence_status from `config-only` to `recovered`,
   fill in `service_callback_role`, `async_worker`, `nrcs`, `side_effects`.

3. Regenerate the CSV:
   ```bash
   make generate-application-diagnostics
   ```

4. Run verification:
   ```bash
   make verify
   ```

### Task A4: Document the DSP path in APPLICATION_DIAGNOSTICS.md

**Files:**
- Modify: `docs/APPLICATION_DIAGNOSTICS.md` (new section after "Bounded negatives")

**Steps:**

1. Add a section "## Recovered DSP dispatch for null-callback SIDs" documenting:
   - The shared gate dispatch tree
   - Per-SID DSP paths with evidence grades
   - Updated bounded-negatives table (now resolved where traced)

2. Update the "Evidence grades" table at the end of the doc.

3. Update the per-SID behavior matrix (section 0) with recovered behavior.

---

## Task Group B: Finish application SecurityAccess algorithm

**The table is recovered; the crypto is not.** Need to trace seed source,
expected-key computation, attempt/delay storage, and what `0x900FC` changes.

### Task B1: Trace the request-seed worker `0x9497C`

**Objective:** Determine the 16-byte seed source: random, counter-derived,
session-derived, or transformed.

**Steps:**

1. Decompile `0x9497C` and trace the seed generation path:
   ```bash
   ghidra ... decompile 0x9497C
   ```

2. Identify where the 16-byte seed is sourced from. Look for:
   - RNG calls (hardware RNG peripheral or PRNG state)
   - Counter/nonce derivation from RAM
   - Session-state mixing
   - Transformation of a stored value

3. Identify where the seed is stored (for later key comparison) — likely a RAM
   slot near `0x26338`/`0x26350` config area.

4. **Checkpoint:** Document seed source, generation mechanism, and storage
   address.

### Task B2: Trace the send-key worker `0x94A72`

**Objective:** Recover the expected-key computation and compare mechanism.

**Steps:**

1. Decompile `0x94A72` and trace the key verification path.

2. Identify the expected-key computation:
   - Does it reuse the bootloader AES path (`SEED_KEY_SECRET`)?
   - Or a different algorithm/constants?
   - Is the tester-supplied 16-byte key stored or consumed-and-discarded?

3. Check if levels `01/02` (programming) and `03/04` (extended) use different
   algorithms, constants, or slots. The config slots at `0x26338`/`0x26350` may
   differ.

4. Trace the attempt-counter and delay-timer storage:
   - Where is the attempt count stored? RAM-only or NvM-persisted?
   - Where is the delay lockout timer?
   - What are the thresholds for NRC `0x36` (exceededNumberOfAttempts) and
     `0x37` (requiredTimeDelayNotExpired)?

5. **Checkpoint:** Document expected-key algorithm, comparison flow, attempt/delay
   storage.

### Task B3: Trace the unlock helper `0x900FC`

**Objective:** Determine what a successful unlock changes in the security state.

**Steps:**

1. Decompile `0x900FC` and trace the state mutation:
   - What security-state byte/word is set?
   - Where is it stored (RAM address)?
   - Does it affect DID access (RDBI/WDBI security check at `0x92FEE`)?
   - Does it affect routine access (`0x31`/`AB`)?
   - Does level-2 unlock (`03/04`) grant different access than level-1
    (`01/02`)?

2. Trace how `0x92FEE` (per-DID security check) reads the unlock state. Confirm
   whether a successful level-2 unlock changes the accessible DID set.

3. **Checkpoint:** Document the unlock state model and its downstream effects.

### Task B4: Encode SA findings as verify-test assertions

**Files:**
- Modify: `tests/verify_application_diagnostics.py` (add SA algorithm assertions)
- Modify: `tools/generate_application_diagnostic_map.py` (update SID 0x27 row)

**Steps:**

1. Add assertions for seed storage address, expected-key comparison instructions,
   attempt-counter address, delay-timer address, and unlock-state address.

2. Update the SID `0x27` row in the generator with recovered algorithm details.

3. Regenerate CSV and run `make verify`.

### Task B5: Document application SA in APPLICATION_DIAGNOSTICS.md

**Files:**
- Modify: `docs/APPLICATION_DIAGNOSTICS.md` (expand "SecurityAccess (0x27)" section)

**Steps:**

1. Expand the SA section with: seed source, expected-key algorithm, attempt/delay
   model, unlock state effects.

2. Update the Corolla comparison table: the Corolla's `0x03/0x04` pair is now
   comparable to this application-level SA, not just the bootloader.

3. Update evidence grades.

---

## Task Group C: Finish proprietary `0xAB` semantics

**Structurally recovered but semantically opaque.** Wire format, typed structure,
subfunction meanings, and RID selection are unknown.

### Task C1: Trace the AB callback chain `0x8D344`

**Objective:** Decode the wire request format and field layout per subfunction.

**Steps:**

1. Decompile the full chain:
   ```bash
   ghidra ... decompile 0x8D344   # callback entry
   ghidra ... decompile 0x8D2B2   # main worker
   ghidra ... decompile 0x8D3CC   # routine lookup
   ghidra ... decompile 0x96918   # lower worker
   ghidra ... decompile 0x968A6   # lower worker alt
   ```

2. For the callback `0x8D344` at phase 0:
   - Determine exact wire request length check (what NRC `0x13` threshold?)
   - Decode the request-mirror copy into `0xFEBF48EC`: what bytes map to what
     fields?
   - Type the structure at `0xFEBF48EC` (+0x50 secondary at `0xFEBF493C`)

3. For the routine lookup `0x8D3CC`:
   - It scans entries `0..12` of the RID table at `0x25768`.
   - What field in the request selects the RID? (byte index + value)
   - What are RIDs `0x204` through the 12th entry?

4. **Checkpoint:** Document the typed request structure and RID selection
   mechanism.

### Task C2: Decode the three subfunctions (`01/02/03`)

**Objective:** Determine what each subfunction does.

**Steps:**

1. Decompile each subfunction wrapper:
   ```bash
   ghidra ... decompile 0x96A34   # subfn 01
   ghidra ... decompile 0x96A56   # subfn 02
   ghidra ... decompile 0x96A78   # subfn 03
   ```

2. For each subfunction, determine:
   - Operation type (start routine, request result, stop routine?)
   - Selected RID range
   - Operation phases and side effects
   - Response format (including the "vendor byte" returned by the worker)
   - Possible NRCs

3. Determine whether this is:
   - A manufacturing/calibration service
   - An event/routine wrapper
   - A tester orchestration service
   - Something else entirely

4. **Checkpoint:** Build the completion table:
   ```
   subfunction | accepted request shape | selected RID range | operation phases
               | side effects | positive response shape | possible NRCs | evidence grade
   ```

### Task C3: Investigate the secondary `0x7A0 → 0x7A8` endpoint

**Objective:** Understand why `AB` is also exposed on the secondary physical
endpoint (service group 4).

**Steps:**

1. The service group directory at `0x25E1C` maps group 4 (five entries `18..22`)
   to secondary physical `0x7A0` → response `0x7A8`, with SID set
   `10,19,22,3E,AB`.

2. The five extra records at `0x25FC8..0x26057` supply group 4's records.
   Decompile the `AB` record in group 4 and compare to the primary `AB` record
   at `0x25F98`. Are they the same callback? Different subfunction policy?

3. Determine the intended role: is `0x7A0` a manufacturing/diagnostic port, a
   secondary tester interface, or something else?

### Task C4: Encode AB findings as verify-test assertions

**Files:**
- Modify: `tests/verify_application_diagnostics.py`
- Modify: `tools/generate_application_diagnostic_map.py` (update SID 0xAB row)

**Steps:**

1. Add assertions for request length checks, typed structure offsets, RID
   selection mechanism, and subfunction dispatch.

2. Update the SID `0xAB` row: change evidence_status from `structural-recovered`
   to `recovered` (or `partial` if some aspects remain opaque).

3. Regenerate CSV and run `make verify`.

### Task C5: Document AB semantics

**Files:**
- Modify: `docs/APPLICATION_DIAGNOSTICS.md` (expand "Proprietary AB/BA" section)

**Steps:**

1. Expand with: typed request structure, subfunction table, RID selection,
   response format, secondary endpoint role.

2. Update evidence grades.

---

## Task Group D: Variant matrix and Calvin reference pin

**Two reproducibility items. No firmware analysis required.**

### Task D1: Create the TSS 3 EPS variant matrix

**Objective:** Consolidate Sienna/Corolla/Camry/etc. findings into a structured
comparison artifact.

**Files:**
- Create: `data/tss3_eps_variant_matrix.csv`

**Steps:**

1. Create the CSV with the fields from the other session's recommendation:
   ```text
   vehicle,eps_part_number,application_software_id,secondary_software_id,
   diagnostic_bus,physical_request,physical_response,functional_request,
   secondary_request,application_sid_set,application_dids,security_levels,
   programming_observation,bootloader_f181_observed,bootloader_dids,
   bootloader_routines,secoc_sync_id,secured_can_ids,mcu,
   firmware_available,evidence_grade,source
   ```

2. Populate the Sienna row from existing verified findings (definitive fields
   only; leave unknowns as `unknown`).

3. Populate the Corolla row from the field observations in
   `docs/APPLICATION_DIAGNOSTICS.md` section 6 (Corolla comparison table).

4. Leave other TSS 3 variants (Camry, RAV4 Prime, etc.) as placeholder rows with
   `evidence_grade=none` — do not fabricate observations.

### Task D2: Update the Calvin reference pin

**Objective:** Pin Calvin's report commit and add the Corolla investigation
artifact.

**Files:**
- Modify: `external-references.lock.json`

**Steps:**

1. Verify the report commit exists:
   ```bash
   git ls-remote https://github.com/calvinpark/openpilot.git | grep eeb87f4
   ```

2. Download `tsk/COROLLA_INVESTIGATION.md` at that commit and compute SHA-256:
   ```bash
   curl -sL "https://raw.githubusercontent.com/calvinpark/openpilot/eeb87f4f9cbcba2ee9c358c8d93015a513c1f822/tsk/COROLLA_INVESTIGATION.md" | sha256sum
   ```

3. Update `external-references.lock.json`:
   - Change `calvinpark_openpilot.commit` to
     `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822`
   - Add artifact entry for `tsk/COROLLA_INVESTIGATION.md` with its SHA-256

4. Update `tests/verify_external_corroboration.py` if it checks the Calvin
   commit hash.

5. Run `make verify-external EXTERNAL_REPOS_DIR=...` if external repos are
   checked out, otherwise at least `make verify`.

### Task D3: Update AGENTS.md and docs cross-references

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md` (if it references the variant matrix or Calvin commit)

**Steps:**

1. Add verified-findings entries for any new docs/tests from groups A-C.

2. Reference `data/tss3_eps_variant_matrix.csv` in the data artifacts list.

3. Update the external-reference note about Calvin's report commit.

---

## Verification (after all groups)

```bash
# Full firmware evidence suite
make verify

# Processor + SLEIGH (if any processor changes — unlikely for this work)
make verify-sleigh
make verify-processor

# External corroboration (if repos checked out)
make verify-external EXTERNAL_REPOS_DIR=...

# Interactive spot-check against the working project
ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin decompile <newly_resolved_addr>
```

All `verify_*.py` suites must pass. No new doc claim should appear without a
corresponding assertion.

---

## Risks and open questions

1. **DSP path may be truly generated/untraceable.** AUTOSAR-generated Dcm code
   can use heavy indirection (function pointer arrays, TP-relative config
   structs). If the dispatch is fully data-driven with no static pointers, we may
   only recover the table addresses, not the handler semantics. In that case,
   document the table structure and mark handlers as `config-table-recovered`
   rather than `recovered`.

2. **Application SA may reuse a hardware crypto accelerator (ICU-S).** The
   bootloader uses software AES. The application path might use the RH850 ICU-S
   hardware crypto. If so, the expected-key computation may be an opaque
   hardware-call boundary — document the call interface but mark the internal
   algorithm as `hardware-mediated`.

3. **AB subfunctions may require dynamic state.** If the subfunction behavior
   depends on runtime RAM state (e.g., current vehicle mode), static analysis
   can only recover the dispatch, not the conditional behavior. Document the
   dispatch and mark conditionals as `state-dependent-unresolved`.

4. **Corolla firmware is still unavailable.** Item 5 (structural pipeline on
   `8965F1208000`) remains blocked. This plan does not attempt it. The variant
   matrix (D1) makes the gap explicit instead of leaving it as disconnected prose.

5. **Ghidra daemon durability.** All interactive decompilation must end with
   `ghidra ... stop` before any `git add`/`make snapshot-project`. See AGENTS.md
   "The ghidra CLI is a persistent daemon" section.
