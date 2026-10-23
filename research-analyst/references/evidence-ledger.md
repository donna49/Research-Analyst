# Evidence ledger

One file per case: `runs/<date>/<TICKER>/ledger.jsonl`, one JSON object per line. Every stage
appends; nothing is deleted (a corrected record supersedes the old one via `supersedes`).
`scripts/ledger.py check <file>` validates it; the memo writer refuses to run on a ledger that fails.

What `check` enforces beyond required fields: `public_at` / `event_at` are `YYYY`, `YYYY-MM`,
`YYYY-MM-DD` or a timestamp **with** offset; quotes ≤ 120 words; `statement_id` points to a
`statement`; `supersedes` points to an existing id; `confidence` starts with high / moderate / low;
`alternative.weight` starts with primary / contributing / unlikely; `knowledge.direction` is
supports / undercuts; source `tier` is 1–3; `search` has `tool` and `query`; no conclusory words
in `claim` unless `attributed`.

Adapted from intel `references/evidence-standards.md` (claim status, source assessment, citation
integrity) and InvestSkill `fact-check` (claim ledger, source tiers, verdicts).

## Record fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | `E001`, `E002`, … unique in the case |
| `stage` | yes | `market-event`, `trigger`, `issue`, `statement`, `comparison`, `knowledge`, `external`, `parties`, `economics`, `claim`, `timeline`, `verify` |
| `kind` | yes | See kinds below |
| `claim` | yes | One proposition, in neutral words |
| `status` | yes | `fact`, `attributed`, `inference`, `assumption`, `estimate`, `gap` (definitions below) |
| `quote` | for `statement`, `revelation`, and any record citing a document | Exact text, verbatim, ≤ 120 words |
| `source` | unless `status` is `inference` or `gap` | Object, see below |
| `public_at` | for anything that reached the market | ISO timestamp (with time zone) when it became public |
| `event_at` | when different from `public_at` | When the underlying thing happened |
| `refs` | for `inference`, `comparison` | IDs of the records the inference rests on |
| `confidence` | for `inference`, `comparison` | `high`, `moderate`, `low` + one-line reason |
| `verified` | set by stage 12 (verify) | `quote-match`, `number-recomputed`, `source-reopened`, `failed: <reason>` |
| `supersedes` | optional | ID of a record this one corrects |

`source` object:

| Field | Meaning |
|---|---|
| `title` | Document title as published |
| `publisher` | Issuer, court, regulator, outlet |
| `doc_type` | e.g. `10-K`, `10-Q`, `8-K`, `annual report`, `ad hoc announcement`, `RNS`, `earnings call transcript`, `press release`, `docket entry`, `opinion`, `news`, `short report`, `script output` |
| `url` | The address actually opened |
| `doc_id` | Accession number, docket number + entry, Bigdata.com document ID, etc. |
| `location` | Item/Note/page/paragraph, or transcript speaker + section |
| `tier` | 1 primary, 2 secondary, 3 discovery only (see `source-hierarchy.md`) |
| `retrieved_at` | ISO timestamp of retrieval |

## Kinds

