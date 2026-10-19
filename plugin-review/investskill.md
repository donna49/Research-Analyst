# InvestSkill (yennanliu/InvestSkill v1.13.0): digest

Reviewed from the local unzip at `.../scratchpad/plugins/InvestSkill-main/InvestSkill-main`. I read every SKILL.md (34) in full, plus the manifests, README, CLAUDE.md, and the parts of `scripts/`, `install.sh` and `.github/workflows/` that matter for security. **No code was executed.**

## 1. Overview and design philosophy

InvestSkill is a plugin made only of prompts. It has no runtime, no MCP server, no hooks, and no API keys. The repo calls it "30 analysis frameworks + 3 aliases + 1 output tool" for US equities. Each skill is a long markdown framework: sections to fill, formulas, threshold tables and a weighted 0–10 score. Every skill ends with a uniform contract:
- **(a)** a `Data & Sources` header at the top (As of / Source / Retrieval = pasted | web/tool | model memory / Confidence). "Model memory" must be paired with LOW confidence.
- **(b)** a **Thesis Invalidation** section with numeric triggers and re-run conditions.
- **(c)** a box-drawn **INVESTMENT SIGNAL** block (Signal / Confidence / Horizon / Score / Action / Conviction) and a disclaimer.

CI checks the contract: `check-skill-contract.js`, golden-output parsing in `tests/llm-golden`, prompt token budgets, and a live Claude eval run against a fictional company, ZEPH. The philosophy is structure and provenance discipline rather than data access. The plugin brings the method; the host or user brings the data (web search, pasted filings, or a keyless SEC EDGAR "recipe"). The newer skills (fact-check, thesis-tracker, risk-stress-test, earnings-preview, etf-analysis, tax-lens, position-ladder, learning-coach) are much more rigorous than the original ones (insider, institutional, options, sector, technical), which read like generic checklists. The skills also ship as AI-agnostic copies in `prompts/*.md`.

**Manifests.** `.claude-plugin/marketplace.json` defines marketplace `invest-skill` with one plugin, `us-stock-analysis` (category finance, MIT). `plugins/us-stock-analysis/.claude-plugin/plugin.json` has no hooks, no mcpServers and no commands; skills are found automatically from `skills/`. The plugin README is stale: it lists only 6 skills.

## 2. Skill table (34 directories)

Abbreviations:
- **DV**: the standard "fetch live price via web search or ask the user; never use training data; show a stale-data warning" preamble plus the Data & Sources header.
- **Sig**: the standard signal block.

Unless a row says otherwise, data sources are "web search or user paste". No skill calls an API, uses an MCP server, or needs a key.

