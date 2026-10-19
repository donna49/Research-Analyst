# Research Analyst Plugin: Plan v2

Supersedes v1. Decisions from 2026-10-19 are folded in.

**Purpose.** For every stock the screener flags (≥10% one-day drop, Canada / US / UK / Germany),
decide whether the drop exposed a gap between what the company had told investors and the truth,
and assemble the evidence so Andrew can make the legal call.

**The one question:** did the new information only show the business did badly, or did it show
investors had earlier been given a materially inaccurate picture?

---

## 0. Decisions locked

| Topic | Decision |
|---|---|
| Countries | All four: Canada, US, UK, Germany |
| Starting point | Andrew's screener script output (not rebuilt here) |
| Workflow | Two layers: Layer 1 triage of every flagged stock → Layer 2 full investigation only for survivors |
| Memo template | Built later from Andrew's past memos (v2 tuning). v1 uses the 7-section structure from the call notes |
| Existing lawsuits | Never stop. Keep investigating and report the existing case prominently |
| Court records | CourtListener (no PACER) |
| Output | Google Doc, always (Layer 1 triage list and Layer 2 memos) |
| Paid data | Bigdata.com (active, verified). Others listed in §2.4 for Andrew to approve |

---

## 1. Rigor rules (apply to every stage)

1. **Evidence ledger first, documents second.** Every finding is a ledger record: claim, source URL,
   document ID (accession / docket / Bigdata doc ID), publication timestamp, exact quote, location.
   Docs are rendered only from the ledger.
2. **Code computes, the model reads.** Prices, returns, abnormal returns, volume, market value lost,
   and dates come from scripts with saved inputs. The model never types a number it did not get from
   a script or a quoted document.
3. **Primary beats secondary.** A news article can point to a fact; the memo cites the filing,
   court document or regulator release behind it whenever one exists.
4. **Point-in-time.** Every statement carries the moment it became public.
5. **Both sides.** Each apparent discrepancy carries its contrary evidence and innocent explanation.
6. **Neutral language.** "Appears inconsistent with", never "fraud" or "misled". No legal conclusions.
7. **Gaps declared.** Missing data is listed as an open question, never estimated. Every doc lists the
   sources searched and the date ranges covered.

---

## 2. Data sources (fixed)

Tested from this environment on 2026-10-19. ✅ works · ⚠️ works with limits · ❌ blocked/unusable.

### 2.1 Used: by need and country

| Need | US | Canada | UK | Germany | Fallback / notes |
|---|---|---|---|---|---|
| Identify company, listings, ISIN | Bigdata.com `find_securities` ✅ | same ✅ | same ✅ | same ✅ | TradingView scanner |
| Same-day move, sector, industry, market cap | TradingView scanner ✅ | ✅ | ✅ | ✅ | Snapshot only, no history |
| Daily price & volume history (stock, index, sector ETF) | Yahoo chart API ✅ | ✅ | ✅ (prices in **pence**) | ✅ | Intermittent rate limits: cache + backoff. Paid backup in §2.4 |
| Shares outstanding | SEC XBRL ✅ | Bigdata.com tearsheet | Bigdata.com tearsheet | Bigdata.com tearsheet | Cross-check with TradingView market cap |
| Annual / interim reports, MD&A | SEC EDGAR ✅ (10-K, 10-Q, 20-F, 40-F, 6-K) | Bigdata.com (partial) + issuer IR site; SEDAR+ ⚠️ (no API) | Bigdata.com + issuer IR site; FCA NSM ⚠️ (web only) | Bigdata.com ✅ (annual reports found) + issuer IR site; Unternehmensregister ⚠️ (web only) | US-listed foreign issuers: EDGAR first |
| Full-text search of past filings | EDGAR full-text search ✅ | Bigdata.com search | Bigdata.com search | Bigdata.com search | — |
| Press releases / market announcements | EDGAR 8-K Ex-99 ✅ | Bigdata.com news (newswires) ✅; Newsfile ✅ | Investegate RNS archive ✅; LSE news ✅ | EQS News (ad hoc releases) ✅ | Bigdata.com for all |
| Earnings call transcripts | Bigdata.com ✅ | Bigdata.com ✅ | Bigdata.com ✅ | Bigdata.com ✅ | Main reason to pay for Bigdata.com |
| News around the drop | Bigdata.com news ✅ | ✅ | ✅ | ✅ | Open web (§2.2) |
| Insider dealing | SEC Form 4 ✅ | SEDI (web) ⚠️ | RNS "PDMR" notices ✅ | BaFin directors' dealings ✅ | — |
| Court records | CourtListener ✅ (incl. securities suit search, nature of suit 850) | Bigdata.com news + court sites; CanLII ⚠️ (needs free key) | UK Find Case Law API ✅ | openJur ✅; Bundesanzeiger KapMuG register ✅ | — |
| Regulators | SEC litigation releases ✅, DOJ press API ✅, Federal Register API ✅ | Capital Markets Tribunal / OSC ✅ | FCA notices (web) | BaFin (web) | Bigdata.com news |
| Existing shareholder suits | CourtListener (NOS 850 + party name) ✅; plaintiff-firm press releases via Bigdata.com | Bigdata.com news; Class Action Database (web) | Bigdata.com news | Bundesanzeiger KapMuG register ✅ | Stanford SCAC ❌ from here: optional manual check only |
| Short-seller reports | Bigdata.com news + open web | same | same | same | — |

