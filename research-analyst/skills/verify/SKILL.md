---
name: verify
description: Stage 12 of a research-analyst investigation. Re-opens every source, exact-matches every quote, recomputes every number, checks dates and attributions, and red-teams each apparent discrepancy before the memo is written. Use before rendering any memo or triage output, or when asked to check a research memo's evidence.
---

# Verify (stage 12)

Adapted from InvestSkill `fact-check` (claim ledger, verdicts, recompute every derived figure,
fabricated citation = failure) and `result-validator`, intel `intel-red-team`, and financial-services
`ib-check-deck` (number consistency across the document).

## 1. Mechanical checks (every record)

| Check | Pass rule | On failure |
|---|---|---|
| Quote match | The quote appears verbatim in the saved source text (whitespace and typographic quotes normalized) | Fix from the source or mark `failed`; never keep a paraphrase as a quote |
| Locator | The page/section/speaker given contains the quote | Correct the locator |
| Date | `public_at` matches the document's publication/filing time, not the period it covers | Correct; check fiscal-year confusion |
| Source opens | URL or document id resolves to the cited document | Replace or mark `gap` |
| Numbers | Every number traces to a script output or a quoted document; derived figures recomputed | Correct; supersede the record |
| Status | Allegations are `attributed`; inferences list `refs` | Re-label |
| Legal citations | Every `legal` record is verbatim from `legal-library.md`; items marked ⚠ or "(not from corpus)" have `verified: checked: <url>` | Check on CanLII / CourtListener, or drop the proposition |
| Economics | `economics.json` was re-run after the final Class Period was fixed; `economics` records match the JSON paths | Re-run and supersede |
| Same case | No `party`, `statement` or `legal` record carries another case's names (exemplar contamination) | Remove |

`scripts/ledger.py check` runs the structural checks and `scripts/ledger.py quotes` the quote
match against `sources/`; locator and source checks are done by re-reading the saved sources.
Set `verified` on each record. `scripts/ledger.py summary` lists records not yet verified and
open gaps.

## 2. Red team (each `comparison`)

For each apparent inconsistency, argue the other side as hard as the evidence allows:
- Was the later fact really unknown and unknowable on the statement date?
- Did the company disclose the specific risk somewhere else (another filing, a call, a footnote)?
  Search for it specifically.
- Is the drop explained by something unrelated (stage 2 alternatives)?
- Was the information already public before day 0?
- Is the "statement" actually puffery or a hedged projection with specific cautionary language?

Record the result in the comparison's `innocent_explanation` and `contrary_evidence_ids`, and lower
`confidence` where the red team succeeds.

## 2b. Red team the decision

Argue the opposite recommendation. For a Pursue, make defence counsel's best leave-motion argument.
For a Pass, ask what a competitor firm would see in the case. Check that the decision applies
Andrew's rules (`andrew-method.md` §4) to the economics flags. Record the result in the decision's
`would_change_if`. If the red team wins, supersede the decision and tell the user.

## 3. Gate

The memo writer may run only when:
- no record has `verified: failed` unless it is superseded or moved to gaps,
- every `comparison` has an `innocent_explanation`,
- every number in the planned memo maps to a `market` or `economics` record or a quoted document,
- there is exactly one current `decision` record.

After the memo is written, `ledger.py memo` must pass.

After the memo is drafted, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" memo <ledger> <memo.md>` must pass: every
cited id exists and is live, no conclusory wording outside quotations, every line with a
percentage or money figure cites a record, and percentages cited to `market` records match them.

Report: records checked, quotes matched, numbers recomputed, failures fixed, items moved to gaps.
