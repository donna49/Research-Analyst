# Case economics: formulas

All of these numbers come from `scripts/economics.py`. This file formalizes the rules of thumb in
Andrew's memos and fixes the arithmetic slips the corpus shows. Present the results as rough
ranges for an internal decision, never as an expert opinion. Every memo says: "rough estimates for
screening; a damages expert (e.g. Gregg Edwards, CE Financial) would be retained before
issuing."

## Inputs (each tied to a ledger record)

| Input | Source |
|---|---|
| Trading venues (symbol, currency) | Stage 1 and the issuer profile (`parties-and-capital`) |
| Class Period start | Date of the first impugned document (`claim-framing`) |
| Corrections (dates; storm warning or correction) | Stage 2 `revelation` records |
| Shares outstanding per equity class | AIF / MD&A / 10-Q cover / OSC Form 13-502F1 (`party` or `capital` record) |
| Retention fractions | Default 0.25 / 0.40 / 0.50 (see below) |
| D&O insurance, cash | AIF / circular / balance sheet records |

## Price reaction for each correction
- `prev_close`: the close of the session before day 0. `close0`: the close on day 0. Day 0 is the first
  session after the information became public.
- `drop_per_share` = prev_close − close0. `drop_pct` = close0 / prev_close − 1.
- `lookback_avg_10d`: mean close over the 10 sessions starting at day 0, i.e. the s. 138.5
  "ten-day look-back". `lookback_vwap_10d` is the same window weighted by volume.
- `volume_ratio`: day-0 volume ÷ mean volume of the previous 30 sessions.
- The abnormal return and t-statistic come from `market_event.py` (stage 1). Report both the raw
  and the abnormal figure; Andrew's memos quote raw prices.

## Damaged shares (the "40% damages analysis")

His flow chart (step 11) states the rule: "Common law is, generally, equal to 40% of the Class Period
trading volume x the drop in price on date of the release of the public correction up to the following
10-days." For the statutory cap: "5% of the company's market capitalization measured at the time of the
release of each impugned document during the proposed Class Period." Pass `impugned_dates` to compute
the cap at each impugned document.

In Ascot he wrote "Class Period Volume (TSX, only): 123M / 40% damages analysis: 49M", then "Basic
Math Statutory Damages: $12.25M". That is 49M shares × the $0.25 per-share drop.

- `class_volume[venue]` = the sum of daily volume from the Class Period start to the session before
  the final correction's day 0.
- `damaged_shares` = class_volume × retention. The default range is 0.25 / **0.40** / 0.50.
- **Why 0.40:** a share can trade many times while only one holder at the correction is damaged, and
  intraday traders and market makers do not hold. The Aurora memo cites a NERA working paper (Oct
  2000) estimating about 50% of volume as market-maker or intraday trading. 0.40 is his working
  figure. 0.25 and 0.50 bracket it.
- Volume is split by venue (TSX vs US vs Frankfurt vs ASX). This shows how much of the class trades in
  each forum, which decided Paladin (4M vs 219M shares).

## Per-share inflation, three measures (shown side by side)
The Class Period is split into segments at each correction. Shares bought before correction *j*
bear the drops from *j* onward. Each measure below is volume-weighted across the segments.
1. **Day-0 drop** (his "basic math"): the sum of the day-0 drops from correction *j* onward.
2. **Statutory (s. 138.5-style):** the close before correction *j* − the 10-day look-back average after
   the final correction.
3. **Upper bound:** the segment's volume-weighted average close − the final 10-day look-back average.

The script reports both the 10-day look-back **average** and the **close on the 10th session**.
Andrew quotes the 10th-session close ("By July 30, 2024, the ten-day look-back, GLO's share price on
the TSX was at $1.29"). The statute uses the average trading price. Give both in the memo, and say
which one the damages use.

## Damages ranges
- `common_law_rough` = damaged_shares × measure 2, using the middle retention, with a low–high range
  across the three retentions and measures 1–2.
- `statutory_capped` = min(common_law_rough, liability_cap).
- Primary-market claims (s. 130) are listed separately: offering price − 10-day look-back, × the
  shares sold in the offering. They are never added silently into the secondary-market total.
- Currencies are never mixed. Each venue is computed in its own currency. Any combined total states
  the FX rate used and the record behind it.

## Liability cap (OSA s. 138.7; Ont. Reg. 1015 s. 249)
- Market capitalization = for each listed equity class, the shares outstanding (averaged over the
  10 trading days before the first impugned document, or the nearest reported figure, flagged) × the
  mean close on the principal market over those 10 days. Add the fair market value of unlisted classes
  if supplied.
- Cap = max(5% × market capitalization, $1,000,000). The $1M floor is not from the corpus; confirm
  it in the statute. Report the market capitalization and the cap with the date window used.
- HEXO's expert included warrants and options. Flag whether they are included.

## Settlement target
- Andrew's observed ratios:
  - Wayland mediation: $9M = 7.2% of uncapped damages and 18.1% of capped-plus-primary damages.
  - Ascot target: C$5–11M against about C$49M in common-law damages, i.e. about 10–22%.
  - Aurora: the US settlement was scaled by volume share and time overlap.
- `settlement_target` = 10%–20% of common_law_rough, floored at statutory_capped × 0.5. It is shown as a
  range.
- Report it next to D&O insurance and cash. Where the target exceeds the insurance plus the cash
  that can realistically be reached, say so; that bears on the recommendation.

## Limitation clock (date arithmetic in the script)
- s. 138.14: 3 years after the first impugned document. Show the date.
- Common law (Limitations Act, 2002): 2 years after the correction. This is a discovery proxy; flag
  it as an approximation.
- If any expiry is less than 6 months away, flag it in the deal sheet and in the reply to the user.

## Screening thresholds Andrew applies (from `andrew-method.md` §4)
| Signal | Flag |
|---|---|
| Canadian recoverable class (Canadian venues + Canadian residents) about $5M or less | "below Andrew's Pass threshold (Paladin)" |
| 10-day look-back recovers more than 75% of the day-0 drop | "price recovered (Alamos)" |
| Settlement target low end below C$5M | "below the targets in his past origination memos" |
| A foreign or US venue holds more than 80% of class volume | "class largely abroad; check the competing foreign action (Paladin)" |
