# Status ledgers

This directory answers five different questions. It is intentionally separate
from dated investigation journals, which live under
[../history/](../history/README.md).

| Question | Document |
|---|---|
| **What should we do next?** | [PRIORITIES.md](PRIORITIES.md) |
| **Is this claim actually established?** | [FINDINGS.md](FINDINGS.md) |
| **What remains unresolved?** | [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) |
| **How complete was the Sienna analysis?** | [ANALYSIS_STATUS.md](ANALYSIS_STATUS.md) (2026-08-15 snapshot, not a live dashboard) |
| **What did we previously get wrong?** | [CORRECTIONS.md](CORRECTIONS.md) |
| **Where did we record a prior lead/finding?** | `tools/know QUERY` |

## Reading order

Read [PRIORITIES.md](PRIORITIES.md) first for current work; follow its links
into subsystem reports or [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) when working a
specific item. These ledgers are navigation aids. Canonical truth for any claim
is its subsystem/variant report — and for firmware questions, the bytes
themselves (source-of-truth hierarchy in [../../AGENTS.md](../../AGENTS.md)).

## Maintenance

These files are historical/navigation aids, **not** a transaction log and **not**
a completeness requirement — see the documentation section of
[../../AGENTS.md](../../AGENTS.md). In particular:

- Do **not** stop active work to add a FINDINGS row, CORRECTIONS row,
  verification owner, or cross-reference footer. Write conclusions in the
  canonical subsystem/variant report; batch ledger cleanup at meaningful
  milestones only if it adds value.
- New work does not need an OQ entry before it can proceed, and resolving a
  question does not require a FINDINGS/CORRECTIONS bookkeeping transaction.
- **No freshness or completeness guarantee.** These pages are updated when
  someone maintains them, not continuously. Verify against the canonical
  reports and `tools/know QUERY` before relying on a ledger statement as
  current.
- Completed investigation narratives belong under `docs/history/YYYY-MM/`, not
  here; [PRIORITIES.md](PRIORITIES.md) holds only the current queue and must
  not grow a completion diary.
