# Digest: anthropics/financial-services plugin marketplace ("claude-for-financial-services")

Source reviewed: `scratchpad/plugins/financial-services-main/financial-services-main` (363 files). The review was read-only: cat, grep, md5sum, diff, and jq for JSON parsing. No scripts were executed. Owner in marketplace.json: Matt Piccolella. Plugin authors: "Anthropic FSI", "Anthropic", LSEG, and Kensho/S&P. License: Apache-2.0.

## 1. Overview and architecture

The marketplace registers 19 installable plugins:

- **6 vertical plugins** (`plugins/vertical-plugins/`). These are the canonical skill sources, plus slash commands and connectors.
  - `financial-analysis` (core, v0.1.1): 13 skills, 7 commands, and all 12 MCP connectors.
  - `investment-banking` (v0.2.1): 9 skills, 7 commands, and a `.local.md.example` settings file.
  - `equity-research` (v0.1.2): 9 skills, 9 commands.
  - `private-equity` (v0.1.2): 10 skills, 10 commands.
  - `fund-admin` (v0.1.0): 6 skills, no commands.
  - `operations` (v0.1.0): 2 KYC skills.
  - All `hooks/hooks.json` files are empty (`{"hooks": {}}`). The IB and PE `.mcp.json` files are empty.
- **10 agent plugins** (`plugins/agent-plugins/<slug>/`). Each is one `agents/<slug>.md` system prompt plus bundled copies of vertical skills:
  - pitch-agent, market-researcher, earnings-reviewer, meeting-prep-agent, model-builder
  - gl-reconciler, kyc-screener, valuation-reviewer, month-end-closer, statement-auditor
  - Each agent prompt has a "What you produce / Workflow / Guardrails" section with stop-for-review gates and `[UNSOURCED]` tagging. Each declares `tools:` with MCP globs such as `mcp__capiq__*`.
- **2 partner plugins** (`plugins/partner-built/`):
  - `lseg` (v1.0.0): 8 skills and 8 commands for fixed income, FX, vol and macro on the LSEG "LFA" MCP.
  - `sp-global` (v1.0.1, by Kensho): 3 skills (tear-sheet, earnings preview, funding digest) on the Kensho/Capital IQ MCP.
- **`claude-for-msft-365-install`** (v0.1.13). This is IT-admin tooling for deploying the Claude Office add-in against Vertex, Bedrock, Foundry or a gateway. It has 9 commands, PS1/SH scripts and a Python bootstrap example. It is not FSI content.
- **`managed-agent-cookbooks/<slug>/`**, one per agent. Each holds:
  - `agent.yaml`: a POST /v1/agents manifest for model `claude-opus-4-7` that references the agent .md and skills by path.
  - `subagents/*.yaml`: depth-1 leaf workers. Exactly one leaf holds Write. Readers have Read/Grep only and optional JSON `output_schema`.
  - `steering-examples.json` and a README with a security tier.
  - MCP URLs are env placeholders (`${CAPIQ_MCP_URL}`, `${DALOOPA_MCP_URL}`, `${FACTSET_MCP_URL}`, `${GL_MCP_URL}`, `${SUBLEDGER_MCP_URL}`, `${NAV_MCP_URL}`, `${SCREENING_MCP_URL}`, `${PORTFOLIO_MCP_URL}`, `${CRM_MCP_URL}`).
- **`scripts/`**:
  - `deploy-managed-agent.sh`: curls the Anthropic API to upload skills and create agents.
  - `check.py`: lint, reference resolution, drift check, and a .ps1 ASCII gate.
  - `sync-agent-skills.py`: rmtree plus copy from verticals into agent bundles.
  - `version_bump.py`, `validate.py`, `test-cookbooks.sh`, and `orchestrate.py` (a reference handoff router).

Design philosophy: everything is Markdown/YAML with no build step. Skills are authored once in the verticals and copied into agents. Most modeling skills support two runtimes. In the Excel/PowerPoint add-in they use Office JS (`range.formulas`, with a recurring "merge-cell" pitfall note). For headless file output they use Python openpyxl, python-pptx, or PptxGenJS/docx-js. The `xlsx-author` and `pptx-author` skills are the headless fallbacks; they write to `./out/`.

**Structural gaps found:**

- **README and directory mismatches.**
  - The README lists `claude-for-financial-advisors`, but that directory does not exist.
  - The meeting-prep cookbook claims a "wealth-management" vertical, which also doesn't exist. Its 3 advisor skills live only inside `meeting-prep-agent`.
  - CLAUDE.md mentions `mcp-categories.json`, which is absent.
