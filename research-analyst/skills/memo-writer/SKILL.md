---
name: memo-writer
description: Stage 10 of a research-analyst investigation. Renders the research memo in Markdown, in the seven-section structure, strictly from the verified case ledger, with record-level citations, open questions and a source list. Use only after the verify stage passes.
---

# Memo writer (stage 10)

v1 structure, reconstructed from the October 4 and 15 calls. To be replaced by Andrew's own template
in v2. Output: `runs/<date>/<TICKER>/memo.md`.

Every factual sentence ends with ledger citations, e.g. `[E004]`, which link to the Sources list.
Follow `references/language-rules.md`.

## Structure

```markdown
# Research memo: <Company> (<EXCH:TICKER>), drop of <date>

Prepared <date>. Research only; not legal advice. Status: <conclusion scale value>.

## Summary
Five bullets: the drop and its abnormal size; the trigger; the key prior statement(s); the main
apparent inconsistency (or that none was found); the main open question.

## 1. Company overview
Business, securities and listings (exchange, ADR, OTC), incorporation, relevant operations.

## 2. Parties
Company, relevant subsidiaries, executives and directors (with tenure dates), auditors,
counterparties, courts and regulators involved.

## 3. Background and history
Narrative of events leading to the decline, then the full timeline table (stage 8).

## 4. Total mix of information
4.1 Issue definition
4.2 Statement trail: every prior statement on the issue, in date order, quoted, with type
4.3 Comparison: one block per material statement: statement, later facts, apparent inconsistency,
    wording change, contrary evidence, innocent explanation, confidence
4.4 Knowledge indicators: supporting and undercutting, dated

## 5. Corrective disclosure(s)
What reached the market, when, from whom, how; earlier partial disclosures; competing explanations.

## 6. Market reaction
Table: close before/after, return, market and peer returns, abnormal return, t, two-day abnormal
return, volume vs average, market value lost; earlier related drops. One line on what the figures do
and do not show (observed reaction, not attributed loss).

## 7. Analysis and conclusion
- Conclusion (scale below) and the three to five records it rests on
- Strongest points for further investigation
- Strongest points against
- Existing litigation
- Open questions (each with the source that would settle it)

## Sources
[E001] Title, publisher, document type, date, locator, link
…

## Coverage
Sources searched and date ranges; quarters checked; known gaps.
```

## Conclusion scale

| Value | Use when |
|---|---|
| **Warrants further investigation** | At least one specific prior statement on the issue appears inconsistent with facts that existed when it was made, and the drop is company-specific and tied to the same subject |
| **Possible, evidence incomplete** | An apparent inconsistency exists, but timing of knowledge or the link to the drop is not yet established |
| **No apparent basis on current evidence** | The company disclosed the specific risk, or the facts arose after the statements, or the drop is not tied to the subject |

The scale describes the research, not legal merit. Always state what evidence would move the case
up or down a level.