| Kind | What it records | Extra fields |
|---|---|---|
| `market` | A number from `scripts/market_event.py`, written by `ledger.py add-market` | `metric`, `value` (number, or null with `text` for the class and flags), `unit`, `event_at` = day 0; `source.doc_type` = `script output` and `source.location` = JSON path |
| `revelation` | Adverse information reaching the market | `channel` (company / news / court / regulator / short seller / analyst), `speaker` |
| `statement` | Something the company said before the drop | `speaker`, `venue`, `statement_type` (see `statement-types.md`), `topic`, `cautionary_language` (quoted, if any) |
| `comparison` | One prior statement set against later facts | `statement_id`, `revelation_ids`, `apparent_inconsistency`, `contrary_evidence_ids`, `innocent_explanation`, `wording_change` |
| `knowledge` | Evidence bearing on what management knew and when | `indicator` (see knowledge-indicators skill), `direction` (supports / undercuts) |
| `external` | Court, regulator, reporting, short-seller items | `forum`, `case_or_matter` |
| `event` | Timeline entry not covered above | — |
| `alternative` | A competing explanation for the drop | `weight` (primary / contributing / unlikely) + reason |
| `gap` | Something we could not establish | `would_be_settled_by` |
| `search` | A search performed (for the coverage record) | `tool`, `query`, `date_range`, `results` (count) |
| `party` | Issuer identity, listing, insider, director, officer, auditor, underwriter, related party | `role` (issuer / listing / officer / director / auditor / underwriter / insider / related party / plaintiff), `name`, `tenure`, plus `ticker`, `cusip`, `isin`, `jurisdiction` for issuer/listing records |
| `capital` | Shares outstanding, market cap, cash, D&O insurance, compensation, insider trade | `metric`, `value`, `unit`/`currency`, `as_of` |
| `offering` | A securities offering in or near the Class Period | `date`, `security`, `price`, `gross_proceeds`, `agents`, `use_of_proceeds` |
| `proceeding` | A parallel or competing proceeding (class action, derivative suit, regulator case, CCAA) | `forum`, `docket`, `filed`, `counsel`, `class_period`, `proceeding_status`, `corrective_dates` |
| `framing` | A claim-framing element from stage 10: class definition, class period end, defendant, cause of action chosen, linkage-matrix row | `element` (class / period / defendant / cause / linkage), `text`, `refs` |
| `issue` | The stage 3 issue definition | `subject`, `search_terms`, `lookback`, `case_types`, `themes` |
| `economics` | A number from `scripts/economics.py` | `metric`, `value`, `unit`/`currency`, `formula`; `source.doc_type` = `script output`, `source.location` = JSON path |
| `legal` | A legal proposition used in the memo, with its authority | `citation`, `pinpoint`, `text` (verbatim from `legal-library.md` or the verified source), `verified` (`library` / `checked: <url>`), `forum` |
| `decision` | The recommendation (one per case; supersede to revise) | `recommendation` (`pursue` / `pursue-hold` / `monitor` / `pass`), `reasons`, `refs` (records it rests on), `would_change_if`, `next_catalyst`, `deadlines` |

## Claim status (from intel evidence standards)

| Status | Meaning | Treatment |
|---|---|---|
| fact | Supported by an inspected record or a script measurement | Cite exact support |
| attributed | A party asserted it (company, plaintiff, short seller, journalist) | Name the party; never adopt it silently |
| inference | Judgment derived from other records | List `refs`; state the alternative |
| assumption | Unverified premise used to proceed | Label it; say why it was needed |
| estimate | Approximate quantity | Show method and inputs |
| gap | Not established | Say what would settle it |

An allegation in a complaint or short report is `attributed`, never `fact`. An adjudicated finding
in a judgment is `fact` about what the court found, and `attributed` as to the underlying events if
it is under appeal.

## Example lines

```json
{"id":"E004","stage":"statement","kind":"statement","status":"fact","claim":"Q2 2025 10-Q described the construction litigation as not expected to have a material adverse effect.","quote":"…we do not believe the outcome will have a material adverse effect on our financial position…","speaker":"Company","venue":"10-Q","statement_type":"opinion","topic":"construction litigation exposure","cautionary_language":"…litigation is inherently uncertain…","public_at":"2025-08-05T16:10:00-04:00","source":{"title":"Form 10-Q for the quarter ended June 30, 2025","publisher":"Issuer","doc_type":"10-Q","url":"https://www.sec.gov/Archives/edgar/data/…","doc_id":"0001689796-25-000123","location":"Part II, Item 1 Legal Proceedings, p. 41","tier":1,"retrieved_at":"2026-10-19T14:02:00Z"}}
{"id":"E017","stage":"comparison","kind":"comparison","status":"inference","claim":"The Q2 2025 assessment appears inconsistent with the trial-court ruling issued six weeks earlier.","statement_id":"E004","revelation_ids":["E011"],"apparent_inconsistency":"The ruling (E009, public 2025-06-20) rejected the company's main defense before the 10-Q was filed.","contrary_evidence_ids":["E012"],"innocent_explanation":"The company may have expected to win on appeal (E012 quotes counsel's appeal notice).","wording_change":"Same wording as Q1 2025; no mention of the ruling.","refs":["E004","E009","E011","E012"],"confidence":"moderate — ruling text confirmed; company's internal assessment unknown"}
```
