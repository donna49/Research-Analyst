# Research Analyst Plugin: Plan

Goal: a plugin that reproduces Andrew's securities-research memo, consistently and verifiably,
for each stock the screener flags. It organizes evidence; Andrew makes the legal judgment.

The one question every run must answer:
**Did the new information merely show the business did badly, or did it show investors had
earlier been given a materially inaccurate picture?**

---

## 1. Design principles (how "rigorous" is enforced, not just requested)

1. **Evidence ledger first, memo second.** Every stage writes structured records to one ledger
   (JSON). The memo is rendered only from the ledger. A sentence with no ledger record behind it
   cannot appear in the memo.
2. **Every record is pinned to a primary source**: document URL, accession number or docket
   number, date and time, exact quoted text, and location (page, section, paragraph).
   Secondary sources (news, short reports) are labeled as such and never stand alone for a fact
   a primary source could confirm.
3. **Code computes, the model reads.** Prices, returns, volume, market-cap loss, abnormal returns
   and date arithmetic come from scripts with saved inputs, so they can be re-run and audited.
   The model never types a number it did not get from a script or a quoted document.
4. **Point-in-time discipline.** Each statement is tagged with when it became public, so the
   timeline can show what investors could have known on each date.
5. **Both sides, always.** For every apparent discrepancy the ledger must hold the contrary
   evidence and the innocent explanation. A memo that finds no discrepancy is a valid result.
6. **Neutral language.** "Appears inconsistent with", never "fraud" or "lied". No legal
   conclusions; Section 7 frames questions for Andrew.
7. **Gaps are shown, not filled.** Missing data is listed as an open question, never estimated.

"100% sure" in practice means: every claim is traceable to a source Andrew can click, every
number reproduces, and every gap is declared. Completeness of news coverage cannot be guaranteed,
so the memo states which sources were searched and over which dates.

---

## 2. Pipeline (input: one row from the screener)

| Stage | Does | Memo section | Andrew's question |
|---|---|---|---|
| 0. Intake | Resolve ticker → legal entity, CIK, exchange, securities; check whether a securities suit is already filed | 1, 2 | — |
| 1. Market event | Price before/after, % drop, volume vs average, market-cap lost, abnormal return vs market and sector index, prior volatility, other ≥10% drops in the lookback | 6 | Q5 |
| 2. Trigger | Everything public in the window around the drop (company filings, news, court, regulator, short reports); rank likely trigger vs confounding news | 5 | Q1 |
| 3. Issue definition | State the specific subject of the adverse news (e.g. "litigation exposure on project X") and search terms for it | 3 | Q1 |
| 4. Prior statements | Pull 10-K, 10-Q (MD&A, risk factors, legal proceedings, contingencies notes), 8-K press releases, earnings calls over 2 years (max 3); extract only passages on the issue, with quotes | 4 | Q2 |
| 5. Comparison | For each prior statement: what later facts bear on it, type of statement (historical fact / forward-looking / opinion / risk factor written as hypothetical), whether wording changed quarter to quarter, apparent inconsistency, contrary evidence | 4 | Q3 |
| 6. Knowledge indicators | Dated evidence management knew or had reason to know: court filings and rulings, regulator letters, insider sales (Form 4), executive departures, auditor changes, internal events disclosed later | 4, 7 | Q4 |
| 7. External evidence | Dockets and filings (CourtListener / PACER), regulator actions, independent reporting, short-seller research | 3, 5 | Q1, Q4 |
| 8. Timeline | One chronology merging events, statements, and market reactions, each with its public date | 3 | all |
| 9. Verify | Re-fetch and re-check every quote and number; recompute all figures; red-team the discrepancy theory | — | — |
| 10. Memo | Render Andrew's 7 sections from the ledger, with open questions and a source list | 1–7 | — |

Human checkpoint after Stage 3: Andrew (or the operator) confirms the issue definition before the
expensive lookback work runs. A wrong issue definition wastes everything downstream.

---

## 3. Data sources

Reachability checked from this environment on 2026-10-19.

| Need | Free source | Status here | Paid / connector option |
|---|---|---|---|
| Filings, full text, exhibits | SEC EDGAR submissions API, Archives, XBRL company facts | ✅ reachable | Bigdata.com (filings search) |
| Search filings for a phrase across time | EDGAR full-text search (2001+) | ✅ reachable | Bigdata.com |
| Press releases | 8-K exhibit 99.1 on EDGAR | ✅ | Bigdata.com news |
| Earnings call transcripts | Rarely free; sometimes company IR | ⚠️ gap | **Bigdata.com** (main reason to pay) |
| News around the drop date | Web search; GDELT (not reachable here) | ⚠️ partial | **Bigdata.com** news |
| Daily prices and volume | Yahoo chart API (unofficial), TradingView scanner | ✅ (unofficial, terms risk) | Bigdata.com market data; a licensed price feed later |
| Shares outstanding | XBRL `dei:EntityCommonStockSharesOutstanding` | ✅ | — |
| Insider trades | EDGAR Form 4 | ✅ | — |
| Court dockets and documents | CourtListener API (RECAP: only documents someone already bought) | ✅ API reachable; MCP connector currently disconnected | PACER ($0.10/page, capped at $3/document) for missing documents |
| Existing securities class actions | Stanford SCAC | ❌ 403 here | CourtListener search; news |
| Regulators | SEC litigation releases and AAERs, DOJ press releases, Federal Register API | ✅ mostly | — |
| Canada / UK / Germany filings | SEDAR+, FCA NSM / RNS, Bundesanzeiger | ⚠️ no clean free APIs | Bigdata.com may cover; to be confirmed |