- **Missing example files.** Skills reference example and template files that are not shipped:
  - `examples/comps_example.xlsx`
  - `examples/LBO_Model.xlsx`
  - No .xlsx, .pptx or .docx files exist anywhere in the repo.
- **Missing helper scripts and external skills.**
  - DCF, 3-statement and LBO require `recalc.py`, which comes from Anthropic's separate `xlsx` skill and is not bundled.
  - The S&P skills read `/mnt/skills/public/docx/SKILL.md`, i.e. they assume the Claude.ai built-in docx skill exists.

## 2. MCP connectors

**Core connectors.** These are defined in `financial-analysis/.mcp.json`, all type http.

| Connector | URL |
|---|---|
| Daloopa | mcp.daloopa.com/server/mcp |
| Morningstar | mcp.morningstar.com/mcp |
| S&P Global/Kensho (`sp-global`) | kfinance.kensho.com/integrations/mcp |
| FactSet | mcp.factset.com/mcp |
| Moody's | api.moodys.com/genai-ready-data/m1/mcp |
| MT Newswires | vast-mcp.blueskyapi.com/mtnewswires |
| Aiera | mcp-pub.aiera.com |
| LSEG | api.analytics.lseg.com/lfa/mcp |
| PitchBook | premium.mcp.pitchbook.com/mcp |
| Chronograph | ai.chronograph.pe/mcp |
| Egnyte | mcp-server.egnyte.com/mcp |
| Box | mcp.box.com |

**BUG: this file is invalid JSON.** There is a missing comma after the `egnyte` block, and the `box` block is unclosed (jq fails at line 47). As shipped, the core plugin's connectors will likely fail to load.

The partner plugins carry their own `.mcp.json` files:
- `lseg` uses `.../lfa/mcp/server-cl`, which is a different path from the core file.
- `spglobal` uses the same Kensho URL as the core file.

All of these connectors need paid entitlements or OAuth.

**Placeholders and naming mismatches:**
- Agents and cookbooks reference `capiq`, `crm`, `portfolio`, `internal-gl`, `subledger`, `nav` and `screening`. None of these are defined in any `.mcp.json`; they are firm-supplied placeholders.
- The agents' `mcp__capiq__*` glob does not match the core server name `sp-global`, so in Cowork the agents will not see the S&P tools unless the server is renamed.

**Which skills need which connectors:**

- **Hard-require an MCP (cannot run without it):**
  - All 8 LSEG skills: bond_price, interest_rate_curve, credit_curve, ir_swap, yieldbook_*, qa_*, and similar tools.
  - All 3 S&P skills. `earnings-preview-beta` explicitly forbids web search: "ONLY Kensho Grounding + kfinance".
  - fund-admin `accrual-schedule`, `roll-forward` and `variance-commentary` need internal-gl.
  - `gl-recon` and `break-trace` need internal-gl plus subledger.
  - `nav-tieout` needs nav.
  - `kyc-rules` needs a screening MCP, or a provided rules file plus screening results.
  - `deal-sourcing` expects Gmail and Slack for its CRM check.
  - The `meeting-prep-agent` needs crm.
  - The `valuation-reviewer` needs portfolio.
- **Prefer an MCP but fall back:**
  - `comps-analysis`: "use S&P Kensho/FactSet/Daloopa exclusively if available; NEVER web search as primary"; fallback is Bloomberg/EDGAR.
  - `dcf-model`: Daloopa, then user data, then web for price/beta.
  - `strip-profile`: FactSet/CapIQ/BamSEC.
  - `earnings-analysis`, `earnings-preview`, `datapack-builder`, `initiating-coverage`, `3-statement-model` (EDGAR).
- **Work with web search plus local files only:**
  - equity-research: `earnings-analysis` (web search is mandated for timeliness), `earnings-preview`, `morning-note`, `sector-overview`, `idea-generation`, `thesis-tracker`, `catalyst-calendar`, `model-update`.
  - investment-banking: all 9 skills, including `datapack-builder` from OMs/CIMs.
  - private-equity: all except `deal-sourcing`'s CRM step.
  - financial-analysis: `competitive-analysis`, `audit-xls`, `clean-data-xls`, `deck-refresh`, `ib-check-deck`, `ppt-template-creator`, `skill-creator`, `lbo-model` and `3-statement-model` (template-driven), and the author skills.
  - The 3 wealth-management skills in meeting-prep-agent (with user data).
