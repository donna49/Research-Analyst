# Accounting and disclosure red flags

Used by `knowledge-indicators` (stage 6) and the red team in `verify`. A red flag is a pattern to
document with dates, not a conclusion: each one has ordinary explanations, and the record must
carry them (`innocent_explanation`, `direction: undercuts` where the evidence points that way).

Adapted from InvestSkill `earnings-quality` / `bear-case` and Bigdata.com `earnings-quality-screen`.

## Filing and governance events (high signal, easy to date)

| Pattern | Where (US) | Where (Canada / UK / Germany) | What to record |
|---|---|---|---|
| Non-reliance on prior financial statements (restatement) | 8-K Item 4.02 | Material change report; RNS; ad hoc announcement | Periods restated, who concluded (board, auditor), date the company says it identified the error |
| Material weakness in internal control | 10-K Item 9A, 10-Q Item 4 | MD&A / annual report internal control section | First period reported, the area affected, whether earlier certifications said controls were effective |
| Late periodic filing | Form 12b-25 (`NT 10-K`, `NT 10-Q`) | Cease trade order for failure to file (Canada); AIM suspension (UK); late annual report (Germany) | Stated reason verbatim; whether the reason later changed |
| Auditor resignation or dismissal | 8-K Item 4.01 and the auditor's Exhibit 16 letter | Change of auditor notice (Canada NI 51-102); RNS; annual report | Disagreements or reportable events stated; timing relative to the audit cycle |
| Sudden CFO, CAO or CEO departure | 8-K Item 5.02 | Announcements | "Effective immediately", stated reason, any severance or consulting terms, whether the person signed the certifications under review |
| Going-concern language | Auditor report; financial statement notes | Same | First period it appeared; whether earlier calls or releases described liquidity as adequate |
| Covenant waiver or amendment | 8-K Items 1.01 / 2.04; debt notes | Material change report; RNS | Date, covenant affected, whether disclosed at the time |
| SEC comment letter on a disclosure at issue | EDGAR `CORRESP` / `UPLOAD` (released about 20 business days after the review closes) | Regulator reviews are rarely public | Both dates: when the letter was sent and when it was made public |
| Enforcement or review by the accounting regulator | SEC, PCAOB | OSC/BCSC; FRC / FCA (UK); BaFin financial reporting enforcement (Germany) | Date opened, scope, the company's description of it |

## Financial-statement patterns (need two or more periods; compute with a script, never by hand)

| Pattern | What it can indicate | Ordinary explanations to record |
|---|---|---|
| Receivables growing much faster than revenue (DSO up) | Revenue pulled forward, collection problems | Customer mix, contract terms, seasonality, an acquisition |
| Inventory growing much faster than sales | Demand weaker than described; obsolete stock | Supply-chain buffers, launches, pricing |
| Reserve or allowance releases boosting earnings | Earnings management | Better collection experience; resolved claims |
| Repeated "one-time" charges | Recurring costs presented as non-recurring | Genuine restructuring programme |
| Change in revenue recognition, segment reporting or KPI definitions | Comparisons broken just before a problem appears | New standard, reorganisation |
| Non-GAAP adjustments growing relative to GAAP results | Results presented more favourably than GAAP shows | Acquisition accounting, stock compensation |
| Goodwill not impaired while market value is below book value | Impairment delayed | Valuation of reporting units differs from market price |
| Operating cash flow persistently below net income | Low earnings quality | Working-capital build in a growth phase |
| Guidance reaffirmed shortly before a large cut | What was known at the reaffirmation | Late-quarter shock documented with a date |

## Disclosure-wording patterns (from the stage 5 statement trail)

- A risk factor that says something "could" or "may" happen after it already had.
- A reassurance repeated each quarter and then dropped without comment the quarter before the drop.
- Hedging that escalates quietly ("we expect" → "we currently expect" → "subject to").
- Specific numbers replaced by qualitative language, or a metric no longer reported.
- An analyst question on the subject answered with a general statement, or deferred.

## Rules

- Every pattern found becomes a `knowledge` record with `indicator`, `direction`, a quote or a
  script figure, and the date it became public.
- Every pattern searched for and not found is recorded too (a `search` record with results 0);
  absence is evidence on the other side.
- Figures (DSO, growth rates, ratios) come from a script over the filed statements, with the
  filing cited; never from memory or from a data vendor's derived field without its source.
