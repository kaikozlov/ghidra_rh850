# Offline EPS recovery liveness observation, 2026-09-12

`saved-log-liveness.json` is a **derived, privacy-minimized observation summary**,
not raw CAN and not a fresh vehicle capture. Its `files` entries identify the
39 retained September-11 post-incident rlogs and one September-4 positive control.
The original rlogs remain under `/Users/kai/dev/inspect/logs/camry-2026`; they
are not duplicated here. One input contains corrupted events, explicitly recorded
in its `parse_warnings`. All other inputs parsed without reported warnings.

Reproduce with `tools/targets/camry/analysis/analyze_camry_eps_recovery_liveness.py`
using `--openpilot-root`, `--output`, and the existing local input paths from the
JSON. The reducer refuses nonexistent/nonlocal input files and imports the
local openpilot LogReader. It never creates a Panda/UDS connection. Counts use
raw CAN events, distinguish native sources from echoes/rejected returns and
`sendcan`, and preserve per-file observations rather than inferring health from
openpilot's CarState flags.

Interpretation and limitations are in §13 of
`docs/variants/camry-f33-eps-recovery-2026-09-11.md`.


The regenerated report records `logger_build` from each producer's `initData`.
The three retained post-incident revisions do not record per-frame FDF/BRS in
their CAN schema. The report does not infer short-frame wire format from payload
length or from the defaults of a different reader schema. This limitation and
the exact bootloader mode-register check are recorded in §14 of the recovery
report. All original source counts, CAN spans and corruption warnings were
checked unchanged when the metadata was added.

The synthetic `tools/test camry_eps_recovery_liveness` suite checks counting
and metadata/timing behavior without loading any private rlog or opening any
vehicle interface.


`gateway-preparation-observation.json` is the separate offline census of the
OEM shared gateway address in the same 39 post-incident files. It distinguishes
logged native frames, echoes/mirrors, and sendcan; its 184 selected records are
not 184 unique wire transmissions. All 36 shared 750/758 records belong to
extensions 0F or 6D, not 5F. The partial coverage does not prove no preparation
was attempted outside these logs. The artifact also retains the matching
current CUW source identities and the optional F181 read's decoded C++
exception-table witness. These facts establish neither a live gateway type nor
a working EPS recovery path.

`reproduce_gateway_observation.py` is a historical offline extractor using the
local input paths in `saved-log-liveness.json` and the same local openpilot
LogReader. Run it with the existing openpilot Python environment. It writes
only `build/work/f33-network-gateway-20260912/reproduced-saved-gateway-observation.json`;
it does not overwrite the curated interpretation, send network traffic, or
contact a Panda. Counts, message summaries, and per-file warnings were compared
identically on a second run. Interpretation is in §18 of
`docs/variants/camry-f33-recovery-exception-followup.md`.