- **Not wired, but useful for Quoin:**
  - Moody's (CMBS/CRE credit data, if licensed), Morningstar, and LSEG (rates/swap curves for CMBS spreads).
  - No skill actually calls Moody's, Morningstar, PitchBook, Aiera, MT Newswires, Chronograph, Egnyte or Box by name. They are listed as available only.
  - No connector covers CRE, CMBS, Trepp, CoStar or property data. This is where the session's QuoinData MCP would complement the marketplace.

## 3. Unique skills (63)

The repo holds 111 SKILL.md files and 63 unique hashes. Each unique skill is reviewed once below.

**financial-analysis**

| Skill | Purpose | Inputs | Output | Key methodology / quality gates |
|---|---|---|---|---|
| comps-analysis | Trading comps | ticker; peers (4-6); MCP/EDGAR | xlsx | Operating plus valuation blocks with Max/75th/Median/25th/Min (QUARTILE); formulas only; every hardcode gets a source cell-comment; blue inputs / black formulas; step-by-step user checkpoints; sanity bands (EV/EBITDA 8-25x); the "5-10 rule". No REIT metrics (FFO, AFFO, P/NAV, implied cap rate). |
| dcf-model | Full DCF | ticker, growth cases | xlsx (DCF and WACC sheets) | Bear/Base/Bull blocks plus an IF case selector; CAPM WACC; mid-year convention; Gordon growth or exit multiple; terminal value must be 50-70% of EV; three 5x5 sensitivity grids with the center cell equal to the base case (highlighted), each cell a full formula (no Data Tables); `recalc.py` must show zero errors (not shipped); `validate_dcf.py` (benign openpyxl checker); 50KB of anti-pattern guidance. |
| 3-statement-model | Fill an IS/BS/CF template | template xlsx, filings | xlsx | Preserve template formulas; BS balances every period; CF ending cash equals BS cash; credit metrics and covenant checks; scenario toggle; master check formula. |
| lbo-model | Fill an LBO template | template (missing default), deal terms | xlsx | S&U, debt schedule, cash sweep, intentional circular (interest), IRR/MOIC, sensitivity; section-by-section approval. |
| audit-xls | Spreadsheet/model QA | xlsx; scope selection/sheet/model | md findings table | Formula errors, hardcodes inside formulas, pattern breaks, off-by-one ranges, BS/CF tie, RE rollforward, terminal value dominance, model-specific bugs (DCF/LBO/merger/3-statement); Critical/Warning/Info; report before fixing. |
| clean-data-xls | Normalize messy data | sheet/range | xlsx (helper columns) | Profiling; TRIM/VALUE/DATEVALUE helper formulas rather than overwrites; confirm destructive dedupe; per-category before/after. |
| competitive-analysis | Competitive landscape deck | company/industry, peers | pptx | Scope via questions, then outline approval, then build; source hierarchy (10-K first); insight titles; real chart objects; quantified signposts; 2x2/radar/tier visuals. |
| deck-refresh | Swap numbers across a deck | pptx plus mapping/xlsx | pptx | Finds all variants ($485M / 485 / $485.0 million); approval gate; flags derived numbers (YoY growth, shares) without silently fixing them; preserves formatting; checks overflow. |
| ib-check-deck | Deck QC | pptx | md report | `extract_numbers.py` normalizes units and flags conflicting values across slides; data-narrative alignment; IB register; visual QC; Critical/Important/Minor. |
| ppt-template-creator | Turn a firm .pptx into a reusable skill | pptx/potx | skill dir (+ .skill zip) | python-pptx placeholder geometry extraction; content-area bounds; example deck. |
| pptx-author | Headless pptx | model outputs | pptx in ./out | python-pptx; firm template; every number traced to the model. |
| xlsx-author | Headless xlsx | inputs | xlsx in ./out | openpyxl; Inputs tab; named ranges; Checks tab with TRUE/FALSE. |
| skill-creator | Older copy of Anthropic's skill-creator | - | skill | init_skill/package_skill/quick_validate scripts (benign). |

**equity-research**

