# finance-skills (himself65) — security and fit review

Source: `scratchpad/plugins/finance-skills-main/finance-skills-main` (marketplace v11.1.0, MIT, owner `himself65`). Every manifest, README, SKILL.md, reference file and opencli JS source file was read. No code was run. A scan for hidden Unicode and prompt-injection phrasing found nothing.

## 1. Overview

The repo does three jobs:

1. **A Claude Code plugin marketplace.** `.claude-plugin/marketplace.json` lists 6 plugins with 26 skills between them.
2. **A set of Agent Skills.** These are mostly prompt documents: SKILL.md plus references.
3. **A Node monorepo of opencli adapters.** `opencli-plugins/tradingview` and `opencli-plugins/hyperliquid` contain real code.

Most skills are prompt-only. They tell Claude to `pip install yfinance`, `curl` an API, or run third-party CLIs (opencli, tdl, uvx).

Two kinds of code run without a separate step:

- **Load-time shell probes.** 20 SKILL.md files have `` !`cmd` `` probes that run when the skill loads (subject to host permissions). Some of them reach the network or start daemons:
  - `opencli doctor` starts the opencli daemon.
  - `tdl chat ls` contacts Telegram using the stored session.
  - The hyperliquid probe calls `api.hyperliquid.xyz`.
  - The options-payoff and company-valuation probes call Yahoo.
- **A bundled MCP server.** `plugins/data-providers/.mcp.json` starts an MCP server **automatically whenever finance-data-providers is enabled**: `uvx --from git+https://github.com/atilaahmettaner/tradingview-mcp@099090e…`. The Git SHA is pinned, but transitive PyPI dependencies resolve at run time.

"Read-only" is enforced only by prompt instructions. The underlying credentials can write: Fintel keys, the Telegram session, and the X, LinkedIn and Discord sessions can all post, delete or modify. The only place read-only is enforced by code is the two opencli plugins, which expose no write endpoints.

## 2. Skill inventory

