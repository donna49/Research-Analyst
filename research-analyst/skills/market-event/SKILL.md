---
name: market-event
description: Stage 1 of a research-analyst investigation. Measures a stock drop against its market, peers and correlated group, finds other large company-specific drops in the lookback period, and writes the numbers to the case ledger. Use at the start of an investigation or whenever a price, volume or market-value figure is needed.
---

# Market event (stage 1)

All numbers come from `scripts/market_event.py`. Read its JSON; never recompute by hand.

## Steps

1. **Day 0 confirmation.** Run the script for the ticker and date:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/market_event.py" EXCH:TICKER --date <date> --json runs/<date>/<TICKER>/market_event.json > runs/<date>/<TICKER>/market_event.md`.
   If the trigger (stage 2) later shows the news came after the close, re-run with the next session
   as day 0 and supersede the records.
2. **Write `market` records** with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" add-market runs/<date>/<TICKER>/ledger.jsonl
   runs/<date>/<TICKER>/market_event.json`. It appends one record per figure (close, previous
   close, return, market, peer and theme returns, expected and abnormal return, t, abnormal return
   on days −1 and +1, two-day abnormal return, pre-event drift, rebound, volume ratio, market value
   lost), the class and every flag, each with `event_at` = day 0 and the JSON path. Never type
   these numbers by hand. Running it again adds only what is new.
3. **Read the flags** (now in the ledger) and add a `gap` record where a flag leaves something
   unsettled (thin trading, OTC, dividend effect, short history, no peer index, correlated group,
   scanner/feed mismatch).
4. **Windows that have not closed yet.** Two-day abnormal return, day +1 and the 5-day rebound are
   empty until every session in the window has traded (the script never sums part of a window, and
   ignores a bar still in progress). Re-run after day +1 / day +5 and add the new records.
5. **Earlier drops on the same story.** Run the script over the lookback period (default 2 years,
   max 3; `--lookback 730 --date <date> --json runs/<date>/<TICKER>/lookback.json`) for every
   session where the stock fell ≥ 5%, and list those that classify as
   company-specific or borderline. Each becomes an `event` record; stage 2 checks whether any relate
   to the same subject (staged revelation).
6. **Recovery.** If the 5-day rebound is large, record it; a full recovery is relevant context.

## What this stage does not do

It does not estimate investor losses or damages. Market value lost on the day is an observed
figure, labelled as such. Loss attribution is the lawyer's work.