| Skill | Purpose | Inputs | Output | Key methodology / quality gates |
|---|---|---|---|---|
| earnings-analysis | Post-earnings update | ticker, quarter | docx (8-12 pages, 8-12 charts) | Mandatory "check today's date / search latest / release <3 months old" freshness gate; quantified beat/miss; hyperlinked EDGAR sources on every figure; refs: workflow, report-structure, best-practices. |
| earnings-preview | Pre-print setup | ticker | 1-page md/docx | Consensus with source and date; bull/base/bear; catalyst checklist; implied options move. |
| initiating-coverage | Initiation report | ticker | md, xlsx (6 tabs), md + tabs, png zip, docx (30-50 pages) | Strict one-task-at-a-time across 5 tasks with prerequisite verification; "no extra deliverables"; 20-30 revenue rows and 40-50 IS lines; DCF + comps + football field; 25-35 charts; ~200KB of references. |
| model-update | Plug actuals, roll estimates | existing model | xlsx + md/docx | Old/new/delta tables; GAAP vs adjusted; price target derivation. |
| morning-note | 7am note | coverage list | md/docx | ≤1 page, opinionated, "no news is valid". |
| sector-overview | Industry primer | sector | docx/pptx + xlsx | TAM with source, structure, value chain, comps, valuation context, investment implications. |
| thesis-tracker | Thesis log and scorecard | position | md/docx | Falsifiable pillars, disconfirming evidence, conviction. |
| catalyst-calendar | Event calendar | universe | xlsx + md | H/M/L impact; archive outcomes. |
| idea-generation | Screens and themes | criteria | md shortlist | Value/growth/quality/short/special-situation screens; one-pagers. |

**investment-banking**

| Skill | Purpose | Inputs | Output | Key methodology / quality gates |
|---|---|---|---|---|
| datapack-builder | Normalized data pack from CIM/OM/filings | docs | xlsx (8 tabs) | Strict number-format rules ($ vs counts vs %); trace each number to a source page; EBITDA normalization patterns; a **Real Estate/Hospitality** adaptation (occupancy, ADR, RevPAR, NOI, cap rate, FF&E) and a Property/Segment tab; row-tracking code pattern. |
| pitch-deck | Populate a bank pptx template | template + xlsx/csv | pptx | Read 4 reference files first; LibreOffice render loop with a mandatory disclaimer that LibreOffice rendering is imperfect; anti-patterns (text "tables", data in placeholders). |
| strip-profile (frontmatter name `fsi-strip-profile`) | 1-4 slide company profile | ticker | pptx (PptxGenJS) | One slide at a time, each rendered to an image and visually reviewed; 4-quadrant layout with fixed font sizes. |
| cim-builder | CIM draft | mgmt materials | docx + xlsx | 8-section TOC, 40-60 pages, data-backed claims, disclaimer. |
| teaser | Blind teaser | facts | docx/pdf/pptx | Anonymization checklist. |
| buyer-list | Buyer universe | target | xlsx | Strategic/sponsor tiers A/B/C; contact mapping. |
| merger-model | Accretion/dilution | deal terms | xlsx | S&U, PPA, phased synergies, breakeven synergies, 2-way sensitivities. |
| process-letter | IOI/final-bid letters | process stage | docx | Evaluation criteria; legal review. |
| deal-tracker | Pipeline tracker | deals | xlsx + md | Milestones, owners, P0-P2. |

**private-equity**

| Skill | Purpose | Inputs | Output | Key methodology / quality gates |
|---|---|---|---|---|
| ic-memo | Investment committee memo | DD findings, terms, returns | docx/md | 9 sections (exec summary through recommendation); risks ranked with mitigants; tables must tie; asks for missing terms rather than assuming them. |
| deal-screening | Pass/fail screen | CIM/teaser | 1-page md | Criteria table; Pass / Further DD / Hard Pass. |
| returns-analysis | IRR/MOIC | entry/exit/leverage | xlsx | Attribution (growth/multiple/deleveraging); 4 two-way grids; gross vs net. |
| dd-checklist | Diligence tracker | sector, deal type | xlsx | Workstreams, statuses, red-flag log (includes "facilities and real estate", environmental). |
| dd-meeting-prep | Question lists | meeting type | 1-page md | Management/expert/customer question banks; red flags. |
| unit-economics | SaaS cohorts | customer data | xlsx | ARR bridge, NDR/GRR, LTV/CAC benchmarks. Not relevant to Quoin. |
| portfolio-monitoring | Actual vs plan | financial package | md/xlsx | Green/yellow/red at 5%/15%; covenant compliance; questions for management. |
| value-creation-plan | EBITDA bridge, 100-day plan | baseline | xlsx/docx | Levers mapped to the bridge. |
| ai-readiness | Portfolio AI scan | portco materials | 1-page md | 3 go/no-go gates; ranked stack; "replays". |
| deal-sourcing | Find targets, CRM check, outreach | criteria | email drafts | Gmail/Slack check; never sends without approval. |

