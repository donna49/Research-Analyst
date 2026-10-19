---
name: first-review
description: Andrew Morganti's own seven-step first review of a stock that fell more than 10% in one day (his trigger, references/trigger.md). Covers the SEDAR+ profile, every record released on the drop date, the 1–3 most important facts, comparison with a year of MD&As, how the language changed, the call transcripts, and a year-plus-30-days of price and volume. Use right after triage for each name that meets the trigger, as the opening of every Layer 2 investigation, or whenever asked for a quick first look at a drop.
---

# First review: Andrew's seven steps

This is the order Andrew follows himself. Run it in this order. It opens every Layer 2 investigation and
can also stand alone as a fast first look. Every finding is written to the case ledger as usual. The
output is `runs/<date>/<TICKER>/first_review.md`.

## 0. Trigger
Confirm the trigger in `references/trigger.md`: a fall of more than 10% in one day, a market cap over
$200M, and either a TSX/TSXV/CSE/Cboe Canada listing, or a Canadian-registered SEDAR+ filer whose
security dropped on Nasdaq, NYSE or US OTC. Record a `framing` record (`element: "trigger"`). If the
trigger is not met, stop and say why.

## 0b. Drive Sources
Read the case subfolder in Research Memos / Sources, and start `to_save.md`, as set out in
`references/drive-sources.md`.

## 1. SEDAR+ profile (the issuer card)
From the company's SEDAR+ profile page (the first page after opening the company), record:
- business address(es)
- the laws of incorporation (jurisdiction)
- CUSIP
- stock symbols
- reporting jurisdictions and filer type

Write these as `party` records.

If the company has **no SEDAR+ entry**, record a `gap`. This happens when a Canadian company has only US
securities. Take the same facts from the 10-K/20-F/40-F cover (EDGAR) and the incorporation records
(OpenCorporates, the provincial registry).

SEDAR+ often blocks automated access (`source-hierarchy.md`). Try the routes listed there. If the
profile still cannot be read, ask the user to save the profile page into the case's Drive folder
(`references/drive-sources.md`).

## 2. Every record released on the drop date
List every document the company filed or released on the drop date, and on the evening before if the
drop session follows an after-close release. Use SEDAR+ "documents" for that date, EDGAR for US filers,
the issuer's news page and the wires. First pull anything the user saved to the case's Drive folder
(`references/drive-sources.md`). Save each document's text to `sources/`. Record the release time
stamp; it decides which session reacted.

## 3. The 1–3 most important facts
Read those records and pick **at most three** facts that most plausibly drove the drop. Write them as
`revelation` records, each with an exact quote and the time stamp. Rank them. Name each one the way
Andrew names a theme, e.g. "Fully Funded" or "Credit Committee approval". These facts become the
provisional issue for stage 3.

## 4. A year of MD&As against those facts
Collect the MD&As filed in the **12 months before the drop**: annual and interim, plus the AIF if one
was filed in that window. For each fact, find what each MD&A said about it, quoting the passage with
page and section. Silence counts and is recorded too. Write these as `statement` records.

## 5. How the language changed
For each fact, build a **language table**: one row per MD&A in date order, then the drop-date
disclosure as the last row. Show the operative words in each and mark what changed: terms added,
dropped, softened or hedged, dates moved, figures changed. Flag every contradiction between an earlier
MD&A and the drop-date disclosure, and every silent change ("CURIOUS"). This table is the core of the
first review and goes straight into the Total Mix.

## 6. The quarterly call transcripts
Do the same for each quarterly earnings call in the year: prepared remarks and analyst Q&A, with the
speaker and the analyst's firm. Sources are Bigdata.com transcripts, then the issuer's webcast page,
then news coverage of the call. Add the call rows to the language table. A missing transcript is a gap,
not silence.

## 7. Price and volume history
```
python3 scripts/price_history.py EXCH:TICKER <drop date> --out runs/<date>/<TICKER>/price_history.csv
```
The window runs from one year plus 30 days before the drop through the drop day. The script also lists
every earlier fall of 10% or more, which are candidate storm warnings. Then run
`economics.py --moves` on each MD&A and call date from steps 4–6, so the language table shows the
price move on each date.

## Output: `first_review.md`
1. The trigger line and the issuer card (step 1).
2. The drop-date records with time stamps (step 2).
3. The 1–3 facts, ranked (step 3).
4. One language table per fact (steps 4–6), with the price move on each date.
5. Earlier 10%+ falls (step 7).
6. A one-paragraph first read in Andrew's voice: is there a contradiction worth a full investigation,
   and what to check next.

Then go on to the full Layer 2 stages. The first review supplies stages 1–5 their starting records,
so do not repeat the work. Stop at checkpoint 1 with the issue definition built from step 3.
