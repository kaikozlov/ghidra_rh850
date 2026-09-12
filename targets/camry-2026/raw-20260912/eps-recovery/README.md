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