---

## 4. What we take from the five plugins

| From | Take | Use in stage |
|---|---|---|
| InvestSkill **fact-check** | Claim ledger, primary-source tiers, recompute every figure, "fabricated citation = fail" | 9 |
| InvestSkill **10k-digest / financial-report-analyst** | Keyless EDGAR recipe; prior-year promise tracker; risk-factor diff and hedging-language flags | 4, 5 |
| InvestSkill **insider-trading** | Form 4 parsing and transaction codes, 10b5-1 plan discount | 6 |
| intel **evidence standards** | Claim types (fact / attributed / inference / assumption), confidence separate from likelihood, counting one source family as one origin | ledger schema |
| intel **diagnose** | Competing hypotheses for the trigger (company news vs sector move vs confounding news) | 2 |
| intel **red-team** | Adversarial pass: strongest innocent explanation for each discrepancy | 9 |
| intel **research** | Source evaluation, tracing a figure to its origin | 2, 7 |
| Bigdata.com **catalyst-monitor / company-brief / earnings-digest** | Query discipline (one topic, one period per search), litigation and regulatory queries, transcript retrieval | 2, 4, 7 |
| financial-services **earnings-analysis** | Hard check that data is current; read numbers only from saved files | 1, 10 |
| financial-services **ib-check-deck** idea | Consistency check of every number across memo sections | 9 |

Not used: buy/sell signals, valuation models, technical analysis, social-media readers.

---

## 5. Plugin structure

```
research-analyst/
  .claude-plugin/plugin.json
  commands/
    investigate.md          # /investigate <ticker> <drop-date>
    batch.md                # run over a screener output file
  skills/
    research-memo/          # orchestrator: runs stages, enforces checkpoints
    market-event/           # stage 1 (calls scripts)
    trigger-finder/         # stage 2
    disclosure-history/     # stages 4-5: extract and compare statements
    knowledge-indicators/   # stage 6
    external-evidence/      # stage 7 (courts, regulators, short reports)
    timeline/               # stage 8
    verify/                 # stage 9: re-fetch quotes, recompute numbers, red-team
    memo-writer/            # stage 10: renders Andrew's template from the ledger
  scripts/
    edgar.py                # filings, full-text search, XBRL, Form 4
    prices.py               # prices, volume, event study (abnormal return, t-stat)
    courts.py               # CourtListener API
    ledger.py               # schema validation; blocks memo if any claim lacks a source
  references/
    memo-template.md        # Andrew's 7 sections, built from his real examples
    statement-types.md      # forward-looking vs fact vs opinion vs hypothetical risk factor
    language-rules.md       # neutral wording, banned phrases
```

---

## 6. Build phases

| Phase | Output | Exit test |
|---|---|---|
| 0. Inputs from Andrew | 3–5 of his past memos, the JBG Smith and mining-company case names and dates, answers to the questions below | We can name each memo section's required content from real examples |
| 1. Deterministic layer | `edgar.py`, `prices.py`, `courts.py`, ledger schema | Reproduces the market figures in Andrew's past memos exactly |
| 2. Evidence skills | Stages 0–8 | On past cases, finds the trigger and the prior statements Andrew cited |
| 3. Verification + memo | Stages 9–10 | Every quote re-matches its source; every number recomputes; no unsourced sentence |
| 4. Back-test | Run on 5–10 cases where Andrew already has memos | Recall of Andrew's cited statements; zero fabricated quotes; time per case |
| 5. Pilot | Run on his backlog of 50+ cases with his review | Andrew's edit rate per memo falls over the pilot |

Later and separate: drafting complaints from the memo plus his 50+ pleadings; identifying
shareholders who held through the drop.

---

## 7. Open questions for Andrew

1. **Jurisdiction.** The screener covers Canada, the UK and Germany. Is the memo US-only
   (Rule 10b-5) for now, or must it handle non-US companies under their own law and filing systems?
   Companies that file on EDGAR (40-F, 20-F, 6-K) are easy; others need different sources.
2. **His past memos.** Can we have 3–5 to build the template and the back-test?
3. **Event-study standard.** Does he want a formal abnormal-return test (market and sector
   adjusted), or the raw price drop as in his current memos?
4. **Already-filed cases.** Should the plugin stop, flag, or continue when a securities class
   action is already filed for the same drop?
5. **PACER.** Does he have a PACER account the plugin may use (with a spend cap) when CourtListener
   lacks a document?
6. **Output format.** Word document, Google Doc, or both?

## 8. Main risks

| Risk | Mitigation |
|---|---|
| Fabricated or altered quotes | Verify stage re-fetches every source and exact-matches each quote; memo blocked on any miss |
| Wrong trigger chosen | Competing-hypothesis table with timestamps; abnormal return vs sector shows if the drop was company-specific |
| Missing the relevant prior statement | EDGAR full-text search over the whole lookback, not only the latest filings; risk-factor diff quarter to quarter |
| Transcript and news gaps | Bigdata.com; memo lists sources searched and dates covered |
| Overstating legal conclusions | Language rules and a final check for banned phrasing |
| Unofficial price data | Cross-check two sources; move to a licensed feed before client use |