| Skill | Purpose | Installs / deps | Data source and auth | Output | Methodology notes |
|---|---|---|---|---|---|
| **yfinance-data** | General quotes, history, statements, options, holders, screener | `pip install yfinance` (unpinned) | Yahoo private endpoints via yfinance; no key | Tables | Thin API cheat-sheet; handles timezones properly |
| **earnings-preview** | Pre-earnings consensus, beat/miss history, analyst targets | yfinance | Yahoo | Brief | Good: report-timing logic via `get_earnings_dates` |
| **earnings-recap** | Actual vs estimate, reaction-day move, margin trends | yfinance | Yahoo | Brief | Correct after-close vs pre-open reaction window |
| **estimate-analysis** | Revisions over 7/30/60/90 days, up/down breadth, growth vs industry | yfinance | Yahoo | Tables plus synthesis | Solid; heuristic thresholds (up-revision ratio above 0.7 counts as bullish) |
| **company-valuation** | DCF, peer multiples and SOTP blended into an implied price, 5×5 sensitivity grid, bull/base/bear | yfinance, numpy, pandas | Yahoo; live 10Y yield from `^TNX` | Valuation report | Bugs: exit TV hardcodes 15x EV/EBITDA; sensitivity grid uses Gordon TV only, so the base cell does not equal the headline DCF; ERP default is 5.5% in SKILL.md but 4.28% in its reference; ΔNWC is `abs()` so it always reduces FCFF; SOTP reference has unsourced win rates and "enter position at $42" advice. Says REITs need NAV or P/FFO, which yfinance does not supply |
| **etf-premium** | ETF price vs NAV, peer comparison, screener, gamma-squeeze decomposition (GEX) | yfinance, pandas, numpy | Yahoo `navPrice` (prior-day NAV) | Tables | Well caveated. Sub-skill E's worked example is copied from an unverified Zhihu post |
| **stock-liquidity** | Spread, ADTV, Amihud ratio, square-root impact, turnover, letter grade | yfinance, pandas, numpy | Yahoo (15-minute delay; top of book only) | Dashboard | Formulas are fine. Two reference functions compute values and then drop them (`options_spread_analysis` and `order_book_proxy` both discard their results) |
| **stock-correlation** | Peer discovery, pair beta and spread z-score, clustering, regime correlation | yfinance, pandas, numpy, optional scipy | Yahoo screener and history | Matrices | Ward linkage on a 1−\|ρ\| distance is non-Euclidean; using \|ρ\| groups hedges with peers; EquityQuery operator spelled `is-in` in one file and `is_in` in another |
| **options-payoff** | Interactive options P&L chart with Black-Scholes pricing | Chart.js from CDN; yfinance for SPX spot | User input | claude.ai `show_widget` HTML | Correct Black-Scholes; depends on a claude.ai-only tool |
| **saas-valuation-compression** | ARR multiple across funding rounds and attribution of the change | Web search, Visualizer tool | Press coverage | Charts plus prose | Benchmark tables sourced from a Twitter account (@speculator_io); "April 2026 meltdown" figures are unverified |
| **sepa-strategy** | Minervini trend template, VCP, stops and position sizing | None (any data source) | — | "Strong Buy Setup / Watch / Pass" | Triggers on "should I buy this stock". Arithmetic errors: pyramid average should be $52.67, not $53.20; the "casino" example sums per-trade percentages |
| **finance-sentiment** | Social buzz and bullish % from Reddit, X, news, Polymarket | curl | Adanos API, paid key `ADANOS_API_KEY` sent as a header | Score blocks | Opaque third-party aggregation |
| **fintel-data** | Short interest, borrow, FTD, 13F, Form 4, analyst targets | curl; optional `claude mcp add` | Fintel REST or MCP, paid `FINTEL_API_KEY` | Tables | Good endpoint map. **Greps `.env` in the working directory and repo root** and exports the key |
| **hormuz-strait** | Strait of Hormuz shipping, oil and insurance dashboard | curl | hormuzstraitmonitor.com (unofficial, no auth) | Briefing | Unknown provenance; not relevant to us |
| **hyperliquid-reader** | Crypto perp and spot markets, funding, order book | `npm i -g @jackwener/opencli` (Node ≥24); `opencli plugin install github:himself65/finance-skills/hyperliquid` (unpinned HEAD) | POST to `api.hyperliquid.xyz/info`, public | Tables | Code is clean (one endpoint) |
| **tradingview-mcp** | Headless TA, scans, futures, Yahoo options, backtests (39 tools) | uv/uvx, Python 3.10–3.13, Git SHA-pinned server | TradingView scanner (undocumented) plus Yahoo; optional `MARKETAUX_API_TOKEN` | MCP JSON | `smart_money_analysis` is a formula proxy; `exchange` defaults to KUCOIN or EGX |
| **tradingview-reader** | TradingView desktop app: chains with greeks, watchlists, alerts, screenshots | opencli plus this repo's plugin; macOS TradingView.app | **Harvests TradingView session cookies over CDP** | Tables, PNG | See §3 |
| **twitter-reader** | Timeline, search, bookmarks, notifications, follower lists | opencli plus **Browser Bridge Chrome extension (load unpacked)** plus daemon | Logged-in x.com Chrome session | Tweets | Scraping |
| **linkedin-reader** | Feed and job search | Same as twitter-reader | Logged-in LinkedIn Chrome session | Posts, jobs | Scraping |
| **discord-reader** | Servers, channels, members, messages | opencli; Discord launched with `--remote-debugging-port=9232`; env var added to shell profile | Discord desktop session over CDP | Messages | Reads only the channel currently open in the app |
| **telegram-reader** | Channel and group exports | tdl via **`curl … install.sh \| sudo bash`**, brew, or `go install @latest` | Full MTProto user session stored on disk (QR, phone, or **imported from Telegram Desktop**) | JSON written to `/tmp` | Export files are world-readable |
| **opencli-reader** | Generic fallback over 500+ opencli adapters (Bloomberg, Reuters, Reddit, Xueqiu, arXiv, `web read`, ChatGPT…) | opencli plus Browser Bridge for COOKIE/UI adapters | Mixed: public sites or browser sessions | Varies | Read vs write decided by command-name heuristics; **explicitly allows ChatGPT/Gemini `ask` (a write)** |
| **yc-reader** | YC companies by batch, industry or tag | curl, jq | yc-oss.github.io static JSON (unofficial, from YC's Algolia index) | Lists | Simple and safe |
| **startup-analysis** | VC, job-seeker and CEO views of a startup | Web search | Public web | Report with verdicts | Reasonable frameworks; benchmark tables are generic |
| **generative-ui** | Design system for claude.ai `show_widget` | None | — | HTML/SVG | Claims to be "Anthropic's actual Imagine / visualize:read_me guidelines, extracted." Very broad trigger ("show me", "chart") |
| **skill-creator** | Write and score skills (10-dimension rubric) | None | — | Skill files | Partly written for the Hermes agent; overlaps `anthropic-skills:skill-creator` |

## 3. Scripts and opencli plugins

**Root files** (`package.json`, `pnpm-lock.yaml`): one maintainer devDependency (`ccbump`), used only for version bumps and never installed by users. CI workflows are `.github/workflows/{skill-lint,release-skills,opencli-plugin-test}.yml`. Tests are pure-JS units only; the actual connections to TradingView and Hyperliquid ("wire level") are not tested.

**`opencli-plugins/hyperliquid/`** (`lib/api.js`, 7 command files)
- Does one `fetch` POST to `https://api.hyperliquid.xyz/info`.
- No authentication, no filesystem writes, no child processes, no telemetry.
- Low risk. The only concern is that the install command pulls whatever is on `main` at install time; nothing is pinned.

**`opencli-plugins/tradingview/`** (12 commands)
- `launch.js` runs `osascript … to quit` and then `open -a TradingView --args --remote-debugging-port=9222`. This:
  - force-quits the app, losing unsaved layouts;
  - leaves an **unauthenticated CDP port on localhost**, so any local process can drive the logged-in app or read its cookies until it restarts.
- `lib/cookies.js` reads cookies:
  - It calls `Storage.getCookies` with no filter (browser-wide), then keeps only `*.tradingview.com` cookies.
  - It caches them in process memory and sends them from Node with a **spoofed TradingView Desktop/Electron User-Agent** to:
    - `scanner.tradingview.com`
    - `news-headlines.tradingview.com`
    - `pricealerts.tradingview.com`
    - `www.tradingview.com/api/v1/symbols_list`
    - `symbol-search.tradingview.com`
  - I found no exfiltration: every outbound host is a TradingView host.
- The `OPENCLI_CDP_ENDPOINT` env var can redirect the CDP target.
- `chart-state.js` uses `Runtime.evaluate` (reads only the DOM and the URL).
- `screenshot.js` writes a PNG to `~/tradingview-<ts>.png` by default.
- **Misleading claims and labels:**
  - The skill README says "no cookie extraction"; the plugin README and the code show it does exactly that.
  - Cookie-using commands are registered as `Strategy.PUBLIC, browser:false`, which hides their auth dependency from opencli's own strategy metadata.
- No write endpoints are exposed.

**Third-party binaries I could not review** (not in the zip):
- `@jackwener/opencli`: 500+ adapters, a daemon, and an unpacked Chrome extension with access to logged-in sessions.
- `tdl`.
- `tradingview-mcp` (Python).

## 4. Security and risk ratings

| Skill | Rating | Reasons |
|---|---|---|
| yfinance-data, earnings-preview/recap, estimate-analysis, stock-correlation, stock-liquidity, etf-premium, company-valuation | **Safe** (caution on licensing) | No credentials. Unpinned `pip install yfinance` (supply-chain hygiene only). yfinance scrapes undocumented Yahoo endpoints, and Yahoo's terms bar commercial use and redistribution, so use internally for research and **don't republish the data in Quoin Data products**. |
| options-payoff, sepa-strategy, startup-analysis, saas-valuation-compression | **Safe** | No credentials; only CDN Chart.js and web search. SEPA's buy verdicts and SaaS's weak sourcing are quality problems, not security ones. |
| yc-reader, hormuz-strait | **Safe** | Unauthenticated GET requests to static or public JSON. The YC data is unofficial. |
| skill-creator | **Safe** | Duplicates the built-in skill-creator. |
| generative-ui | **Caution** | No security risk. The "extracted Anthropic internal guidelines" claim is questionable. Its broad trigger can override this workspace's `dataviz` and `artifact-design` skills, and its target tool is claude.ai-only. |
| finance-sentiment | **Caution** | Paid key goes to a little-known vendor (Adanos). Only tickers are sent. |
| fintel-data | **Caution** | Paid, metered key. The load probe and instructions read `.env` files (key-hunting behavior). The key can also call Fintel's write endpoints; only the prompt prevents that. Optional MCP registration stores the key in Claude config. |
| tradingview-mcp | **Caution** | Auto-starts third-party Python on every session once the plugin group is enabled. Transitive dependencies are unpinned. Uses the undocumented TradingView scanner (ToS gray area). |
| hyperliquid-reader | **Caution** | The code is clean, but it needs a global opencli install and an unpinned plugin pulled from GitHub. Crypto-only. |
| opencli-reader | **Caution** (public adapters) / **Avoid** (cookie adapters) | Large, fast-changing registry. Writes are blocked only by name heuristics, and ChatGPT `ask` writes are explicitly allowed. Bloomberg, Reuters and Weixin run through your paid or logged-in sessions (paywall and ToS issues). |
| tradingview-reader | **Avoid** | Opens a CDP port, harvests session cookies, impersonates the TradingView Desktop app, violates TradingView ToS, and its own docs misdescribe it. macOS only. |
| twitter-reader | **Avoid** | Unpacked Chrome extension with cross-site session access. X prohibits scraping, so the account risks suspension. Pulls personal notifications and bookmarks into LLM context. |
| linkedin-reader | **Avoid** | Same mechanism. LinkedIn bans scraping and enforces it (account restriction, legal exposure). |
| discord-reader | **Avoid** | CDP self-bot automation violates Discord ToS (ban risk). Reads private-server messages and member lists, which is third-party personal data. Persists the CDP endpoint in the shell profile. |
| telegram-reader | **Avoid** | Installs via `curl \| sudo bash`. Creates a full-power Telegram account session on disk, optionally imported from Telegram Desktop. Leaves exports in world-readable `/tmp`. |

## 5. Quality assessment

**Strengths:**
- Consistent structure across skills: detection, routing table, defaults, then an output contract.
- Disclaimers are honest about Yahoo delays, prior-day NAV and top-of-book limits.
- Report-timing logic in earnings-recap is careful.
- The opencli JS is small, readable and tested at the unit level.
- Pinning the MCP server to a Git SHA is good practice.
- Reference data is date-stamped (for example, the Damodaran snapshot dated 2026-08-01).

**Weaknesses:**
- Code templates have real bugs (company-valuation, stock-liquidity, stock-correlation details in §2).
- Some content leaks or is weakly sourced (Zhihu worked example, Twitter-sourced drawdowns, "extracted" Anthropic guidelines).
- sepa-strategy and the SOTP reference contradict the repo's own "no trade recommendations" stance.
- Read-only rests on prompts alone.
- Install instructions for third-party binaries are unpinned.
- One docs-vs-code contradiction (cookie extraction).

Overall: **good-quality prompt engineering, with medium-quality financial code templates.** Check any number a skill produces before it reaches a client.

## 6. What works in our sandboxed cloud container

Our container has a proxied network, no browser, no desktop apps, and is not macOS. None of this was tested.

- **Likely works** if the proxy allows PyPI and `query1/query2.finance.yahoo.com` plus `fc.yahoo.com`:
  - all 8 yfinance skills;
  - sepa-strategy (with yfinance).
  - Yahoo often rate-limits or blocks datacenter IPs (429 or crumb errors), so expect flakiness.
- **Works** with plain HTTPS or web search: yc-reader, hormuz-strait, startup-analysis, saas-valuation-compression, skill-creator.
- **Works only with paid keys added as environment secrets:** fintel-data, finance-sentiment.
- **Possible but install-heavy:**
  - hyperliquid-reader: needs Node ≥24, an npm global install, and GitHub access.
  - tradingview-mcp: needs uv, Python ≤3.13, GitHub, PyPI and `scanner.tradingview.com`, and the MCP server must be registered at session start.
- **Does not work here:**
  - tradingview-reader (macOS app plus CDP);
  - twitter-, linkedin- and discord-reader (need Chrome or the desktop app);
  - telegram-reader (interactive login; it would also create a long-lived secret in the container);
  - opencli-reader's COOKIE, HEADER, INTERCEPT and UI adapters (its PUBLIC ones such as `hackernews`, `arxiv` and `web read` could work);
  - options-payoff and generative-ui (they need claude.ai `show_widget`; here the Artifact tool and `dataviz` cover the same need).

## 7. Best use cases for a Quoin Data research analyst (DC/MD/NoVA CRE, CMBS)

None of these skills covers property-level or loan-level data; QuoinData MCP stays the primary source. These are useful for public-market and credit context around it.

1. **CMBS and CRE-credit stress gauge** (etf-premium). Track premium or discount to NAV and peer spreads on CMBS and agency-MBS ETFs (for example iShares `CMBS`, `MBB`) and REIT ETFs (`VNQ`, `XLRE`). A widening discount relative to the bid-ask spread is an early stress signal to set beside our loan-level delinquency data.
2. **DC-metro REIT and lender earnings monitoring** (earnings-preview, earnings-recap, estimate-analysis). Cover names with DC/MD/NoVA office or multifamily exposure, such as JBG SMITH, BXP and Federal Realty (verify current tickers and listing status, for example Elme Communities). Also cover CRE lenders and mortgage REITs (for example STWD, BXMT, ABR, and regional banks with high CRE concentration). The goal is to catch guidance, impairment and estimate-revision trends that lead CMBS servicer commentary.
3. **Rate-sensitivity and contagion mapping** (stock-correlation, regime mode). Measure rolling and down-day correlation of DC office REITs and CRE lenders against the 10Y yield (`^TNX`), regional-bank ETFs and the CMBS ETF. This shows whether local office stress is trading as idiosyncratic or as systemic risk.
4. **Ownership and insider signals on CRE-exposed issuers** (fintel-data, paid). 13F holder changes, Form 4 insider selling, and short interest or borrow costs on office REITs and CRE lenders, as sentiment input for market notes.
5. **Liquidity screen for public comps** (stock-liquidity). Rank small-cap REITs and lenders by dollar volume and Amihud ratio before using their prices as valuation comps, since thin names give noisy implied cap rates.
6. **Proptech and CRE-data competitive intelligence** (yc-reader `industries/real-estate-and-construction`, about 138 companies; startup-analysis). Map venture-backed entrants in CRE data and analytics against Quoin Data's offering, and do quick diligence on specific competitors or partners.
7. **Implied-valuation cross-check** (company-valuation, relative-multiples path only). A sanity check on public REIT pricing versus peers. Fix the exit-multiple and ERP issues first, and add P/FFO from filings, because yfinance has no FFO.

Skip: all social readers, tradingview-reader, hyperliquid-reader, hormuz-strait, options-payoff, generative-ui and sepa-strategy. They are unsafe, off-mission, or already covered by tools in this workspace.

**Install recommendation:** install `finance-market-analysis` only, and optionally `finance-startup-tools`. Do **not** enable `finance-data-providers` as a group, because enabling it auto-starts the tradingview MCP server. If Fintel is wanted, copy that one skill and set the key as an environment secret instead of keeping it in `.env`. Do not install `finance-social-readers`.
