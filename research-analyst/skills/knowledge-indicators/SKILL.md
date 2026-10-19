---
name: knowledge-indicators
description: Stage 6 of a research-analyst investigation. Collects dated evidence bearing on whether management knew, or had reason to know, of the problem before the adverse disclosure, and evidence pointing the other way. Use after the prior-statement comparison, or when asked what a company knew and when.
---

# Knowledge indicators (stage 6)

Collect dated evidence on both sides. Each item is a `knowledge` record with `direction`
`supports` (suggests earlier awareness) or `undercuts` (suggests the problem was new or unforeseeable).
Never conclude that anyone "knew"; record what the evidence shows and when.

## Indicators to search for

| Indicator | Where | Notes |
|---|---|---|
| Earlier court filings, rulings, expert reports in the same matter | CourtListener docket entries; UK Find Case Law; openJur | Date each ruling; compare with statements made after it |
| Regulator correspondence or actions (comment letters, warning letters, inspection findings) | SEC comment letters (EDGAR `CORRESP`/`UPLOAD`); FDA and other agency databases via open web; Bigdata.com news | Comment letters are released with a lag; record both dates |
| Insider dealing before the drop | EDGAR Form 4 (code S = open-market sale, P = purchase; note 10b5-1 plan footnotes and plan adoption dates); RNS PDMR notices; BaFin directors' dealings; SEDI | Compare timing and size with the person's usual pattern (from InvestSkill `insider-trading`) |
| Executive or director departures, auditor changes | 8-K Items 5.02 and 4.01; announcements | Note "effective immediately" and stated reasons |
| Internal facts later disclosed | The corrective disclosure itself, later filings, complaints, court findings | E.g. "the company first learned of X in March" stated in a later filing |
| Analyst questions on the subject that management deflected | Transcripts (Q&A) | Quote question and answer |
| Accounting signals | Restatements, reserve changes, material weaknesses, delayed filings, auditor change or resignation (Canacol: KPMG → PwC) | Treat an auditor change shortly before the correction as a storm warning |
| Sworn statements made later | Affidavits by officers in lien, CCAA, insolvency or commercial proceedings; monitor reports | Ascot: the CEO's affidavit contradicted the earlier "fully funded" statements. Quote by paragraph |
| Trading ahead of the release | Intraday prices vs the release time stamp; volume on the days before | Sintana: a 15% drop on record volume before an after-hours release. Paladin: "as if certain market participants knew" |
| Timing of the company's own excuse | The reason given at the correction vs when that reason arose | Global Atomic: the excuse (an election) came before statements that were made as if nothing had changed |
| Earlier incidents of the same kind | Prior spills, delays, guidance misses, regulator findings | Barrick: two prior spills made the third foreseeable |
| Operational facts that management would ordinarily see | Production or shipment data, customer notices, outages, recalls in public records or reporting | Record the public date and the underlying date |
| Contrary evidence | Specific earlier disclosures of the risk; documented new facts arising after the statements | Must be searched for, not just noted if found |

## Searches

Bigdata.com fast mode, entity filter, one indicator per query, within the lookback; CourtListener
for the same matter; EDGAR for Forms 4, 8-K items and correspondence. Record every search.