| Skill | Produces | Inputs | Data sources expected | Output | Notable methodology |
|---|---|---|---|---|---|
| stock-eval | Full single-stock fundamental and valuation evaluation | Ticker | DV; consensus/estimates (unspecified vendor) | MD tables + Sig | Piotroski F-Score (9 tests), DuPont 3/5-factor, CCC, DOL, ROIC/WACC/EVA, 10-yr DCF + 5×5 sensitivity, MoS bands (>30% compelling), ERM revision score, Net Debt/EBITDA bands |
| stock-valuation | Multi-method intrinsic value, football field | Ticker, flags `--methods`, `--growth/--wacc/--terminal`, `--peers` | DV; peers, consensus | MD + Sig | DCF (20/60/20 bull/base/bear), CCA (25% each of EV/Rev, EV/EBITDA, fwd P/E, EV/FCF), P/E, Residual Income (justified P/B), TV>75–80% flag, SBC-adjusted FCF. "Asset-based NAV" is named for real estate but has no method |
| fundamental-analysis | **Alias** of stock-eval; ratio cheat-sheet only | n/a | n/a | Sig | n/a |
| dcf-valuation | **Alias** of stock-valuation; WACC/TV quick reference | n/a | n/a | Sig | WACC ranges by risk; never g>WACC |
| research-bundle | **Deprecated**; points to full-report | n/a | n/a | Sig | 25/25/20/15/15 composite; conflict rules (e.g. recession >60% overrides bullish). Its depth lists **contradict** full-report's |
| full-report | Orchestrator; standalone HTML report | Ticker, `--depth quick(5)/standard(10)/comprehensive(15)`, `--lang`, `--output` | All modules' sources | **Writes** `output/<T>_report_<date>.html` (Chart.js CDN) | Composite: Business Quality 25 / Valuation 25 / Market Signals 20 / Technical 15 / Risk 15; modules not run default to 5.0; must run fact-check then result-validator before shipping |
| technical-analysis | MA table (30/60/90/200/365), mandatory trade rec (entry/target/stop), MTF, Volume Profile, Ichimoku, P/C, GEX | Ticker, `--chart` | Price history; says "**retrieve or estimate** recent price data" | ASCII charts, tables, Sig | MA stack rules, MTF 3/3 alignment ("never trade ≤1/3"), Ichimoku 5-condition grade |
| economics-analysis | Macro regime and recession probability | None | FRED/BLS/BEA/ISM/NY Fed | MD + Sig | Yield curve (3M10Y), Sahm ≥0.5pp, LEI, IG/HY OAS bands, MOVE, DXY thresholds, composite recession zones |
| sector-analysis | 11-sector rotation ranking | None | Sector ETFs; FactSet/Bloomberg named | MD + Sig | Hard-coded P/E, P/S and yield ranges, seasonality calendar, qualitative correlation matrix, 4-factor momentum rank; REITs on P/FFO 14–22x |
| portfolio-review | Allocation, risk and tax review of holdings | Pasted holdings | User data | 10-section report + Sig | Concentration scores, ENP=1/Σw², diversification ratio, parametric VaR, TLH table, 6-factor tilt, rebalance flowchart |
| risk-stress-test | Risk report / Risk Budget Score | Holdings, β, σ, ADV, drawdown budget | User paste; sector-ETF proxies flagged | MD + Sig | Scenario replay (2008/2020/2022/2025 tariff), VaR/CVaR 95/99, crisis-correlation σ (ρ→0.85), days-to-exit at 20% ADV, weighted 35/20/15/15/10/5 score |
| financial-report-analyst | 10-K/10-Q/8-K/proxy red-flag analysis | Paste or ticker + form, `--section`, `--compare-prior` | **Keyless EDGAR recipe** (company_tickers.json → submissions → Archives → XBRL companyfacts) | Dashboard + Accounting Quality /21 + Sig | DSO/DIO, FCF conversion >80%, SBC >5% of revenue, goodwill >30% of assets, risk-factor diff, hedging-language flags |
| 10k-digest | Structured 10-K digest (EN or zh-TW) | Ticker/FY or paste, `--output` | EDGAR recipe; `scripts/fetch-edgar.js` as fallback | MD (may **write** a file) + Sig | Section summaries by Item, metrics table, **Prior-Year Promise Tracker**, reference list with accession numbers |
| earnings-call-analysis | Tone, guidance delta, Q&A, red flags | Transcript paste or URL | Seeking Alpha, IR, "8-K transcripts" (wrong; see §5) | 10-section MD + Sig | Hedging-language taxonomy, guidance credibility |
| earnings-preview | Pre-print expectations and scenario grid | Ticker, confirmed date, consensus, straddle, 8-quarter history, position | IR, options chain, consensus | MD + Sig | Expectation stack (whisper must be labeled an estimate), beat-and-drop count, implied move with non-event-day variance stripped, reverse-multiple "priced-in" check, Earnings Setup Score |
| catalyst-calendar | 90-day event map and ASCII heat map | Ticker(s), `--days`, `--focus` | Earnings and FOMC calendars, options | MD + Sig | Implied move = straddle/price, EV ranking, catalyst stacking, debt-maturity windows (Net Debt/EBITDA >3x) |
| insider-trading | Form 4 sentiment | Ticker, `--period`, `--data` | EDGAR Form 4, OpenInsider | MD + Sig | Net sentiment = (B−S)/(B+S) bands; P/S/M/F/A/G codes; 10b5-1 discount |
| institutional-ownership | 13F flows, smart money | Ticker, `--track` | EDGAR 13F, WhaleWisdom | MD + Sig | Concentration and HHI, retention; 13D/G deadlines updated for the 2024 rule. **Sample tables contain realistic-looking fake rows** (e.g. Buffett, Burry) |
| short-interest | Squeeze Score 0–10 | Ticker, `--scan` | FINRA, borrow-rate sites | MD + Sig | Additive points (SI>20% +3, DTC>10 +2, …) and borrow tiers |
| options-analysis | Greeks, IV regime, strategy picker | Ticker, `--greeks/--strategy/--earnings/--iv` | Broker or options vendors | MD + Sig | IVR/IVP bands, strategy matrix, sizing (undefined-risk sized on a 2σ stress loss) |
| dividend-analysis | Actually a **capital allocation** analysis | Ticker, `--portfolio`, `--sector` | Filings, rating agencies | 13-section MD + Sig | Dividend Safety 0–100 (FCF payout, coverage, Debt/EBITDA, stability, streak), REIT AFFO payout bands, Chowder rule, M&A overpaying score, sector leverage bands (REITs 4–6x "conservative") |
| competitor-analysis | Moat score | Ticker, `--peers` | 10-K, Gartner, G2, Glassdoor, patents | MD + Sig | Morningstar-style 5 moat sources, Porter 1–5 → attractiveness, HHI bands, Moat composite 25/20/20/15/10/10 |
| industry-map | Value-chain directed graph | Theme, ticker or layer | Web | **Mermaid** flowchart + tables + Sig | Bottleneck Score (scarcity, substitutability, switching, inelasticity), value-migration thesis, idea buckets |
| stock-screener | Ranked multi-ticker leaderboard | Tickers, `--sector`, `--index`, filters | Web | Table + top-3 / bottom-3 + Sig | 5 linear-scaled dimensions: Val 20 / Qual 25 / Mom 20 / Sent 15 / Growth 20 |
| bear-case | Deliberate one-sided short thesis | Ticker or a pasted bull thesis | DV | MD + Sig (inverted mapping) | 6-pillar Bear Strength 0–10, reverse DCF, Beneish-style flags, mandatory Thesis-Killers, downside target with math shown |
| fact-check | Claim ledger, corrected and cited report, Verification Score | Any report + sources | Tier-1 primary only (EDGAR, IR, FRED, issuer), with the full EDGAR recipe and a 13F-by-manager-CIK caveat | Ledger + corrected copy + References + Sig | Verdicts ✅⚠️❓🔁🕒; recompute every derived figure; hard caps (a fabricated citation scores 0; a signal-driving mismatch >5% caps at 4.0); `--cite-only/--recompute/--diff` |
| result-validator | Confidence score 0–100 for any output | Pasted analysis (+ fact-check ledger) | n/a | Scorecard + adjusted signal | 5×20-point dimensions; missing header caps Data Quality at 10; Data Quality bounded by the fact-check score |
| thesis-tracker | Saved thesis "contract" and status checks | Ticker + the user's own thesis; `--update/--review/--close` | KPIs from filings | **Writes** `output/thesis/<T>.md` + Sig | 3–5 KPIs with thresholds, triggers, pre-mortem, INTACT/WEAKENED/BROKEN/INSUFFICIENT EVIDENCE rule table, Thesis Health Score |
| position-ladder | Staged entry, floor/ceiling, trim/re-add cycle | Holding, ceiling, portfolio size | Price, ATR | Tables + Sig | ATR rung spacing, blended cost math (worked example checks out), wash-sale and FIFO warnings, buy-and-hold reality check, Ladder Suitability Score |
| tax-lens | US tax mechanics; `--non-us` module | Lots, dates, bracket, residency | IRS Pub 550/519/559, W-8BEN | MD + Sig | 61-day wash timeline, qualified-dividend test, HIFO vs FIFO, account placement, tax-drag formula, NRA withholding / $60k estate exposure / UCITS. No 1031 coverage |
| etf-analysis | ETF Fitness Score | ETF(s), holdings, purchase size | Issuer factsheet and prospectus | MD + Sig | Tracking difference vs tracking error, overlap = Σmin(w), structure caps (leveraged ≤3.0, ETN ≤5.0), renormalized weights when inputs are missing |
| learning-coach | Mentor-style explanation, Socratic questions, quizzes | Pasted output, `--level`, `--quiz`, `--lang zh-TW` | Never re-fetches | Explanation cards + mirrored Sig | Links to the author's GitHub Pages lessons |
| chart-master | Mermaid, ASCII and Chart.js chart snippets | Data/analysis | n/a | Code blocks + Sig | Uses an **unversioned** `cdn.jsdelivr.net/npm/chart.js`; the RSI annotation needs a plugin that is never loaded; sample data looks like real AAPL revenue |
| report-generator | Standalone HTML/PDF report template | Prior output, JSON or CSV | n/a | HTML (Chart.js 4.4.0 CDN + Google Fonts) | Template hard-codes a BULLISH / HIGH / BUY 8.4 signal and placeholder revenue arrays. It is the only skill with no closing Thesis Invalidation |

