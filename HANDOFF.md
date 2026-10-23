# Handoff: research-analyst plugin (state as of 2026-10-19)

Repository: `donna49/research-analyst`, branch `main`.

## What exists

| Path | What |
|---|---|
| `PLAN.md` | Plan v2: decisions, data sources, drop standard, two-layer workflow, what is borrowed from the five plugins |
| `plugin-review/` | Reviews of the five source plugins (intel, Bigdata.com, financial-services, InvestSkill, finance-skills) |
| `research-analyst/` | The plugin (v0.1): orchestrator + 9 stage skills, references, scripts, `/triage` and `/investigate` commands |
| `runs/2026-10-16/` | First real run: 63-name screener, drop standard, triage of the 18 company-specific names |
| `runs/2026-10-16/FOXF/` | First Layer 2 case, stopped at the stage 3 checkpoint (`issue.md`) |

## Setup in the new account

1. Clone the repo and check out the branch above.
2. Python 3 with `numpy` and `websocket-client` (`pip install numpy websocket-client`).
3. Connectors: **Bigdata.com** and **CourtListener**. SEC EDGAR needs no key; send a User-Agent
   with a contact email (update the email in the skills/scripts to Andrew's or the firm's).
4. Install the plugin from `research-analyst/` (it has `.claude-plugin/plugin.json`).
5. Smoke test: `python3 research-analyst/scripts/market_event.py NASDAQ:FOXF --date 2026-10-16`
   should report abnormal −12.8%, t −5.7, Company-specific.

## Where things stand

- **Layer 1 (triage)** works end to end on 2026-10-16: 4 Full investigation (FOXF, CNDT, EBS,
  OMER), 11 Watch, 26 Exclude, 22 Borderline names not yet trigger-scanned
  (`runs/2026-10-16/triage.md`).
- **Layer 2 (FOXF)**: stages 1–3 done, ledger of 37 records passes both checks. Waiting on three
  decisions in `runs/2026-10-16/FOXF/issue.md`:
  1. Confirm the issue framing (fiscal 2026 outlook, six threads A–F).
  2. CEO departure in scope or context only.
  3. Context period two years or three.

## Next steps, in order

1. Answer the three FOXF questions, then run stages 4–10 (`/investigate NASDAQ:FOXF 2026-10-16`
   resumes from the ledger). Stage 4 must fetch full transcripts with `bigdata_fetch_document`;
   the six transcript quotes currently match only against search excerpts.
2. Trigger-scan the 22 Borderline names to finish the 2026-10-16 triage.
3. Done in v0.2: the memo layer is rebuilt on about 60 of Andrew's memos (see below).
   Still open: calibrate the drop-standard thresholds and trigger tiers against his cases.
4. Test a non-US case (Canada, UK or Germany) end to end.
5. Later: Google Docs output; complaint drafting from the memo plus Andrew's pleadings.

## Lessons recorded in the skills (keep them)

- Every number from a script; every quote verbatim with a locator; `scripts/ledger.py check`
  and `quotes` before any memo.
- EDGAR submissions-JSON acceptance times are wrong; use the filing header or index page (ET).
- Never compare a stock with other names from the same screen (selection bias); the theme
  factor handles group moves.
- Plaintiff-firm "investigation" notices are signals, not suits; existing suits never stop work.
- The reviewer pass catches researcher errors (e.g. a misrecorded filing time); keep it.

## v0.2 (2026-10-19): memo layer rebuilt on Andrew's corpus

- New references: `andrew-method.md`, `memo-template.md`, `legal-library.md`, `case-types.md`,
  `economics.md`, `corpus.md` (exemplar memos with Drive IDs).
- New stages: `parties-and-capital` (8), `case-economics` (9), `claim-framing` (10, with checkpoint 2:
  the decision). `memo-writer` now renders Andrew's form.
- New script `economics.py`; `ledger.py memo` lints the rendered memo.
- FOXF resumes at stage 4 once the three checkpoint-1 questions are answered. It then runs through
  the new stages.
