---
description: Layer 1 triage of today's falls of more than 10% under Andrew's trigger (screens TradingView itself, or takes a screener table)
argument-hint: [path to screener output or pasted table] [date YYYY-MM-DD]
---

Run Layer 1 of the research-analyst workflow on: $ARGUMENTS

1. **No screener table given:** run Andrew's screen yourself:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/screener.py"
   ```
   It always screens the **last trading session that closed before today** (Monday's run screens Friday)
   and writes `runs/<session date>/screener.md` (the names meeting the trigger), `screener_outside.md`
   (every other 10%+ fall, with the reason) and `screener.json`. `<date>` below is that session date.
   **A table was given:** save it to `runs/<date>/screener.md` (copy rows exactly; do not edit them). If the
   date is not given, it is the trading day the screener ran for; confirm it from the script output's day 0.
2. Follow the `triage` skill exactly, under the rules of the `research-analyst` skill. Carry the screener's
   flags (stale secondary quote, thin volume, cap between C$200M and C$250M) into each row.
3. Write `runs/<date>/triage.md` and `runs/<date>/triage_ledger.jsonl`.
4. Reply with the counts (Full investigation / Watch / Exclude), the Full-investigation names with
   one line each, and the path to the file.