**fund-admin and operations (all need internal MCPs)**

| Skill | Purpose | Output | Key gates |
|---|---|---|---|
| gl-recon | GL↔subledger match | break report + summary | Full-outer join; 6 buckets; cause tags. |
| break-trace | Root-cause one break | JSON | One-sentence cause, owner, action. |
| accrual-schedule | Period accruals | table + draft JEs | Never posts. |
| roll-forward | Account rollforward | table | Must foot; no plugs. |
| variance-commentary | Flux commentary | table + narrative | "Driver unclear" rather than invented drivers. |
| nav-tieout | LP statement vs NAV | pass/fail per line | 0.01 tolerance; sum of LPs = NAV. |
| kyc-doc-parse | Onboarding packet to JSON | JSON | Untrusted-document wrapper; null rather than guesses. |
| kyc-rules | Apply rules grid | disposition JSON | Every outcome cites a rule; never approves. |

**meeting-prep-agent only (wealth management)**

- `client-review`: performance, IPS drift and agenda.
- `client-report`: quarterly performance report, PDF/docx.
- `investment-proposal`: prospect deck in pptx with Monte Carlo and fees.

**LSEG (MCP-only)**

Each skill opens with "let the tools compute, you interpret" and closes with a tool-chaining workflow and output tables.

| Skill | Purpose |
|---|---|
| bond-relative-value | G/Z/OAS decomposition, rate shocks |
| fixed-income-portfolio | MV-weighted yield/duration/DV01, YieldBook cashflows, ±200bp scenarios |
| swap-curve-strategy | Swap spreads, steepeners/flies |
| macro-rates-monitor | GDP/CPI, curves, breakevens |
| bond-futures-basis | CTD, implied repo |
| fx-carry-trade | Carry-to-vol |
| option-vol-analysis | SABR surfaces, Greeks |
| equity-research | IBES consensus snapshot |

**S&P/Kensho (MCP-only)**

| Skill | What it produces |
|---|---|
| tear-sheet | docx via docx-js, with 4 audience references (ER, IB/M&A, corp dev, sales/BD) |
| earnings-preview-beta (frontmatter `earnings-preview-single`) | 4-5 page HTML; strict fiscal-quarter and LTM/NTM rules |
| funding-digest | 1-slide pptx; requires `npm install simple-icons sharp` |

Shared S&P quality gates:
- Every MCP result is written to `/tmp/...` intermediate files, and the final document reads numbers only from those files.
- An arithmetic validation pass is mandatory.
- An "AI-generated" disclaimer is required.

## 4. Slash commands and agents

**Commands (41 FSI plus 9 admin):**

- **financial-analysis:**
  - `/comps` (full workflow and checklist)
  - `/dcf` (comps first, then DCF with comps-informed terminal multiple and cross-checks)
  - `/lbo`, `/3-statement-model`, `/competitive-analysis`
  - `/debug-model` (audit-xls at model scope)
  - `/ppt-template` (allowed-tools Read/Write/Bash/Glob)
- **equity-research:**
  - `/earnings` (full workflow)
  - `/earnings-preview`, `/initiate`, `/model-update`, `/morning-note`, `/screen`, `/sector`, `/thesis`, `/catalysts`
- **investment-banking:**
  - `/one-pager` (full workflow with template-skill discovery)
  - `/cim`, `/teaser`, `/buyer-list`, `/merger-model`, `/process-letter`, `/deal-tracker`
- **private-equity:**
  - `/source`, `/screen-deal`, `/dd-checklist`, `/dd-prep`, `/unit-economics`, `/returns`, `/ic-memo`, `/portfolio`, `/value-creation`, `/ai-readiness`
- **lseg:**
  - `/analyze-bond-rv`, `/analyze-fx-carry`, `/research-equity`, `/analyze-swap-curve`, `/analyze-option-vol`, `/review-fi-portfolio`, `/macro-rates`, `/analyze-bond-basis`
- **msft-365-install:**
  - `setup`, `manifest`, `consent`, `entra-app`, `access-policies`, `update-user-attrs`, `bootstrap`, `debug`, `export-data`
  - Plus a local `verify` skill.

Most commands are three-line stubs that only load the matching skill.

**Agents** (name: workflow / bundled skills / MCP globs):

- **pitch-agent**: comps, precedents, DCF/LBO, football field, then a deck on the bank template, then QC.
  - Skills: 11.
  - MCP: capiq. The cookbook adds daloopa.
