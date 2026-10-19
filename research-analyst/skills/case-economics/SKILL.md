---
name: case-economics
description: Stage 9 of a research-analyst investigation. Runs scripts/economics.py to compute what Andrew's memos estimate by hand, and records each result as an economics ledger record. Covers the price reaction to each correction, the ten-day look-back, Class Period volume by venue, damaged shares, rough statutory and common-law damages, the 5% liability cap, a settlement target and the limitation dates. Use once the corrections and a provisional Class Period start are known, or when asked how big the case is.
---

# Case economics (stage 9)

`references/economics.md` defines every formula. You prepare the input; the script computes; you
record. Never type a damages figure, percentage or cap yourself. Andrew's own memos show what
happens otherwise: −44.2% written for −30.7%, and a cap that mixed USD and CAD.

## 1. Price move for every disclosure in the total mix
```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/economics.py" --moves EXCH:TICKER <date> <date> ... --json runs/<date>/<TICKER>/moves.json
```
Run this on every statement date from stage 4 and every correction date. Andrew logs a price move,
including "(nil%)", for each disclosure in the total mix. Record each as a `market` record citing
`moves.json`. **Add `+` to a date released after the close** (e.g. `2024-07-16+`); the script then
uses the next session as the reacting session. Without `+`, the script uses the date itself, if it
was a trading session.

## 2. Input file
Write `runs/<date>/<TICKER>/economics_input.json`:
```json
{"venues": [{"symbol": "TSX:XXX", "role": "primary", "currency": "CAD", "ledger": "E0nn"},
            {"symbol": "OTC:XXXXF", "role": "secondary", "currency": "USD", "ledger": "E0nn"}],
 "class_period": {"start": "YYYY-MM-DD"},
 "first_impugned_date": "YYYY-MM-DD",
 "corrections": [{"date": "YYYY-MM-DD", "label": "storm warning: ...", "storm_warning": true, "ledger": "E0nn"},
                 {"date": "YYYY-MM-DD", "label": "public correction: ...", "ledger": "E0nn"}],
 "shares_outstanding": [{"class": "common", "shares": 0, "as_of": "YYYY-MM-DD, source", "ledger": "E0nn"}],
 "other_equity_fmv": 0,
 "d_and_o": {"amount": null, "ledger": "E0nn or gap id"},
 "cash": {"amount": 0, "currency": "CAD", "as_of": "YYYY-MM-DD", "ledger": "E0nn"}}
```
- The Class Period start is provisional until stage 10 (claim-framing) fixes it. Re-run the script
  after it changes.
- Use the release date for each correction, and set `"after_close": true` for releases made after the
  close. The script then uses the next session. Check the release time stamp (stage 2) first.
- Add `"offerings": [{"date": ..., "security": ..., "price": ..., "units": ..., "ledger": ...}]` for
  prospectus offerings (s. 130). The script prices them against the final ten-day look-back and
  keeps them separate from the secondary-market damages.
- Run with `--asof YYYY-MM-DD` to set the date the limitation countdown runs from (default: today).
- Include every venue with meaningful volume. Volume by venue drives the "where is the class"
  question (Paladin).

## 3. Run
```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/economics.py" runs/<date>/<TICKER>/economics_input.json --json runs/<date>/<TICKER>/economics.json
```
Then write one `economics` record per headline figure. Each record has `metric`, `value`,
`currency`, `formula` (copied from the JSON), and source `script output` with `location` set to the
JSON path. Write records for:
- day-0 drop and percentage, volume ratio and 10-day look-back for each correction, on each venue
- Class Period volume and VWAP for each venue, and the volume split
- per-share measures m1, m2 and m3
- damaged shares and damages for each retention
- market cap, the cap window and the liability cap
- the headline common-law range, the capped statutory figure and the settlement target
- the limitation expiry dates

## 4. Read the flags as Andrew would
| Flag | His reading |
|---|---|
| look-back at or above the pre-correction close | "the stock price immediately recovered". Lean **Monitor / Pass** (Alamos) unless a later correction is expected |
| a non-primary venue holds more than 80% of volume | The class is mostly abroad. Check the competing foreign action; lean **Pass** if the Canadian remainder is about $5M or less (Paladin) |
| settlement target below 5M | Below his origination targets. Say so in the deal sheet |
| limitation less than 183 days away | Urgent. Put it first in the reply to the user |

Record every flag as an `economics` record (status `fact`, citing the flags path). Its implications
go to claim-framing.

## 5. Caveat line (always in the memo)
"Rough screening estimates from public prices and volume; not an expert damages opinion. A damages
expert would be retained before issuing."
