---
name: disclosure-history
description: Stages 3 to 5 of a research-analyst investigation, the intellectual center of the memo. Defines the issue the adverse news concerns, retrieves every prior company statement on that issue over the lookback period (filings, announcements, earnings calls, presentations), and compares each statement with what later became public. Use after the trigger is established, or whenever earlier company statements on a subject must be collected and compared.
---

# Disclosure history (stages 3–5)

## Stage 3: define the issue (checkpoint)

From the trigger, write one `issue` record:
- **Subject**: the precise matter (e.g. "exposure in the X construction litigation", "production at
  the Y mine after the coup", "Phase 2 trial Z enrollment and data").
- **Search terms**: names, project codes, case names, counterparties, product names, synonyms the
  company uses; in the filing's language for non-English issuers.
- **Lookback**: 2 years by default, never more than 3; shorter if the subject arose more recently
  (start from its first mention).
- **Related earlier drops** from stage 1 that may belong to the same story.

**Stop and show the issue definition to the user. Continue only after they confirm or correct it.**
A wrong issue definition wastes everything downstream.

## Stage 4: collect prior statements

Not a summary of every filing: only passages on the issue.

| Source | Sections to read |
|---|---|
| Annual reports / 10-K / 20-F / 40-F / AIF | Business, risk factors, legal proceedings, MD&A, contingencies and subsequent-events notes, critical accounting estimates |
| Interim reports / 10-Q / half-year | MD&A, legal proceedings, risk factor updates, contingencies note |
| Announcements / 8-K / RNS / ad hoc | Every announcement that mentions the subject |
| Earnings calls | Prepared remarks and Q&A; analyst questions on the subject are especially telling (what was asked, how it was answered) |
| Investor presentations, capital markets days, offering documents | Statements on the subject; offering documents carry extra weight |

Method (adapted from InvestSkill `financial-report-analyst` and `10k-digest`, and Bigdata.com
`risk-assessment`):

1. **US**: list filings from EDGAR submissions for the lookback; run EDGAR full-text search for
   each search term restricted to the company's CIK and date range; open every hit and the
   matching sections of every 10-K/10-Q even without a hit (silence is also evidence).
2. **All countries**: Bigdata.com fast mode, entity filter, category `filings` and separately
   `transcripts`, one search term per query, one fiscal year per query; fetch full documents for
   hits (`bigdata_fetch_document`). Then issuer IR site for anything missing (annual reports,
   presentations).
3. For each passage write a `statement` record: verbatim quote, speaker, venue, `public_at`, exact
   locator, `statement_type` (`references/statement-types.md`), cautionary language quoted if any.
4. Save the text of every source document used under `runs/<date>/<TICKER>/sources/`.

Coverage rule: for every quarter in the lookback, record whether the periodic report and the call
were checked and whether they mention the subject. A quarter with no record is a gap, not "silent".

## Stage 5: compare

Build the **statement trail**: all `statement` records on the issue in date order, side by side
with what was happening at each date (from stages 2, 6 and 7 as they arrive).

Then one `comparison` record per material statement:

| Field | Content |
|---|---|
| `statement_id` | The prior statement |
| `revelation_ids` | Later facts that bear on it |
| `apparent_inconsistency` | One neutral sentence: what the later facts show relative to the statement |
| `wording_change` | How the passage changed from the previous period, if at all (added / removed / softened / hedging escalated) |
| `contrary_evidence_ids` | Records pointing the other way (e.g. the company did disclose the specific risk) |
| `innocent_explanation` | The strongest benign reading (bad luck, new facts after the statement, genuine uncertainty disclosed) |
| `confidence` | high / moderate / low + reason |

Questions to work through for each comparison (evidence, not conclusions):
- Did the later facts exist, or were they developing, on the statement date? Which record shows it?
- Was a risk presented as hypothetical when it had already occurred?
- Did the company speak on the subject (making omissions relevant) or stay silent throughout?
- Was the specific risk disclosed concretely before the drop? If so, cite it: this cuts against
  an inconsistency and must be recorded.
- Was the statement forward-looking, and what exactly did its cautionary language say?

Note: a generic risk warning is not necessarily disclosure of a specific known problem, and a poor
outcome does not by itself show an earlier statement was wrong. Record both possibilities.