- **market-researcher**: sector primer, landscape, comps spread, 3-5 ideas, note.
  - MCP: capiq and factset.
- **earnings-reviewer**: transcript, model-update, audit, note draft.
  - MCP: factset and daloopa.
- **model-builder**: DCF/LBO/3-statement/comps, audit, sensitivities.
  - MCP: capiq and daloopa.
- **meeting-prep-agent**: CRM pull, briefing pack.
  - MCP: crm and capiq.
- **valuation-reviewer**: GP packages, marks vs policy, waterfall, LP pack.
  - MCP: portfolio.
- **Back-office agents**, each read-only orchestrator with a single Write leaf and no posting or distribution:
  - gl-reconciler (internal-gl, subledger)
  - month-end-closer (internal-gl)
  - statement-auditor (nav)
  - kyc-screener (screening)

## 5. Duplicate map

`md5sum` was run on all 111 SKILL.md files, and `diff -rq` on each agent skill directory against its vertical source (including references and scripts).

**Result:** all 48 bundled agent skill directories are byte-identical to their vertical sources. There are 0 diverged copies. Three agent-only skills have no vertical source: client-report, client-review and investment-proposal. `check.py` enforces the no-drift rule.

Copy counts (the vertical source plus N agent copies):

- **Most copied:**
  - xlsx-author: 1 + 8 (earnings, gl, kyc, model, month-end, pitch, statement, valuation)
  - audit-xls: 1 + 6 (earnings, gl, model, month-end, pitch, statement)
  - comps-analysis: 1 + 3 (market-researcher, model-builder, pitch)
  - pptx-author: 1 + 3 (market-researcher, meeting-prep, pitch)
- **Copied into 2 agents:**
  - dcf-model, lbo-model and 3-statement-model: model-builder and pitch
  - sector-overview: market-researcher and pitch
- **Copied into 1 agent:**
  - pitch: pitch-deck, ib-check-deck, deck-refresh
  - market-researcher: competitive-analysis, idea-generation
  - earnings-reviewer: earnings-analysis, earnings-preview, model-update, morning-note
  - valuation-reviewer: ic-memo, returns-analysis, portfolio-monitoring
  - gl-reconciler: gl-recon, break-trace
  - month-end-closer: accrual-schedule, roll-forward, variance-commentary
  - statement-auditor: nav-tieout
  - kyc-screener: kyc-doc-parse, kyc-rules
- **Never copied (vertical or partner only):**
  - equity-research: initiating-coverage, thesis-tracker, catalyst-calendar
  - investment-banking: all except pitch-deck
  - private-equity: all except ic-memo, returns-analysis and portfolio-monitoring
  - financial-analysis: clean-data-xls, ppt-template-creator, skill-creator
  - all LSEG and S&P skills

Practical implication: install verticals OR agents, not both. Installing both gives the same skill name in multiple plugins and causes trigger collisions. Skill-name collisions also exist with Anthropic built-ins and the S&P skills:
- `skill-creator` (the bundled copy is older than the built-in one)
- `earnings-preview` vs S&P `earnings-preview-single`
- LSEG `equity-research` vs the `equity-research` plugin name

## 6. Scripts, hooks, MSFT 365 tooling, security

**Plugin hooks:** none. Every hooks.json is empty, and no skill installs hooks into the user's Claude config.

**`.githooks/pre-commit`:** runs `scripts/version_bump.py --apply`. `check.py` silently runs `git config core.hooksPath .githooks` on first run. This is benign in their repo but notable if you vendor it: running check.py rewires your clone's hooks.

**`deploy-managed-agent.sh`:**
- Sends `ANTHROPIC_API_KEY` to `${ANTHROPIC_API_BASE:-api.anthropic.com}`. Setting that env var would redirect the key.
- Uploads zipped skill directories to /v1/skills. Uses beta headers `managed-agents-2026-04-01` and `skills-2025-10-02`.
- Env substitution into YAML is regex-whitelisted (`[A-Za-z0-9._/:@-]`), which is good hygiene.

**`orchestrate.py`:**
- Reference only. Its header openly documents the prompt-injection threat model and mitigates it with a target allowlist and jsonschema payload validation.
- Bug: `HANDOFF_RE` uses a non-greedy `.*?\}`, so any handoff with a nested `payload` object is truncated at the first `}` and fails to parse. Handoffs silently never fire.

**`sync-agent-skills.py`:** does `shutil.rmtree` on bundled directories. This is expected.

