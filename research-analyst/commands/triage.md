---
description: Layer 1 triage of a day's screener output (stocks down 10%+ in Canada, US, UK, Germany)
argument-hint: <path to screener output or pasted table> [date YYYY-MM-DD]
---

Run Layer 1 of the research-analyst workflow on: $ARGUMENTS

1. Save the screener table to `runs/<date>/screener.md` (copy rows exactly; do not edit them).
   If the date is not given, it is the trading day the screener ran for; confirm it from the
   script output's day 0.
2. Follow the `triage` skill exactly, under the rules of the `research-analyst` skill.
3. Write `runs/<date>/triage.md` and `runs/<date>/triage_ledger.jsonl`.
4. Reply with the counts (Full investigation / Watch / Exclude), the Full-investigation names with
   one line each, and the path to the file.
