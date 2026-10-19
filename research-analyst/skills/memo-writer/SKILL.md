---
name: memo-writer
description: Final stage of a research-analyst investigation. Writes the memo exactly in one of Andrew Morganti's own four forms (2026 form, IRAC form, Litigation Opportunity form, Pass form), chosen by case, with real footnotes in his citation style, strictly from the verified ledger. Renders it to Word and, on the user's go-ahead, uploads it to their Google Drive as a Google Doc. Use only after verify passes and the claim-framing decision has been shown to the user.
---

# Memo writer (final stage)

Outputs, all under `runs/<date>/<TICKER>/`:
- `memo.md`: the memo, exactly in his form; footnotes as `[^n]`; no ledger ids.
- `memo_trace.json`: the form letter, plus the ledger ids behind every footnote and every figure line
  without a footnote.
- `memo_annex.md`: the internal companion: sources by ledger id, coverage, open questions, pipeline
  fields, deadlines. None of this goes in the memo.
- `memo.docx`: rendered with real footnotes. Becomes a Google Doc in the user's Drive (see §5).

## 1. Choose the form
Read `references/memo-forms/README.md` and apply its selection order (Pass → D; Monitor → C, Alamos
variant; mining/project/contract → C, Ascot variant; financing/insider/derivative → B; otherwise → A).
Record the choice as a `framing` record (`element: "form"`). Then read the chosen form file and the
model memo it names (Drive ID in `references/corpus.md`) **for form and voice only**.

## 2. Write `memo.md` in that form, exactly
- Use his header lines, headings, order, opening phrases and sign-off exactly as the form file gives
  them. Add no heading, label, table, summary block or appendix the form does not have.
- **Body content comes only from verified ledger records**: quotes from `statement` and `revelation`
  records, figures from `market` and `economics` records, law from `legal` records, judgments from the
  `framing` and `decision` records.
- **Footnotes** follow his style (README "Rules common to all four forms"): the document, date and
  pinpoint, written as he writes them, with his kind of commentary where the records support it.
  Every footnote is listed in `memo_trace.json` with its ledger ids.
- **Argument sections** (Misrepresentation(s), Analysis, Bear v. Bull, Conclusion) are written as
  continuous submissions in his voice ("It is my submission that …"), not as numbered checklists.
  Each factual assertion in them carries a footnote.
- **The price-first habit** in Forms B and C: "On «date», $«a» to $«b» (down «x»%), «TICKER» published
  …". Use `moves.json` for the figures.
- **Ten-day look-back** as he quotes it: the close on the 10th session (`lookback_close_10th`).
- Fix his known slips; never copy them (`references/andrew-method.md` §5; form notes).
- **No other case's facts.** Prior cases appear only by name, as analogy or precedent.

## 3. Write `memo_trace.json` and `memo_annex.md`
```json
{"form": "B",
 "footnotes": {"1": ["E037"], "2": ["E038", "E040"]},
 "lines": {"TSX: \"AOT\" from $0.44 to $0.19": ["E176"]}}
```
`lines` covers header lines that carry figures and no footnote (his deal lines in Form C, and the like).
The annex holds everything else the reader may want: a source list by ledger id, coverage, gaps, the
decision record, deadlines and the next catalyst.

## 4. Check
```
python3 scripts/ledger.py check runs/<date>/<TICKER>/ledger.jsonl
python3 scripts/ledger.py quotes runs/<date>/<TICKER>/ledger.jsonl
python3 scripts/ledger.py memo runs/<date>/<TICKER>/ledger.jsonl runs/<date>/<TICKER>/memo.md
python3 scripts/render_memo.py runs/<date>/<TICKER>/memo.md [--letterhead]   # --letterhead for Form A
```
Fix every problem before going on. Then compare your memo against the form's model side by side,
heading by heading. Any heading, phrase pattern or footnote style that differs is a defect.

## 5. Google Doc in the user's Drive
The user's standing choice is a Google Doc in their Drive.
1. Ask which Drive folder, unless the user has named one for this case or set a default. Never guess a
   shared drive. Uploading to a shared drive makes the memo visible to others.
2. Upload `memo.docx` with the Google Drive connector `create_file`:
   - `title`: "Memo from Morganti to File («Issuer short name»)(«Month D, YYYY»)", his file-naming pattern
   - `base64Content`: the .docx bytes, base64-encoded
   - `contentMimeType`: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
   - `parentId`: the folder id
   Drive converts it to a Google Doc with native footnotes.
3. Give the user the link. Record the Doc id in `memo_annex.md`.

## 6. Reply
Give:
- the form used and why
- the recommendation
- the three to five records it rests on
- the key figures
- the nearest limitation date
- the open questions
- the paths: `memo.md`, `memo.docx`, `memo_annex.md`
- the Doc link, if uploaded