**GitHub workflows:**
- Plugin validation via `curl claude.ai/install.sh | bash` at a pinned CLI version.
- gitleaks with a pinned SHA256.
- A grep that scrubs internal Anthropic hostnames.
- A version-bump check.
- `secret-scan` pins the checkout action by SHA, but the others use `@v4` tags.

**Skill scripts:**
- `validate_dcf.py` and `extract_numbers.py` are pure local parsing with no network access.
- The skill-creator scripts import yaml/zipfile.
- Supply-chain notes:
  - `funding-digest` runs `npm install simple-icons sharp` at runtime.
  - initiating-coverage Task 4 runs `pip install matplotlib seaborn pandas numpy plotly`.
  - The S&P skills write to `/tmp/earnings-preview/` and similar paths.
- No `curl|bash`, base64, eval or exfiltration patterns in any skill.

**Prompt-injection posture:** this is the strongest of any marketplace reviewed so far.
- KYC, GL, accrual, transcript and GP-package inputs are explicitly marked untrusted (the "`<untrusted_document>`" framing).
- Reader leaves get Read/Grep only with no MCP. Exactly one Write leaf. Output schemas have regex-constrained strings.
- "Never post/send/publish/approve" rules throughout.

**MSFT 365 install (most security-sensitive part):**
- **Tenant-wide Graph consent.** It drives tenant-wide admin consent for Anthropic's multi-tenant Entra app `c2995f31-11e7-4882-b7a7-ef9def0a0266` with delegated **Mail.ReadWrite**, Calendars.Read, People.Read, User.Read and offline_access (for Outlook).
- **Secrets in client-side manifests.** It embeds secrets (`gateway_token`, `azure_api_key`, `google_client_secret`, `mcp_servers`) in the add-in manifest URL fragment (after `#`). These are client-side and visible to anyone with the manifest. Per-user tokens can instead be written to Entra extension attributes via `az rest`.
- **Setup log.** Writes a setup log to `~/Desktop/claude-for-msft-365-install-setup.md` that captures IDs and URLs, and potentially pasted secrets.
- **Node install.** Offers to install Node via brew/winget, asking first.
- **Destructive cache scripts.** `clear-addin-cache.{sh,ps1}` delete Office Wef caches and registry keys. They run in dry-run mode unless `--apply`/`-Apply` is passed, and the README warns this also wipes chat history.
- **Export scripts.** Read-only.
- **Bootstrap example.** The Python FastAPI bootstrap validates RS256 JWTs with audience and issuer. It has a `DEV_JWKS_PATH` bypass for local tokens; ensure that is unset in production.
- **Quoin relevance:** none unless Quoin deploys the Office add-in on its own cloud. Do not run it casually.

## 7. Quality assessment

**Strengths:**
- Genuinely practitioner-grade modeling discipline:
  - Formulas over hardcodes, source cell-comments, and blue/black/green color coding.
  - Odd-dimension sensitivity grids with the center cell equal to the base case.
  - Terminal value share bands, BS/CF tie-outs, and staged user checkpoints.
- Deck QC that catches derived-number staleness. `ib-check-deck` and `deck-refresh` are excellent and domain-agnostic.
- Strong freshness gates (earnings-analysis) and source-hierarchy rules.
- The S&P "intermediate file is the source of truth" pattern is a good anti-hallucination technique worth copying.
- Agent and cookbook security architecture is thoughtful.
- Zero drift between copies.

**Weaknesses:**
- **Corporate-equity centric.** There is no real-estate, REIT or credit content: no NOI/cap-rate DCF, FFO/AFFO, P/NAV, DSCR/debt yield/LTV, rent roll, lease-up, CMBS waterfall or loan surveillance. The only CRE touch is a short datapack-builder paragraph.
- **Shallow skills alongside deep ones.** Many IB/PE/ER skills are 2-4KB checklists, while dcf, comps and initiating-coverage run 30-50KB plus references (verbose and token-heavy).
- **Broken or missing pieces:**
  - The core `.mcp.json` is invalid JSON.
  - Example xlsx templates and `recalc.py` are missing.
  - The README references a missing advisors plugin.
  - Agent MCP names (capiq) don't match the defined server (sp-global).
  - Frontmatter names differ from directory names (`fsi-strip-profile`, `earnings-preview-single`).
- **Inconsistent defaults:**
  - Times New Roman in comps and ER vs Calibri elsewhere.
  - comps says "never web search" while earnings mandates web search.
- **Partner skills are vendor-locked.** They are valuable only with LSEG or S&P entitlements.

**Overall:** high reuse value for modeling and QA mechanics. The vertical content needs adaptation before Quoin can use it.