## 3. How the skills chain

- **full-report** is the orchestrator. Its 5 phases run in order and each phase feeds the next:
  1. Business: stock-eval, competitor-analysis
  2. Valuation: stock-valuation
  3. Signals: insider-trading, institutional-ownership, earnings-call-analysis
  4. Technical: technical-analysis, sector-analysis
  5. Risk: short-interest, options-analysis, economics-analysis, financial-report-analyst, bear-case, catalyst-calendar

  The bear-case downside target sets the Bear scenario, and the catalyst dates feed the monitoring plan. Required finish: **fact-check → result-validator** (fact-check's ledger caps the validator's Data Quality score), with both scores printed in the footer. research-bundle is a deprecated alias of it, and its depth module lists disagree with full-report's.
- **Verification layer:** fact-check checks the inputs (claim level, primary sources only). result-validator checks the reasoning (methodology, consistency, risk coverage). learning-coach explains the result and never changes the verdict.
- **Position lifecycle:**
  1. stock-eval and bear-case produce the thesis and its killers.
  2. thesis-tracker records the KPIs and triggers.
  3. earnings-preview fixes the plan before each print; earnings-call-analysis reviews it afterwards; then `thesis-tracker --update`.
  4. position-ladder handles sizing, honoring thesis-tracker's status gate.
  5. tax-lens covers wash sales and lots; risk-stress-test and portfolio-review cover book-level risk.
