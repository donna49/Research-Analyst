---
name: parties-and-capital
description: Stage 8 of a research-analyst investigation. Builds the issuer profile and the facts about parties and capital that Andrew's memos open with and rely on, and records each as a ledger record. Covers listings, tickers, CUSIP/ISIN, incorporation, reporting-issuer provinces, shares outstanding, market cap, offerings, insider trades, officers, directors, auditor, underwriters, compensation, cash and D&O insurance. Use after the issue is confirmed, or when asked who the defendants are, what the capital structure is, or whether the company can pay.
---

# Parties and capital (stage 8)

Andrew opens every memo with the issuer's identity and closes with whether there is money to recover.
This stage collects both, from primary documents, as `party`, `capital` and `offering` records.
It can run in parallel with stages 6–7.

## 1. Issuer identity (`party`, role `issuer` / `listing`)
- Full legal name. Defined term and ticker, written as in his memos: «Issuer» ("TICKER").
- Statute and jurisdiction of incorporation; head-office address. Take these from the AIF or 10-K
  cover, not from a data vendor.
- Every listing: exchange, ticker, currency, and whether it is primary. Include OTC, Frankfurt, ASX,
  and CDRs/ADRs with the depositary and ratio.
- CUSIP and ISIN (Bigdata.com `find_securities`; SEDAR+ profile; the 10-K cover for US issuers).
- Reporting-issuer provinces (SEDAR+ profile, AIF), and US filer status.
- The company's self-description, quoted from the AIF or 10-K business section, for the Overview.
- Canadian footprint for issuers not listed in Canada (see `jurisdictions.md` step 1).

## 2. Capital (`capital`)
- Shares outstanding per equity class, with the as-of date. Use the figure **nearest the 10 trading
  days before the first impugned document** (the s. 249 window) and the figure nearest the
  correction. Sources: the MD&A "outstanding share data", the 10-Q/10-K cover, or OSC Form
  13-502F1. Also note warrants and options.
- Cash and equivalents, and debt, at the last balance sheet before the correction.
- **D&O insurance:** the amount and layers if disclosed (the AIF or circular sometimes states it,
  e.g. "$50 million of coverage for directors and officers' liability insurance"). Otherwise record a
  `gap` with `would_be_settled_by` "D&O policy (production) / circular". Note any CCAA order limiting
  recovery to insurance.
- Market cap from the scripts only (stage 1 or `economics.py`), never typed in.

## 3. Offerings (`offering`)
Record every offering from 12 months before the Class Period through the correction: prospectuses,
prospectus supplements, private placements, bought deals, ATM programmes. For each: date, security,
price, number, gross proceeds, agents/underwriters, use of proceeds, and the exemption relied on.
These ground the s. 130 primary-market class and the gatekeeper defendants.

## 4. People (`party`)
- Officers who certified each impugned document: CEO and CFO for each period. Use the certificates
  (NI 52-109 / SOX 302) or the signature blocks.
- Directors during the Class Period, with tenure. Note audit-committee membership and any lawyers or
  accountants on the board.
- Compensation for the year before the correction, from the summary compensation table in the
  circular or proxy (the MDC/NAP memos). Include auditor fees.
- Auditor: name, opinion dates, any change ("storm warning", e.g. KPMG → PwC in Canacol), any
  resignation or disagreement.
- Underwriters and agents of offerings in the Class Period.
- Controlling holders and related parties: holdings, management agreements, related-party
  transactions (Slate: the manager owned by two trustees).

## 4b. Other companies of the executives and directors (flow-chart step 7)

For each C-level executive and director, list their other directorships and offices. Sources:
- the circular's director biographies
- SEDAR and EDGAR filings of those other companies
- OpenCorporates
- ICIJ Offshore Leaks, for offshore entities

Note any overlap with counterparties, related parties or other troubled issuers. Record each as a
`party` record (`role: related party`), with the source.

## 5. Insider trades (`capital`, metric `insider trade`)
- From six months before the Class Period through the correction. Use SEDI for Canadian issuers;
  EDGAR Form 4 (code S/P; 10b5-1 footnotes) for US; RNS PDMR for the UK; BaFin for Germany.
- One record per trade: name, role, date, number, price, value. Compare each with the person's usual
  pattern.
- If none: one `search` record showing the query and date range, so the memo can say "none reported".
  This mirrors Slate, where each trustee's sales were listed as "$nil".

## 6. Output
Write `runs/<date>/<TICKER>/parties.md`: an issuer card, capital table, offerings table, people
table and insider-trade table, with every row citing ledger ids. The memo-writer copies from the
records, not from this file.
