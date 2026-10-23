# Drop standard

Implemented in `scripts/market_event.py`. The model reads its output; it never recomputes by hand.

## Why

A raw 10% fall means little alone:
- A stock down 11% while its sector is down 8% had a sector day.
- A stock down 11% while its sector is down 2% had a company day.
- A stock that routinely moves 6% a day needs a much bigger fall to mean anything.
- Some industries move as a group the classification misses (crypto miners on bitcoin, AI
  infrastructure, quantum computing), so a theme factor is added from a fixed list of theme ETFs.

## Calculation

1. **Day 0** is the session in which the price reacted. News released after the close or before the
   open belongs to the next session (exchange time zone).
2. **Benchmarks.**
   - Market: S&P 500 (US), S&P/TSX Composite (Canada), FTSE All-Share (UK), HDAX (Germany).
   - Peers: equal-weighted index of the 10 largest same-industry, same-market primary listings
     (TradingView industry classification, OTC excluded, the company itself excluded). If the
     industry has fewer than 3 other listings in the market (e.g. UK wireless telecoms), the 10
     largest same-sector listings are used instead, flagged. If fewer than 3 peer series have
     prices, the peer factor is dropped and the model uses market (+ theme) only, flagged.
3. **Normal behaviour.** Regress the stock's daily returns on market, peer (and theme) returns over 120
   trading days ending 10 days before day 0, leaving out days with ≥10% moves.
4. **Theme factor.** From a fixed list of theme ETFs (bitcoin, biotech, semiconductors, software,
   cloud, speculative growth, US small caps, quantum/AI computing, robotics/AI, solar, batteries,
   uranium, gold miners, energy, metals and mining, regional banks, retail, aerospace and defense),
   pick the one the stock tracked most closely over the estimation window; if its correlation is
   ≥ 0.4, add it to the regression. The list is fixed in advance, so it is never chosen by outcome.
5. **Abnormal return (AR)** = actual return − expected return. **t** = AR ÷ standard deviation of
   the regression's unexplained moves.
6. **Screen context (not used in the calculation).** Count the other stocks on the same screen that
   usually move with this one (correlation ≥ 0.5). Every screened stock fell 10%+, so this group is
   selected on the outcome and would always "explain" the fall; it is reported only as a hint that
   several names may share one piece of news.
7. **Also reported:** AR on day −1 and day +1, two-day AR (days 0–1), pre-event drift (days −5 to −1), rebound (days 1–5),
   volume ÷ 30-day average, market value lost, dividend effect, thin trading, OTC status.

**Market value lost** = scanner market cap ÷ scanner close (the share count) × the day-0 price
change on the split-adjusted series, in the currency of the market cap (`market_cap_currency`; GBP
for LSE names quoted in pence). It is an observed figure, never an estimate of investor loss.

**Incomplete data.** A bar for a session that has not closed yet is ignored (and never cached), so
a run during market hours measures the last completed session. Windows that reach past the latest
completed session (day +1, two-day AR, rebound) are reported as empty, never as a partial sum;
re-run once they have traded.

Prices come from the TradingView chart feed (dividend-adjusted and split-adjusted series; the
split-only series is used to detect dividend effects). Classification data comes from the
TradingView scanner. Both are cached in `.cache/` per day.

## Classes (v1 defaults; calibrate on past cases with `scripts/calibrate.py cases.csv`)

| Class | Rule |
|---|---|
| Company-specific | AR ≤ −7% and t ≤ −2.58 |
| Borderline | AR ≤ −5% and t ≤ −1.96, but not Company-specific |
| Borderline (short history) | Fewer than 60 usable days (recent listing or sparse trading); AR vs peers ≤ −5% |
| Not company-specific | Otherwise |

## Overrides the model applies when reading the output

- **Bellwether.** If this company's own news moved the sector (peers fell because of it), the peer
  adjustment understates the drop. Check the trigger before excluding.
- **Industry revelation naming the company.** Keep as Borderline even when peers fell too.
- **Two-day fall.** If news straddled two sessions, judge on the two-day AR.
- **Thin trading / OTC.** Treat the price signal as unreliable; a one-trade print can produce any
  percentage. Note it rather than rely on it.
- **Dividend effect.** If the unadjusted and adjusted returns differ, part of the fall is an
  ex-dividend adjustment, not news.