### 2.2 Open web: allowed, with rules

Allowed for **discovery** (finding that something exists) and for official pages (issuer IR sites,
regulators, courts, exchanges). Every web fact must be traced to a primary source before it goes in
a memo; if it can't be, it is labeled "reported by [outlet]" and never used alone.
Not allowed: social media, forums, paywall bypass, anything needing someone's login.

### 2.3 Not used

| Source | Why |
|---|---|
| PACER | Replaced by CourtListener (decision) |
| Social media readers (X, LinkedIn, Discord, Telegram) | Take over logged-in sessions; ToS and evidentiary quality |
| TradingView desktop / cookie-based tools | Session hijack; the public scanner is enough |
| Stooq, GDELT | Not reachable from this environment |
| Stanford SCAC | Blocked (403); CourtListener + news cover it |
| Seeking Alpha, OpenInsider, WhaleWisdom | Paywalled or secondary copies of primary data we already get |
| Built-in benchmark tables in the five plugins | Unsourced and dated |

### 2.4 Optional additions for Andrew to approve

| Source | Cost | Fills |
|---|---|---|
| CanLII API key | Free on request | Canadian court decisions |
| Companies House API key | Free | UK company officers and filings history |
| A paid end-of-day price feed covering TSX, LSE and Xetra | Low monthly fee | Backup when Yahoo rate-limits; licensed data for client work |

---

## 3. The drop standard: is it company-specific?

A raw 10% fall means nothing alone. A stock that falls 11% while its sector falls 8% had a sector day.
A stock that falls 11% while its sector falls 2% had a company day. A stock that swings 6% on an
ordinary day needs a bigger fall to mean anything. The standard measures all three.

### 3.1 Calculation (scripted, same for all four countries)

1. **Event day (day 0).** The trading day the price reacted. If the news came after the close or
   before the open, day 0 is the next session; times are converted to the exchange's time zone.
2. **Benchmarks.**
   - Market index: US S&P 500, Canada S&P/TSX Composite, UK FTSE All-Share, Germany DAX/HDAX
     (exact symbols confirmed in build).
   - Sector: the matching sector ETF (US SPDR sectors; Canada S&P/TSX sector ETFs; UK and Germany
     STOXX Europe 600 sector ETFs), plus the **same-day median move of same-industry peers** in the
     same country from the TradingView scanner as a cross-check.
3. **Normal behaviour.** Regress the stock's daily returns on market and sector returns over an
   estimation window of 120 trading days ending 11 days before day 0 (other ≥10% days removed).
4. **Abnormal return (AR)** = actual return − expected return from step 3.
   **t-statistic** = AR ÷ standard deviation of the stock's normal unexplained moves.
5. **Also computed:** two-day abnormal return (day 0 and day 1), pre-event drift (days −5 to −1)
   for leakage, 5-day rebound, volume ÷ 30-day average, market value lost in local currency and USD.

### 3.2 Classification (v1 defaults, to calibrate on Andrew's past cases)

| Class | Rule | Example |
|---|---|---|
| **Company-specific** | AR ≤ −7% and t ≤ −2.58 | Stock −11%, sector −2% → AR ≈ −9% |
| **Borderline** | AR between −5% and −7%, or t between −1.96 and −2.58 | Volatile small cap, −12% on a −3% sector day |
| **Not company-specific** | AR > −5%, or t > −1.96 | Stock −11%, sector −8% → AR ≈ −3% |

