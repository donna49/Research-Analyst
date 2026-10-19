# Digest: Bigdata.com plugin marketplace (RavenPack), v1.3.0

Source reviewed: `.../scratchpad/plugins/bigdata-plugins-marketplace-main/bigdata-plugins-marketplace-main` (all manifests, both READMEs, llms-install.md, server.json, .mcp.json, Cowork packaging, 3 build scripts, all 28 SKILL.md files, report templates, and the references/ files; Python scripts inspected statically, nothing executed).

## 1. Overview, MCP server and auth

- **What it is:** RavenPack's official marketplace repo for **Bigdata.com**, a hosted, paid financial content layer. It contains one plugin, `bigdata-com`, with 28 skills that are prompt-only workflows. Each skill is a SKILL.md, a report template, framework references and optional stdlib Python calculators. It also holds the MCP Registry entry (`server.json`, name `com.bigdata/bigdata-mcp`) and a Microsoft 365 Copilot Cowork package.
- **MCP server:** remote Streamable HTTP at `https://mcp.bigdata.com/`. Nothing runs locally. `plugins/bigdata-com/.mcp.json` declares `{"bigdata.com": {"type":"http","url":"https://mcp.bigdata.com"}}` with no header, which means OAuth by default (it also lacks the trailing slash that the other configs use).
- **Auth:** OAuth works natively in Claude.ai/Desktop, ChatGPT and Copilot Studio. Every other client sends an API key in the `x-api-key` header (keys come from platform.bigdata.com/api-keys), or uses a custom OAuth client from platform.bigdata.com/oauth-clients. **An active paid Bigdata.com account is required.** LICENSE is proprietary ("Master Agreement and Order Schedule"; trials fall under NDA/Trial Agreement).
- **Tools the skills name exactly** (6 in total):
  - `find_securities`: resolves a name, ticker, ISIN, CUSIP or SEDOL to a RavenPack `entity_id`. It is the prerequisite for the next three.
  - `bigdata_company_tearsheet`: financials, estimates, consensus, surprises, multiples, segments, sentiment, insider/ownership/short fields "where exposed", geographic revenue and ESG.
  - `bigdata_events_calendar`: earnings dates and conferences.
  - `bigdata_search`: cited similarity search over news, SEC filings, transcripts, broker research, podcasts, expert interviews and the user's uploaded docs. Returns a `url` per document.
  - `bigdata_country_tearsheet`: macro data, calendar and G7 comparison.
  - `search` / `fetch`: generic tools that do **not** accept `plugin_slug`.
- **Tools named only generically in the README** (exact names not in the repo; call `tools/list`): market, ETF, sentiment and portfolio tearsheets; a company screener (market cap, price, beta, sector, country, exchange); a macro release calendar; private-content connectors, tags, document listing, fetch and **upload**; and "analysis code" on Bigdata data for prices, returns, peers and charts.
- **Hosts:** Claude Code (`claude mcp add --transport http bigdata_com https://mcp.bigdata.com/ --header "x-api-key: ..."`), Cursor, VS Code/Copilot, Copilot CLI, Codex, Snowflake Cortex, Qwen, Grok and Cline (via `npx mcp-remote`). Each skill also carries `agents/openai.yaml` for ChatGPT/Codex, with `allow_implicit_invocation: true` on all 28.

## 2. Skill table

Every company skill starts with `find_securities` (and asks the user to disambiguate if a name is ambiguous), then calls `bigdata_company_tearsheet`. "Searches" counts `bigdata_search` calls. Every output is Markdown following `assets/report-template.md`, ending with Sources, the "Powered by Bigdata.com" line and the Disclaimer, with an offer of .docx or a deck.