## 8. Best use cases for a Quoin Data research analyst (CRE in DC/MD/NoVA, CMBS)

Most of these pair the marketplace mechanics with QuoinData MCP property data, web or EDGAR, and local files.

1. **DC-metro REIT trading comps** (comps-analysis via `/comps`, xlsx).
   - Peers: e.g. JBG SMITH, BXP and other office/multifamily REITs with DC exposure.
   - Keep the stats block, cell-comment sourcing and checkpoints.
   - Swap the metrics for P/FFO, P/AFFO, P/NAV, implied cap rate, net debt/EBITDA, occupancy, and DC-region % of NOI.
   - Data from 10-K/10-Q supplementals (EDGAR) when no S&P/FactSet is available.
2. **Property-level DCF / valuation** (dcf-model mechanics, xlsx).
   - Re-base on unlevered property cash flow (NOI less TI/LC/capex reserves) with an exit-cap terminal value instead of Gordon growth.
   - 5x5 grids of exit cap × discount rate and rent growth × vacancy, with the center cell equal to the base case.
   - Bear/Base/Bull case selector.
   - Feed with QuoinData assessments, transactions and tax history, plus `find_nearby_sales` for cap-rate and $/SF anchors.
   - Run `audit-xls` (`/debug-model`) before sharing.
3. **CMBS loan credit memo** (ic-memo structure plus returns-analysis sensitivity, docx).
   - Exec summary, then property/sponsor, market, financials (UW NCF vs servicer NCF), structure, a risks-with-mitigants table, and a recommendation.
   - Replace IRR grids with DSCR, debt yield and LTV under NOI-haircut × cap-rate stress, plus a refinance-at-maturity test.
   - Use QuoinData flood, EPA, wetlands and zoning lookups for the environmental/zoning section; the dd-checklist workstreams adapt directly.
4. **Data pack from an OM, rent roll or servicer report** (datapack-builder plus clean-data-xls, xlsx).
   - Use the Real Estate adaptation, strict $ vs count vs % formatting and page-cited sources.
   - Clean messy servicer and loan-tape exports with helper-column formulas, not overwrites.
5. **Submarket / sector primer** (sector-overview plus competitive-analysis via `/sector`, docx/pptx).
   - Topics such as NoVA data-center land, DC office distress or MD multifamily.
   - TAM-style sizing becomes inventory, absorption, vacancy, pipeline and sales volume (QuoinData `search_properties`, transactions, builder sites).
   - Insight-titled slides with real charts.
6. **Client pitch deck or property one-pager** (strip-profile 4-quadrant layout, pitch-deck, ppt-template-creator for a Quoin-branded template skill; pptx).
   - Always finish with `ib-check-deck` for cross-slide number consistency.
7. **Quarterly deck/report refresh** (deck-refresh, pptx).
   - Roll recurring market reports or CMBS watchlist decks with new vacancy, delinquency or rate figures.
   - The approval gate flags stale derived YoY figures.
8. **CMBS watchlist and maturity calendar** (catalyst-calendar, thesis-tracker, portfolio-monitoring; xlsx + md).
   - Track loan maturities, DSCR/occupancy trigger breaches, special-servicing transfers, lease expirations of top tenants, and Fed/FOMC dates.
   - Use green/yellow/red variance flags against UW.
9. **REIT earnings review** (earnings-preview, earnings-analysis, model-update, morning-note).
   - For DC-exposed public REITs: beat/miss on FFO/AFFO, same-store NOI and leasing spreads.
   - The freshness gate and EDGAR hyperlinking come for free.
10. **Rates and spread context for CMBS pricing** (optional; LSEG macro-rates-monitor and swap-curve-strategy only with an LSEG entitlement).
    - Otherwise reproduce the outputs (UST/swap curve shape, swap spreads) from public FRED/Treasury data by hand.
    - Also: `deal-screening` (`/screen-deal`) as a fast pass/fail triage of inbound OMs against Quoin or client criteria.

**Recommendation:**
- Install `financial-analysis` (fixing the `.mcp.json` comma and brace first, or deleting unused servers) plus `private-equity` and `investment-banking` for document scaffolds.
- Skip the agent plugins (duplicates and enterprise MCP placeholders), fund-admin/operations, msft-365-install, and LSEG/S&P unless licensed.
- Fork comps-analysis, dcf-model and ic-memo into Quoin-specific `reit-comps`, `property-dcf` and `cmbs-credit-memo` skills that call QuoinData MCP tools.