Overrides:
- If the sector itself fell sharply, check whether **this company's news caused the sector fall**
  (a bellwether's disclosure drags peers). If so, it is not excluded.
- An industry-wide revelation that names the company specifically is kept as Borderline.
- A big fall spread over two days is judged on the two-day abnormal return.

### 3.3 Mechanical false signals (checked before any research)

Ex-dividend or special dividend; split or consolidation; rights issue or placing at a discount
(common in UK and Germany); spin-off; data errors (TradingView and Yahoo closes disagree by >1%;
UK pence/pounds mix-ups); index deletion; lock-up expiry. Each is checked automatically from price
events and announcements and becomes an exclusion reason code.

---

## 4. Layer 1: triage of every flagged stock

Goal: within minutes per stock, sort the screener list into **Full investigation**, **Watch** or
**Exclude**, each with a reason Andrew can check in one click.

### 4.1 Steps per stock

1. **Resolve** the entity (legal name, country, all listings, ISIN, US listing or ADR yes/no).
2. **Mechanical check** (§3.3).
3. **Drop standard** (§3.1–3.2).
4. **Trigger scan**: everything published from day −2 to day 0 close: company announcements,
   news, court, regulators, short-seller reports, analyst actions. Rank the likely trigger.
5. **Trigger tier:**

| Tier | Triggers |
|---|---|
| **A: high signal** | Restatement or non-reliance; auditor resignation or qualified opinion; material weakness; regulator or prosecutor investigation, subpoena, raid; short-seller report alleging misconduct; court judgment or ruling on a matter previously downplayed; guidance cut soon after guidance was reaffirmed; sudden CEO/CFO exit; delayed filing; going-concern doubt; trial or regulatory failure after confident statements; dividend cut after assurances; write-down of an asset recently promoted; operational disruption previously described as contained; concealed breach, recall, or loss of a key customer or contract |
| **B: medium** | Earnings miss with guidance cut (no recent reaffirmation); downgrade citing new facts; discounted share sale with an unexplained reason |
| **C: low** | Macro, commodity or rate move; sector news not naming the company; acquirer falling on its own deal announcement; technical or index flows |
| **Unexplained** | No identifiable news. Goes to Watch; news often surfaces days later |

6. **Prior-statement pre-check (quick).** One targeted search of the last 2 years of the company's
   disclosures and earnings calls on the trigger topic. Outcome: *reassured* (raises priority),
   *specific warning given* (lowers priority), *silent* (raises priority), *unclear*.
7. **Existing litigation check**: securities suits already filed or announced (never excludes).

### 4.2 Disposition

| Drop class | Trigger tier | Disposition |
|---|---|---|
| Company-specific | A | **Full investigation** |
| Company-specific | B | Full investigation if pre-check is *reassured* or *silent*; else Watch |
| Borderline | A | Full investigation |
| Borderline | B | Watch |
| Any | Unexplained | Watch (re-scan in 5 trading days) |
| Not company-specific, or mechanical, or Tier C | — | **Exclude** with reason code |

### 4.3 Triage Google Doc (one per screener run)

One row per stock: Company · Ticker · Country · Raw drop · Abnormal return (t) · Market value lost ·
Trigger (one line + link) · Tier · Prior-statement pre-check · Existing suit · **Disposition** ·
Reason code. Excluded stocks stay in the doc, at the bottom, with their reason, so nothing is
silently dropped.

---

## 5. Layer 2: full investigation (stages)

| # | Stage | Output into the ledger | Memo section |
|---|---|---|---|
| 1 | Market event | Full §3 analysis, plus every other ≥10% company-specific drop in the 3-year lookback (staged disclosures) | 6 |
| 2 | Trigger | Exact publication time and source of the adverse information; competing explanations, each scored | 5 |
| 3 | Issue definition | The precise subject of the bad news, its search terms, the lookback period (2 years default, 3 max, shorter if the issue is newer). **Checkpoint: Andrew confirms** | 3 |
| 4 | Prior statements | Every passage on the issue from annual/interim reports (MD&A, risk factors, legal proceedings, contingencies), press releases, earnings calls (prepared remarks and Q&A), investor presentations, with quotes and dates | 4 |
| 5 | Comparison | Per statement: type (historical fact / forward-looking / opinion / risk described as hypothetical); how its wording changed over time; what later facts bear on it; apparent inconsistency; contrary evidence | 4 |
| 6 | Knowledge indicators | Dated evidence management knew or should have known: earlier court filings and rulings, regulator correspondence, insider sales before the drop, executive departures, auditor changes, internal reports later disclosed | 4, 7 |
| 7 | External evidence | Court dockets and documents, regulator actions, independent reporting, short-seller research; how each describes the issue versus the company | 3, 5 |
| 8 | Timeline | One chronology of events, statements and price reactions, each with its public date | 3 |
| 9 | Verification | Re-fetch every source and exact-match every quote; recompute every number; red-team: the strongest innocent explanation for each discrepancy | — |
| 10 | Memo | 7 sections rendered from the ledger, with open questions and a source list, as a Google Doc | 1–7 |

---

## 6. What we take from the five plugins

Copied and adapted, not referenced loosely. Paths are inside the uploaded packs.

| Component | From | Adapted into |
|---|---|---|
| Claim ledger, source tiers, recompute-every-figure, "fabricated citation = fail" | InvestSkill `fact-check` | Stage 9 and the ledger schema |
| Confidence scoring rubric, capped by fact-check results | InvestSkill `result-validator` | Stage 9 quality score on each memo |
| Keyless EDGAR recipe (CIK, submissions, archives, XBRL) | InvestSkill `financial-report-analyst`, `10k-digest`, `scripts/lib/edgar.js` | `edgar.py`, Stage 4 |
| Prior-year promise tracker; risk-factor diff; hedging-language flags | InvestSkill `10k-digest`, `financial-report-analyst` | Stage 5 statement-change tracking |
| Form 4 transaction codes, 10b5-1 handling | InvestSkill `insider-trading` | Stage 6 |
| Thesis-killers and "show the downside math" | InvestSkill `bear-case` | Stage 9 innocent-explanation pass (inverted) |
| Claim types, evidence standards, confidence vs likelihood, source families | intel `references/evidence-standards` | Ledger fields and doc language |
| Competing hypotheses | intel `intel-diagnose` | Stage 2 trigger attribution, Layer 1 step 4 |
| Source evaluation, tracing a figure to its origin, negative evidence | intel `intel-research` | Stages 2, 7 |
| Adversarial review | intel `intel-red-team` | Stage 9 |
| Executive writing standards | intel `intel-brief` | Triage doc and memo prose |
| Risk-factor and 90-day 8-K search pattern; governance searches | Bigdata.com `bigdata-risk-assessment` | Stages 4, 6 |
| Mandatory litigation query; six-category news sweep | Bigdata.com `bigdata-company-brief` | Layer 1 step 4, Stage 2 |
| Regulatory, legal and refinancing catalyst queries | Bigdata.com `bigdata-catalyst-monitor` | Stages 2, 7 |
| Transcript pulls; guidance now vs prior guidance | Bigdata.com `bigdata-earnings-digest`, `-earnings-reaction` | Stages 4, 5 |
| Restatement, revenue recognition, related-party searches | Bigdata.com `bigdata-earnings-quality-screen` | Stage 6 |
| Query discipline (one entity, topic and period per search) | Bigdata.com plugin conventions | All search stages |
| Pass/fail screen against fixed criteria | financial-services `deal-screening` | Layer 1 disposition |
| Structured extraction from documents | financial-services `kyc-doc-parse`, `datapack-builder` | Stage 4 statement extraction |
| Data-currency hard check; numbers read only from saved files | financial-services `earnings-analysis`, S&P `tear-sheet` | Stages 1, 10 |
| Number consistency across a document | financial-services `ib-check-deck` | Stage 9 |
| Open-questions list | financial-services `dd-checklist` | Memo open questions |
| Regression and correlation code patterns | finance-skills `stock-correlation`, `stock-liquidity` | `prices.py` event study (known bugs fixed) |

Not taken: buy/sell signals, valuation models, technical analysis, social readers, MSFT 365 tooling.

---

## 7. Plugin layout

```
research-analyst/
  .claude-plugin/plugin.json
  commands/
    triage.md               # /triage <screener output>  → Layer 1 Google Doc
    investigate.md          # /investigate <ticker> <date> → Layer 2 memo
  skills/
    triage/                 # Layer 1 orchestrator
    market-event/           # §3 drop standard
    trigger-finder/
    disclosure-history/     # stages 4-5
    knowledge-indicators/
    external-evidence/
    timeline/
    verify/
    memo-writer/
  scripts/
    prices.py               # Yahoo + TradingView, cache, event study
    edgar.py                # EDGAR filings, full-text search, XBRL, Form 4
    courts.py               # CourtListener helpers
    ledger.py               # schema; blocks any doc line without a source
  references/
    country-sources.md      # §2 per country
    trigger-tiers.md        # §4.1
    statement-types.md
    evidence-standards.md   # from intel
    language-rules.md
```

---

## 8. Build order

| Step | Output | Done when |
|---|---|---|
| 1 | `prices.py` + drop standard | Classifies a sample of real screener rows across all 4 countries; numbers reproduce |
| 2 | Layer 1 triage, end to end | One real screener run produces the triage Google Doc |
| 3 | Stages 1–8 | Two test cases fully evidenced (one US, one non-US) |
| 4 | Verification (stage 9) | Every quote re-matches; every number recomputes; zero unsourced lines |
| 5 | Memo writer (stage 10) | 7-section Google Doc |
| 6 | v2 tuning on Andrew's past memos | Template, thresholds and tiers calibrated |

## 9. Still open

1. Google Docs output needs the Google Drive connector connected in the session that runs the plugin.
2. Approval of the optional sources in §2.4.
3. The JBG Smith judgment date and the mining-company name, to use as the first two test cases.