- **Discovery:** industry-map (find nodes) → stock-screener (rank them) → competitor-analysis (moat) → bear-case.
- **Output:** any skill → chart-master or report-generator.
- **Stale cross-references:** competitor-analysis and position-ladder still point to the aliases `/dcf-valuation` and `/fundamental-analysis`. thesis-tracker refers to a `trade-postmortem` skill that does not exist.

## 4. Scripts, hooks, network, file writes, security

- **Hooks, MCP, auto-executed code: none.** `plugin.json` declares no hooks or servers. There are no `preinstall`, `postinstall` or `prepare` npm scripts. I scanned all SKILL.md files for zero-width or bidi characters and Unicode tag characters and found none. The only HTML comments are the layout comments inside report-generator's template.
- **Prompt-injection posture:** I found no hidden instructions. The skills do tell the model to act:
  - fetch from sec.gov / data.sec.gov / Seeking Alpha, and run web searches, when the host allows it
  - **write files**: `output/<T>_report_<date>.html` (full-report), `output/thesis/<T>.md` (thesis-tracker, which also reads every file in that folder on `--review`), and an optional `--output` markdown (10k-digest)
  - **tell the user to run** `node scripts/fetch-edgar.js` / `fetch-fundamentals.js`

  The skills also ingest untrusted text (transcripts, pasted reports), and nothing tells the model to treat that text as data, not instructions.
- **Generated HTML** loads Chart.js from jsDelivr (pinned to 4.4.0 in report-generator, **unpinned** in chart-master) and Inter / JetBrains Mono from Google Fonts. Opening a report therefore makes third-party requests, a small privacy and supply-chain leak. No telemetry is built in, though the skills link to the author's GitHub Pages site.
- **Optional scripts** (outside the plugin; Node 18 global fetch):
  - `scripts/lib/edgar.js`, `fetch-edgar.js` and `fetch-fundamentals.js` call only sec.gov / data.sec.gov. They pace requests at 150 ms, send the `EDGAR_USER_AGENT` header (default `InvestSkill/<ver> (+github url)`), and write to `data/filings/<T>/` and `data/fixtures/<T>.md`. They look clean.
  - `scripts/claude-complete.js` needs `@anthropic-ai/sdk` and `ANTHROPIC_API_KEY` and is used only by CI's `llm-eval.yml`.
  - `setup-verify.js` uses `execSync` to run `claude /plugin list`. The release, publish and site-review scripts use git and `execSync`; `site-review.js` deletes old `qa/` reports.
  - `publish-gemini.js` points at a `registry.gemini.ai` URL that looks fictional.
