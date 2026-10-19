# research-analyst plugin

Securities-disclosure research on one-day stock drops in the US, Canada, UK and Germany.

**Question it answers:** did the new information merely show the business did badly, or did it show
investors had previously been given a materially inaccurate picture? It organizes evidence; the
lawyer makes the legal judgment.

## Workflow

| Layer | Command | Output |
|---|---|---|
| 1. Triage every screened drop | `/triage <screener output> [date]` | `runs/<date>/triage.md` |
| 2. Investigate one drop | `/investigate <EXCH:TICKER> <date>` | `runs/<date>/<TICKER>/memo.md` + `ledger.jsonl` |

Layer 2 stages: market-event → trigger-finder → disclosure-history (issue checkpoint) →
knowledge-indicators + external-evidence → timeline → verify → memo-writer.

## Layout

| Path | What |
|---|---|
| `skills/research-analyst/` | Orchestrator: the question, stage order, rules, expert questions |
| `skills/<stage>/` | One skill per stage |
| `references/` | Evidence ledger schema, drop standard, trigger tiers, statement types, sources, language rules, jurisdictions |
| `scripts/market_event.py` | Drop standard (TradingView chart feed + scanner); all market numbers |
| `scripts/ledger.py` | Ledger structure check and quote matching |
| `runs/` | One folder per screener date |

## Requirements

Python 3 with `numpy` and `websocket-client`. Connectors: Bigdata.com, CourtListener. SEC EDGAR
needs no key (send a User-Agent with contact email).

## Borrowed from

InvestSkill (fact-check, financial-report-analyst, 10k-digest, insider-trading, bear-case,
result-validator), intel (evidence standards, diagnose, research, red-team, brief), Bigdata.com plugin
(company-brief, catalyst-monitor, risk-assessment, earnings-digest, earnings-quality-screen, query
discipline), financial-services (deal-screening, kyc-doc-parse, datapack-builder, earnings-analysis,
ib-check-deck, dd-checklist). See `PLAN.md` §6 at the repository root for the mapping.

## Status (v0.1)

Workflow, references and the drop-standard script are in place. Thresholds are v1 defaults to be
calibrated on Andrew's past memos (v2), which will also replace the memo template.
