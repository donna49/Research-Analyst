# Andrew's Securities Origination Flow-Chart (August 15, 2026)

Source: "Securities Origination Flow-Chart (August 15, 2026)", a Google Sheet in Andrew's Drive
(file id 1dnZDxtSESkG_DAzl2Psmrl6slVrP5WSpNJ3fr-q3Zu4). This is his own written procedure. Where it
differs from anything else in the plugin, **the flow chart wins**, except where he has said otherwise
since (noted below).

## Markets he tracks

- TSX
- TSXV
- CSE
- Cboe Canada
- Nasdaq Canada
- Canadian electronic markets
- **NYSE and Nasdaq, limited to companies reporting on SEDAR**

UK and German exchanges are **not** among the markets he tracks. The UK FCA and the Australian ASIC appear
only as regulator sources for triggers (below).

## Triggering events and their source pages

1. **Price trigger:** a company with a market capitalization over **$250M** whose security drops more
   than 10%. Exchanges are watched by a daily search profile (free). His message of October 19, 2026
   gives **$200M**; the plugin uses $200M, the later statement, and treats $200–250M as a margin to flag.
2. **Company disclosure, including foreign companies**, from daily Google alerts. For a non-Canadian
   company, check whether it reports on SEDAR or whether its securities trade on a tracked market.
3. **Regulator notices of a new investigation or enforcement action:** US SEC; Ontario Securities
   Commission; Quebec Securities Commission (AMF); British Columbia Securities Commission; US CFTC; UK
   Financial Conduct Authority; Australian Securities and Investments Commission. All are free.
4. **Verteris.com** (subscription, $500 a month).
5. **CBA Class Action database** (Canadian Bar Association; free, "need to click a few buttons"). Shows
   which class actions are already filed.

## The 15 steps, and where each one lives in the plugin

| Step | His words (lightly condensed) | Sources he lists | Plugin |
|---|---|---|---|
| 1 | Look at the YTD and 1-year stock chart. Are there patterns? A natural increase or decrease over time? Is the stock volatile? Is the drop harsh and immediate? Goal: identify a potential Class Period | — | `first-review` step 7 (`price_history.py`); `market-event` |
| 2 | Identify the news published just before the 10%+ drop (the "Public Corrective Statement") and its material facts. Was it published by the company or by a third party? | — | `first-review` steps 2–3; `trigger-finder` |
| 3 | Search the company's continuous disclosure records (core documents, e.g. quarterly reports) for the new material facts in the Public Corrective Statement | SEDAR, EDGAR, company website | `first-review` steps 4–5; `disclosure-history` |
| 4 | Analyze the quarterly investor call transcripts during the theoretical class period for statements that contradict the Public Corrective Statement | Company website; Seeking Alpha and Stockhouse (free); Seeking Alpha and Intelligize (subscription) | `first-review` step 6 |
| 5 | Analyze the media's responses to the Public Corrective Statement | Professional research analysts; short-seller firms | `external-evidence` (analysts, short sellers, media) |
| 6 | Analyze all companies that do business with the corporate defendant, through those companies' own continuous disclosure records | SEDAR, EDGAR, social media and articles | `external-evidence`: counterparties |
| 7 | What other companies do the defendant's C-level executives and board members serve? Use those companies' disclosure records | SEDAR, EDGAR | `parties-and-capital`: other directorships |
| 8 | How far back did the company make statements on the new material facts that contradict each other? This identifies the Class Period | SEDAR, EDGAR, Intelligize (subscription) | `disclosure-history`; `claim-framing` §3 |
| 9 | Did insiders sell shares during the proposed Class Period? | SEDI.ca | `parties-and-capital` §5 |
| 10 | Did the company conduct public offerings during the Class Period? | SEDAR, EDGAR | `parties-and-capital` §3 |
| 11 | Liability limits and damages. **Statutory:** 5% of market capitalization *measured at the release of each impugned document*. **Common law:** generally 40% of Class Period trading volume × the price drop from the release of the public correction through the following 10 days | — | `case-economics` (`economics.py`) |
| 12 | Jurisdiction: reporting issuer (SEDAR)? Responsible issuer (*Van Breda* test)? | SEDAR | `claim-framing` §1; `jurisdictions.md` |
| 13 | Are the corporate defendant, its executives or its board members involved in other litigation, or targets of government investigations? | (his October 19 list: PACER, Law360, SEC Enforcement, DOJ, financialcrimenews.com, ICIJ, OpenCorporates) | `external-evidence`; `claim-framing` §2 |
| 14 | Draft memo to file; news release of his investigation; retainer agreement | — | `memo-writer`. The investigation news release and the retainer are drafted only when he asks; they are outward-facing |
| 15 | Draft the statement of claim, application or complaint | — | Later stage (not built yet; his sample pleadings are in `00 Sample Pleadings`) |

## What this confirms in the plugin

- **The 40% rule** in `economics.md` is his own written rule: 40% of Class Period volume × the drop
  through the 10-day look-back.
- **The 5% cap is measured at each impugned document.** `economics.py` computes it at each date in
  `impugned_dates`, not only at the start of the Class Period.
- The **trigger** in `trigger.md`, and the restriction of US-listed names to SEDAR reporters.
- **Steps 6 and 7** (counterparties; executives' other companies) are now explicit tasks in
  `external-evidence` and `parties-and-capital`.
