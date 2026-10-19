---
name: market-event
description: Stage 1 of a research-analyst investigation. Measures a stock drop against its market, peers and correlated group, finds other large company-specific drops in the lookback period, and writes the numbers to the case ledger. Use at the start of an investigation or whenever a price, volume or market-value figure is needed.
---

# Market event (stage 1)

All numbers come from `scripts/market_event.py`. Read its JSON; never recompute by hand.

## Steps

1. **Day 0 confirmation.** Run the script for the ticker and date. If the trigger (stage 2) later
   shows the news came after the close, re-run with the next session as day 0 and supersede the
   records.
2. **Write `market` records** for: close, previous close, return, market return, peer return,
   expected return, abnormal return, t-statistic, two-day abnormal return, pre-event drift, rebound
   (when available), volume ratio, market value lost (local currency; state the currency and that it
   is computed from the scanner's market cap). Each record cites the script output by JSON path.
3. **Read the flags** and record each as a `market` or `gap` record (thin trading, OTC, dividend
   effect, short history, correlated group, scanner/feed mismatch).
4. **Earlier drops on the same story.** Run the script over the lookback period (default 2 years,
   max 3) for every session where the stock fell ≥ 5%, and list those that classify as
   company-specific or borderline. Each becomes an `event` record; stage 2 checks whether any relate
   to the same subject (staged revelation).
5. **Recovery.** If the 5-day rebound is large, record it; a full recovery is relevant context.

## What this stage does not do

It does not estimate investor losses or damages. Market value lost on the day is an observed
figure, labelled as such. Loss attribution is the lawyer's work.