| Skill | Trigger / purpose | Workflow (tool calls) | Output | Notable methodology |
|---|---|---|---|---|
| `bigdata` (router) | Any Bigdata task with no specific skill; "what can Bigdata do"; build your own skill | Resolve → plan data needs → gather only that → cite | Answer / Findings / What It Means / **Gaps** / Sources | "Prefer over web search"; offers once to turn a repeated task into a user skill (`references/skill-builder.md`) |
| catalyst-monitor | "What's coming / what could move X" | resolve → events_calendar (2–4 quarters) → tearsheet (what's priced) → **6–8 searches** (FDA/FTC, trial dates, debt maturities/refi, contract renewals, patent, index/lock-up) | Catalysts ranked by impact plus a chronological calendar | Each item has a date or window, direction, magnitude tied to a value driver, and separate date vs outcome confidence; undated risks are excluded |
| company-brief | 30-day "catch me up" | resolve → tearsheet → ≥1 competitive search → **5–10 searches**, including a mandatory litigation query | 6 categories (results, product, M&A, reg/legal, management, other) plus top 2–3 | Primary/secondary tagging; "so what" at the mechanism level ("+Ybps margin"); empty categories marked; brief Porter context |
| country-analysis | One economy, institutional/IMF-style | country_tearsheet, then **~35 query templates in 9 steps** (falls back to search, one indicator per query) | Long report with a pillar-structured policy-recommendations section | Structural history, debt composition and servicing, tax-to-GDP, PFM, macro and micro labor, FDI |
| country-sector-analysis | Sector × country ("US tech", "China EV") | ~15 searches; 5–10 domiciled leaders via find_securities + tearsheet + events_calendar; country_tearsheet | Macro + sector + leaders + policy + valuation tables | Geographic revenue must confirm exposure; valuation vs **global** peers; subsidies, tariffs, FDI rules |
| cross-sector | Rotation, sectors vs sectors | 3 searches per sector; 3–5 bellwethers per sector (tearsheets); cycle and ROIC searches | Like-for-like table plus an OW/UW call | Peak / mid / trough earnings-power read ("low P/E on peak earnings is not cheap") |
| earnings-digest | Post-print deep dive | resolve → tearsheet → events_calendar → **5–7 searches** (transcript, analyst reactions, guidance, legal) | Mandatory tables: quality signals with a "watch for" column, positioning, scenarios | Surprise in σ terms; sustainable vs one-time; bull **and** bear thesis check; post-print scenario EV with math shown |
| earnings-preview | Pre-print setup | resolve → tearsheet → quality screen → events_calendar → **≥8–10 searches over 60–90 days** (core, reg/legal, Form 4/13F/short/options) | EPIC table, priced-in table, FaVeS, bull/base/bear with EV math | "What's priced in" is built before bull/bear; missing positioning cells say "Not available in data" |
| earnings-quality-screen | "Are X's earnings real" | resolve → tearsheet (4–8 quarters or 3 years) → **~5 searches** (rev-rec, capitalization, restatement, related party, non-GAAP) | Graded High / Adequate / Questionable / Poor | OCF/NI and FCF/NI, BS and CF accrual ratios, DSO/DIO/DPO, optional Beneish M (8 inputs shown); diagnostic, not accusatory |
| earnings-reaction | Decision note after a print | resolve → tearsheet → calendar → **3–5 searches** | Short note with an action and the next date | Thesis is one of Intact / Strengthened / Weakened / Broken; prior vs new guidance; explicit estimate and price-target revisions |
| g7-comparison | G7 benchmarking | country_tearsheet + ~15 searches | 7-country table plus a ranked view | Euro-area members distinguished by fiscal position and pricing; central-bank divergence as the headline |
| investment-memo | Full thesis, "should I buy X" | resolve, tearsheet, searches (unbudgeted), events_calendar | Recommendation, conviction 1–5, scenarios | EPIC → FaVeS → quality and moat **before** valuation; method chosen by type (REIT = NAV, P/AFFO, implied cap rate; bank = P/TBV, DDM); 5 optional scripts |
| moat-governance-review | Moat durability and stewardship | resolve → tearsheet → ~8 searches | Moat None / Narrow / Wide plus trend; management Strong / Adequate / Weak | ROIC vs WACC over 5–10 years is mandatory; capital allocation judged on returns achieved; governance graded separately |
| peer-comparables | Comps / relative value | resolve subject + **5–8 peers**, a tearsheet each, 2 validation searches | Comps table with median and quartile | Peer rationale **and exclusions** stated; premium split into justified vs unexplained; sector multiples (P/AFFO, P/TBV) |
| post-ipo-day1 | IPO debut | Bigdata tools + **web search** for price and volume | 4–7 page note | Float mechanics, stabilization, quiet period; no recommendation |
| post-ipo-day14 | NASDAQ-100 fast-track | same + web search for Nasdaq methodology and QQQ AUM | 4–7 pages | Index weight × AUM / price → days-to-cover vs ADV; rules must be cited |
| post-ipo-day179 | 180-day lock-up | same + filings | 4–7 pages | Unlock / ADV = days-to-trade; 10b5-1 plans, short interest and borrow |
| post-ipo-day365 | Founder lock-up | same | 4–7 pages | Float-adjusted index re-weight demand netted against supply; dual-class |
| pre-ipo-analysis | S-1/F-1 note | Web for filing terms, plus Bigdata search and sentiment; web-only fallback | 6–10 pages | "Not yet disclosed" instead of estimates; balanced, no call |
| quick-take | One-page PM view | resolve → tearsheet → **2–4 searches, then stop** | One page | 2–3 drivers, a stated view, a falsifiable "what would change it", next dated catalyst |
| regional-comparison | US vs Europe vs Asia | country_tearsheet + ~13 searches | Allocation call | Cross-asset (equity, rates, FX) per region |
| risk-assessment | Rated risk map | resolve → tearsheet → 10-K risk-factor search → 8-K (90 days) search → **4–6 news searches** → 4 governance searches | 6-category likelihood × impact matrix plus a scenario bridge | Numeric likelihood and impact bands (e.g. High impact = >10% of revenue); simplified Altman Z when levered; mitigation status |
| scenario-analysis | Bull/base/bear with EV | resolve → tearsheet (spot) → 3 debate searches | Line-item assumption table, EV, skew | 2–3 swing variables only; base case ≈ consensus or the gap explained; up/down ratio; probability triggers |
| sector-analysis | One sector | **5–10 searches**, 5–10 bellwethers (tearsheets), events_calendar | OW / N / UW plus top picks | GICS KPI lens (REITs: AFFO, NAV, cap rate vs bonds, SS-NOI); early / mid / late cycle |
| sector-playbook | "How to invest sector X" | loads the sector reference first, then 3+ debate searches, tearsheets, calendar | KPI framework, debates, sub-industry map, own / avoid / watch | 7 sector reference files, including a strong `reits.md` and `financials-banks.md` |
| thematic-research | Cross-sector theme | **5–10 searches** + tearsheets + country_tearsheet | Beneficiaries **and** losers, implementation | Scope stated up front; invalidation conditions |
| valuation-snapshot | "What is X worth" | resolve → tearsheet → peer search | Cheap / fair / rich | Reverse-DCF reasoning without building a model; multiples fit to the business type |
| variant-perception | Consensus gap | resolve → tearsheet → 2+ consensus searches | Falsifiable variant statement | All four EPIC tests must pass, else "no variant view" is the honest null; names why the mispricing persists |

## 3. Shared conventions

- **Telemetry tag:** every Bigdata tool call must pass `plugin_slug: "<skill-name>"`, except `search` and `fetch`. User-built skills use `"bigdata-user"`. The vendor can therefore see which workflow generated each call.
- **Citations:** inline `[1]`, `[2]` immediately after each claim, hyperlinked to the document URL returned by `bigdata_search` (skill-builder says to keep the passage number in the link). A numbered **Sources** list or table follows (name, date in MMM DD, YYYY, URL). Figures computed from non-document data (prices, estimates, screens) go in one "**Data:** Bigdata.com … (retrieved <date>)" line.
- **Branding:** the closing "**Powered by Bigdata.com** - https://bigdata.com" line and a fixed **Disclaimer** (not investment advice) are mandatory and verbatim. `build-skill.sh` fails a build when the template lacks the footer. Content must be branded exactly "Bigdata.com". IPO notes add a "Prepared with Claude" cover line.
- **Query discipline:** natural-language queries naming the entity plus a time phrase ("last 30 days", "2026 outlook"); one focus and one period per call; country work searches one indicator per query. Search budgets appear per skill. Resolve first and ask on ambiguity. Ask the user rather than silently widening the window when news is thin.
- **Analytic discipline:** facts kept apart from analysis; the "PM test" (what's different / what matters / what to do, no position sizing); the top 2–3 drivers instead of equal-weighting everything; "Not available" cells instead of dropped rows; a gaps section; no filling from memory or web search unless the user is told. The router skill says do not answer from web search unless the user asks. IPO skills explicitly allow web search for prices and index rules.
- **Upload back to the corpus:** no shipped skill writes to Bigdata. Only `bigdata/references/skill-builder.md` "Recurring skills" tells user-built scheduled skills to **save each deliverable to the user's Bigdata.com documents with fixed tags** (e.g. `skill:weekly-holdings-review`, `week:2026-10-12`), recall the last 1–2 runs by tag to lead with what changed, and exclude its own saved runs from news results. It asks the user whether to save always, ask each run, or never. User-built skills must describe data needs instead of naming tools, so they survive tool renames.

## 4. Scripts, hooks, network, security

- **No hooks**, no commands, no agents/subagents, and nothing auto-executed. The only network endpoint is `https://mcp.bigdata.com/`, plus the Cowork `validDomains` (`app.bigdata.com`, `content.bigdata.com`, `files.prod.nvirginia.common.ravenpack.com`, `cdn.prod.nvirginia.common.ravenpack.com`) for MCP widgets.
- **Skill scripts** (5 unique files, duplicated across skills: `dcf_model.py`, `reverse_dcf.py`, `earnings_quality.py`, `peer_comparables.py`, `scenario_probability.py` under `plugins/bigdata-com/skills/*/scripts/`): imports are stdlib only (`typing`, `dataclasses`, `math`, `statistics`). There is no file I/O, subprocess, eval or networking. `__main__` blocks print hard-coded examples. Every skill says to run them only when the user explicitly asks. `scenario_probability.py` includes **Kelly-criterion position sizing**, which conflicts with the skills' "no position sizing" rule.
- **Packaging scripts** (`packaging/bigdata-com/scripts/build-plugin.sh`, `build-skill.sh`, `build-cowork.sh`) are maintainer-only zip and validate tools using local `python3` heredocs. No network. Not needed to use the plugin.
- `scripts/validate-template.mjs` is **0 bytes**. `server.json` is only metadata.
- `packaging/bigdata-com/cowork/manifest.json` contains an OAuth `referenceId`, a base64 Teams Developer Portal identifier that the README says is not a secret. No credentials anywhere. The SVG icons contain no scripts.
- **Data-exposure considerations:** every query text (company names, theses, and potentially proprietary context) goes to RavenPack. The `plugin_slug` tags let the vendor attribute usage per workflow. `allow_implicit_invocation: true` together with "prefer it over web search" means it can capture general finance questions once connected. The upload/save flow (user-built skills only) would put your deliverables into Bigdata's document store. Bigdata's privacy policy and terms govern this. Check before sending proprietary data in prompts.

## 5. Quality assessment

**Strengths**
- Unusually strong analytic scaffolding: EPIC, FaVeS, reverse DCF, an earnings-quality ladder, a numeric likelihood × impact risk rubric, and peer-set justification with named exclusions.
- Firm anti-hallucination rules ("Not available", Gaps section, cite or label every number, show EV arithmetic).
- Explicit "use instead" routing tables in every skill reduce overlap.
- `reits.md` is solid: FFO/AFFO formulas, NAV build, cap-rate and P/FFO bands by property type, office occupancy >90% target, lease-rollover and +50–100bp cap-rate stress tests, AFFO payout >100% red flag. Bank material covers NPL, NCO, ACL coverage and >25% single-industry loan concentration, which maps directly to CRE concentration.
- Clean security posture: pure prompts plus inert calculators.

**Gaps and defects**
- **Broken references.**
  - `references/sector-routing.md` in investment-memo, peer-comparables, sector-analysis and sector-playbook links to `./sectors/*.md`, which does not exist. Only sector-playbook ships the sector files, flat in `references/`. So a REIT investment memo cannot load `reits.md`.
  - `post-ipo-common.md` links to `../private_company/...`, `../../assets/templates/...` and `./post-ipo-day1.md`, all left over from a monolith.
- **Benchmarks are static and partly dated:** the cap-rate table (Class A gateway office 4.5–5.5%) reads like the pre-2023 regime and is unsuitable for 2026 DC office.
- **Tearsheet fields are assumed** ("where exposed"). Positioning and short data may be sparse. no structured macro time series beyond the country tearsheet.
- No search budget for investment-memo or variant-perception. The country skills fire 35+ queries (cost and latency).
- Everything depends on a **paid Bigdata.com subscription**. Content depth (broker research, expert calls, premium news) depends on entitlements and add-on packages (see `images/data-packages/bigdata-packages.png`). Without it the skills are inert apart from the IPO web-search fallback.
- Some "2026" literals are hard-coded in query templates, so they will age.

