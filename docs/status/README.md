# Live status

This directory answers five different questions. It is intentionally separate
from dated investigation journals, which live under [../history/](../history/README.md).

| Question | Document |
|---|---|
| **What should we do next?** | [PRIORITIES.md](PRIORITIES.md) |
| **Is this claim actually established?** | [FINDINGS.md](FINDINGS.md) |
| **What remains unresolved?** | [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) |
| **How complete is the analysis?** | [ANALYSIS_STATUS.md](ANALYSIS_STATUS.md) |
| **What did we previously get wrong?** | [CORRECTIONS.md](CORRECTIONS.md) |

## Reading order

For normal project work, read `PRIORITIES.md` first. It is deliberately short
and should stay that way. Follow its links into subsystem reports or
`OPEN_QUESTIONS.md` only when working a specific item.

`FINDINGS.md`, `OPEN_QUESTIONS.md`, and `CORRECTIONS.md` are exhaustive ledgers.
They are reference documents, not onboarding narratives.

## Maintenance contract

- Resolved question → remove it from `OPEN_QUESTIONS.md`, add/update its
  `FINDINGS.md` row, and update the canonical subsystem report.
- Superseded claim → record why in `CORRECTIONS.md`.
- New immediate work → add to `PRIORITIES.md` only if it changes the near-term
  execution order.
- Completed investigation narrative → archive under `docs/history/YYYY-MM/`;
  do not leave dated journals in this live directory.
- Coverage denominator changes → update `ANALYSIS_STATUS.md` and its verification
  gate.
