---
description: Just the list: stocks that fell more than 10% in the last closed trading session and meet Andrew's trigger (no triage, no searches)
argument-hint: (none)
---

Produce the candidate list only. Do not triage, search or investigate.

1. Once per session: `bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh"`.
2. Run:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/screener.py"
   ```
   It screens the last trading session that closed before today (a Monday run screens Friday) and writes
   `runs/<session date>/screener.md`, `screener_outside.md` and `screener.json`.
3. Reply with:
   - the session date screened
   - the candidates from `screener.md` as a table: company, ticker, drop %, market cap before the drop
     (C$M), flags. Clean names first, then the ones flagged "likely a stale secondary quote" under a
     separate heading, since their main listing barely moved
   - one line with the number of other 10%+ falls outside the trigger, and the path to `screener_outside.md`
4. End by offering `/triage` on the list, or `/investigate <EXCH:TICKER> <date>` on one name.