- **install.sh:** the README path is `curl … main/install.sh | bash`. The script downloads a codeload tarball of an **unpinned `main`** (`-r` can pin a ref) with no checksum. It copies prompts to `.investskill/prompts/` and `.claude/skills/`, and appends marked blocks to CLAUDE.md, AGENTS.md, GEMINI.md or copilot-instructions. `rm -rf` is limited to its own mktemp directory. Installing via the marketplace avoids all of this.
- **CI:** auto-deploy, release and site-review hold `contents: write` and push to main and tags (they include a daily bot commit). This matters only for trusting future upstream versions.

## 5. Quality assessment

**Strengths**
- The provenance contract (Data & Sources header, "model memory ⇒ LOW", show conflicting sources and never average them) is better than most finance prompt packs.
- fact-check is excellent and transferable: claim ledger, source tiers, recomputing derived figures, fiscal-year mismatch heuristics, and a zero score for fabricated citations.
- The keyless EDGAR recipe is accurate, including CIK zero-padding, the aligned `filings.recent` arrays, the companyfacts cross-check, and 13F filed under the manager's CIK.
- The newer skills state formulas and show the arithmetic. The position-ladder worked example is internally consistent.
- Signal mappings for non-directional skills (risk, tax, ETF, thesis) are spelled out explicitly. Thesis Invalidation triggers carry numeric thresholds.

**Weaknesses and structural issues**
- **Everything ends in BUY/HOLD/SELL** plus a 0–10 score, even descriptive work. A firm that sells data cannot ship that as-is, and it creates false precision. Many weights (for example the screener's linear scales and the Moat Score) are arbitrary.
- **No real data path.** "Use web search or ask the user" is the whole data layer. Nearly every table assumes consensus, short borrow, options chains, 13F aggregates and peer multiples that a web search will only partly fill, so models will fill gaps from memory. The DV preamble only *warns*; it cannot prevent this.
- Very long prompts (up to about 34 KB each) and template-heavy output: many empty tables invite padding.
- Hard-coded "typical" bands (sector P/E ranges, WACC 6–20% tiers, REIT leverage 4–6x, credit-spread bands, seasonality, sector correlations) are unsourced and will be quoted as fact.

**Stale or hallucination-prone guidance to watch**
- technical-analysis: "Retrieve **or estimate** recent price data", then *always* produce an entry/target/stop table. That is the most hallucination-prone instruction in the pack. Its sample recommendations use plausible-looking real-ticker prices (AAPL $185, TSLA $310, MSFT $415).
- earnings-call-analysis claims 8-K filings contain "official transcripts filed within 4 days". Item 2.02 usually carries the press release, not the transcript.
- economics-analysis:
  - The TED spread is defined on LIBOR (discontinued); it says "now SOFR", but that is not a TED spread.
  - Its historical table lists "2022–2023" as a recession, with "Sahm: No (so far)".
  - Its claim that the Sahm rule "triggered in every US recession since 1970" ignores the 2024 false-positive debate.
- short-interest:
  - It cites "FINRA Rule 4560" for daily short volume; 4560 is the short-interest reporting rule.
  - Iborrowdesk "TD Ameritrade" is gone.
  - It lists Hindenburg as an active short seller.
  - The FINRA URL given is the short-sale *volume* page.
- Fabrication magnets: stock-valuation's peer example includes TWTR (delisted); institutional-ownership has realistic fake 13F rows (Buffett $7.5B, Burry exit); chart-master's sample data looks like real AAPL revenue; report-generator's template defaults to BULLISH 8.4.
- Small errors:
  - stock-screener: "12M … same scale as 12M".
  - options: the claim that straddle/price is "68% probability" (it is about 0.8σ).
  - sector-analysis: an unsourced "Google/Meta ad revenue dropped 15–25% in prior downturns".
  - chart-master: references an annotation plugin it never loads.
  - catalyst-calendar / earnings-preview: "beat rate" depends on consensus history the model cannot see.

