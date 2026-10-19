# research-analyst plugin

Securities-litigation origination research on one-day stock drops in the US, Canada, UK and Germany,
built on Andrew Morganti's method.

**Questions it answers:** (1) did the new information merely show the business did badly, or did it
show investors had previously been given a materially inaccurate picture? (2) If so, is there a
claim worth issuing? It organizes the evidence and drafts his submissions; the lawyer makes the
legal judgment.

## Workflow

| Layer | Command | Output |
|---|---|---|
| 1. Triage every screened drop | `/triage <screener output> [date]` | `runs/<date>/triage.md` |
| 2. Investigate one drop | `/investigate <EXCH:TICKER> <date>` | `runs/<date>/<TICKER>/memo.md` (Andrew's form) + `ledger.jsonl` |

**Trigger** (Andrew's, `references/trigger.md`): a one-day fall of more than 10%, a market cap over $200M,
and a TSX/TSXV/CSE/Cboe Canada listing, or a Canadian-registered SEDAR+ filer listed on Nasdaq, NYSE or
US OTC.

Layer 2 opens with Andrew's seven-step **first-review** (SEDAR+ profile, drop-date records, the 1–3 key
facts, a year of MD&As, the language change, call transcripts, and price and volume history). Then the
stages:
1. market-event
2. trigger-finder
3. disclosure-history: issue and case type (**checkpoint 1**), then total mix and drift tables
4. knowledge-indicators, external-evidence and parties-and-capital, in parallel
5. case-economics
6. claim-framing: forum, classes, linkage, Bear v. Bull, decision (**checkpoint 2**)
7. timeline
8. verify
9. memo-writer

## Where the method comes from

`references/andrew-method.md` distils about 60 memos from Andrew's Drive, written 2012–2026: his own
origination memos, associate research memos and an expert damages report. It covers the questions
he asks, the 20 research angles, his pursue/pass rules with the cases they came from, and his voice.

- `references/memo-forms/`: his four memo forms, copied exactly: 2026 (Slate/FiServ), IRAC (Global
  Atomic/Li-Cycle), Litigation Opportunity (Ascot/Alamos) and Pass (Paladin). The plugin chooses one
  per case and writes in it exactly, with footnotes in his style.
- `references/memo-template.md`: the content checklist.
- `references/legal-library.md`: the boilerplate he reuses verbatim, with citations, and flags on
  citations the corpus gives inconsistently.
- `references/case-types.md`: 13 playbooks.
- `references/economics.md`: his damages rules of thumb, formalized.
- `references/corpus.md`: the exemplar memos, with Drive IDs, to read for voice.

## Layout

| Path | What |
|---|---|
| `skills/research-analyst/` | Orchestrator: the question, stage order, rules, expert questions |
| `skills/<stage>/` | One skill per stage |
| `references/` | Evidence ledger schema, drop standard, trigger tiers, statement types, sources, language rules, jurisdictions |
| `scripts/market_event.py` | Drop standard (TradingView chart feed + scanner); all market numbers |
| `scripts/price_history.py` | Step 7: daily close and volume from one year plus 30 days before the drop, with every earlier 10%+ fall flagged |
| `scripts/economics.py` | Price move on each disclosure; look-back; volume by venue; damages ranges; 5% cap; settlement target; limitation dates |
| `scripts/render_memo.py` | Renders the memo to Word with real footnotes (and his letterhead for Form A), for upload as a Google Doc |
| `scripts/ledger.py` | Ledger structure check, quote matching, and `memo` lint (citations, placeholders, uncited figures, text carried over from another case, required sections) |
| `runs/` | One folder per screener date |

## Requirements

Python 3 with `numpy` and `websocket-client`. Connectors: Bigdata.com, CourtListener, and Google Drive
(to read the exemplar memos, and to save a memo as a Doc when asked). SEC EDGAR needs no key (send a
User-Agent with contact email).

## Borrowed from

InvestSkill (fact-check, financial-report-analyst, 10k-digest, insider-trading, bear-case,
result-validator), intel (evidence standards, diagnose, research, red-team, brief), Bigdata.com plugin
(company-brief, catalyst-monitor, risk-assessment, earnings-digest, earnings-quality-screen, query
discipline), financial-services (deal-screening, kyc-doc-parse, datapack-builder, earnings-analysis,
ib-check-deck, dd-checklist). See `PLAN.md` §6 at the repository root for the mapping.

## Status (v0.2)

- The memo layer is rebuilt on Andrew's corpus: three new stages (parties-and-capital,
  case-economics, claim-framing), a rewritten memo-writer, and a second checkpoint at the decision.
- `economics.py` was backtested on two of his cases:
  - Global Atomic: −17.3% and −31.9% match his memo exactly. The script dates each drop to the
    session that actually reacted.
  - Slate Grocery: $15.26 → $11.40 on 25.9× volume, against his "$15.26 down to $11.30". The script
    also flags that the 10-day look-back recovered past the pre-drop price after the takeover news.
- Drop-standard thresholds are still v1 defaults.
- Still to come: run a full case end to end (FOXF is paused at checkpoint 1), test a non-US case,
  and draft complaints from the memo.
