---
name: timeline
description: Stage 11 of a research-analyst investigation. Merges every dated ledger record into one chronology of underlying events, company statements, public revelations and price reactions, showing what was publicly known at each point. Use after stages 1 to 10, or when a chronology of a disclosure story is needed.
---

# Timeline (stage 11)

One chronology built only from ledger records. Each row cites its record id.

| Column | Content |
|---|---|
| Date (time, time zone) | `public_at`; if the underlying event date differs, show both |
| What | One neutral line |
| Type | Event / Company statement / Revelation / Court / Regulator / Insider trade / Price reaction |
| Source | Ledger id → document link |
| Publicly known? | Whether this was public at that date (underlying events often were not) |

Rules:
- Price reactions (from stage 1) appear on the session they occurred, with abnormal return.
- Where an underlying event precedes a company statement on the same subject, mark the pair; these
  are the rows the memo's analysis section will point to.
- Show staged revelations: earlier partial disclosures and their price reactions.
- No row without a ledger record. No inferred dates: unknown dates are marked "date not established"
  and listed as a gap.
