---
description: Layer 2 investigation of one stock drop, ending in a memo in Andrew Morganti's own form
argument-hint: <EXCH:TICKER> <drop date YYYY-MM-DD>
---

Run Layer 2 of the research-analyst workflow on: $ARGUMENTS

Read `references/andrew-method.md` first. Begin with Andrew's own seven-step review (`first-review`
skill: trigger, SEDAR+ profile, drop-date records, the 1–3 key facts, a year of MD&As, the language
change, call transcripts, price and volume history). It seeds the stages below. Then follow the
`research-analyst` skill's stage order:
1. market-event
2. trigger-finder
3. disclosure-history, issue and case type. **Checkpoint 1: stop and ask the user to confirm.**
4. disclosure-history, total mix and drift tables
5. knowledge-indicators, external-evidence and parties-and-capital (these can run in parallel)
6. case-economics
7. claim-framing. **Checkpoint 2: show the decision, reasons and deal-sheet figures; wait for the user.**
8. timeline
9. verify
10. memo-writer

If a ledger already exists for the case, resume from the first stage whose records are missing.
Use the early exit (orchestrator skill) when the economics show Andrew would pass on size or price
recovery.

Write everything under `runs/<date>/<TICKER>/`. Before replying, run:
- `python3 scripts/ledger.py check` on the ledger
- `python3 scripts/ledger.py quotes` on the ledger
- `python3 scripts/ledger.py memo` on the ledger and the memo

Then reply with:
- the recommendation
- the three to five records it rests on
- the deal-sheet figures
- the nearest limitation date
- the open questions
- the path to `memo.md`
