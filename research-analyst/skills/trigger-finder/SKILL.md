---
name: trigger-finder
description: Stage 2 of a research-analyst investigation. Establishes exactly what adverse information reached the market around a stock drop, when (to the minute where possible), from whom, through which channel, and what competing explanations existed. Use after market-event, or whenever the cause and timing of a drop must be pinned down.
---

# Trigger finder (stage 2)

Question: what specific information reached the market, when, and from whom? The news need not come
from the company.

## Window

From 5 sessions before day 0 to the close of day 1. Extend back if pre-event drift (stage 1) is
large: information may have leaked or emerged in stages.

## Sweep (one channel per search; record each as a `search` record)

Adapted from Bigdata.com `company-brief` (six-category sweep with mandatory litigation query) and
`catalyst-monitor` (regulatory and legal queries).

| Channel | Where |
|---|---|
| Company announcements | US: EDGAR filings in the window (8-K items, 10-Q/10-K, NT filings, 6-K). Other countries: announcement archives in `references/source-hierarchy.md` |
| Earnings call | Bigdata.com transcripts dated in the window |
| News | Bigdata.com news, entity filter, window; then specific queries per candidate cause |
| Courts | CourtListener dockets with the company as party, entries in the window |
| Regulators | SEC/DOJ releases (US), provincial commissions, FCA, BaFin; Bigdata.com news "regulator" queries |
| Short sellers | Bigdata.com news and open web: "<Company> short report" in the window |
| Analysts | Bigdata.com news/research: downgrades in the window that cite new facts |
| Sector / group | Peers' and correlated group's news on day 0 (from stage 1) |

## For each candidate trigger, record a `revelation`

- Exact headline or passage quoted, `public_at` with time and time zone, channel and speaker.
- Primary document behind any news report (fetch it; cite it).
- Whether the item was the first public appearance of the information, or a repeat.

## Attribution (competing hypotheses, from intel `intel-diagnose`)

Write one `alternative` record per explanation: company-specific news (each candidate separately),
sector/group move, market move, mechanical effect, confounding company news released at the same
time (e.g. results plus a CEO exit). For each: supporting evidence ids, undercutting evidence ids,
weight. The trigger is the explanation the evidence best fits, timed to the price reaction (stage 1
day-0 and intraday timing if available). Say plainly when the evidence does not separate two
candidates.

## Tier

Assign the tier from `references/trigger-tiers.md` and record it on the main `revelation`.
