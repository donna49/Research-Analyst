---
description: Layer 2 full investigation of one stock drop, producing the evidence ledger and research memo
argument-hint: <EXCH:TICKER> <drop date YYYY-MM-DD>
---

Run Layer 2 of the research-analyst workflow on: $ARGUMENTS

Follow the `research-analyst` skill's stage order: market-event → trigger-finder →
disclosure-history (stop after the issue definition and ask the user to confirm it) →
knowledge-indicators and external-evidence → timeline → verify → memo-writer.

Write everything under `runs/<date>/<TICKER>/`. Run `python3 scripts/ledger.py check` and
`python3 scripts/ledger.py quotes` on the ledger before writing the memo; fix every problem or move
it to gaps. After writing it, `python3 scripts/ledger.py memo <ledger> <memo.md>` must report 0
problems. If the ledger already has records, resume from the first stage whose records are
missing (`python3 scripts/ledger.py summary <ledger>`). Reply with the conclusion-scale value, the three to five records it rests on, the open
questions, and the path to `memo.md`.
