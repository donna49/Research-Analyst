---
name: memo-writer
description: Final stage of a research-analyst investigation. Renders the memo in Andrew Morganti's own form (CONFIDENTIAL / LAWYER WORK-PRODUCT; deal sheet; Overview; Total Mix of Information; Public Corrective Disclosure; Parties; Potential Class Proceeding; The Misrepresentation(s); Parallel Proceedings; Bear v. Bull; Conclusions), strictly from the verified case ledger, with footnote citations, then lints it. Use only after verify passes and the claim-framing decision has been shown to the user.
---

# Memo writer (final stage)

Output: `runs/<date>/<TICKER>/memo.md`. A Google Doc copy is made only when the user asks (see §5).

Read first:
- `references/memo-template.md`: the structure, section by section
- `references/andrew-method.md` §5: his voice
- `references/language-rules.md`: the difference between findings and draft submissions
- the closest A-grade exemplar in `references/corpus.md`, through the Google Drive connector, for
  tone and density

## 1. Inputs
- The ledger, with every record verified. The memo is rendered from the ledger; a sentence with no
  record behind it does not go in.
- `claim.md` (stage 10) and the `decision` record.
- `parties.md`, `economics.json` and `moves.json`.

## 2. Rules
1. **His structure, his headings, in his order** (`memo-template.md`). Sections that do not apply
   stay in, with one line saying why.
2. **Deal sheet first.** Every figure comes from an `economics` or `market` record.
3. **Total mix in his form:** "On «date», «TICKER» published its «document» and reported, in
   relevant part:", then verbatim quotes, then the price move for that date. Each quote is footnoted
   to its record, which gives the document, page or paragraph, and link.
4. **Corrections:** label a STORM WARNING separately; quote the linking words; give the market
   impact from records; give the competing explanations.
5. **Draft submissions** (Misrepresentation(s), Bear v. Bull, Conclusions) are in his voice, are
   labelled *Draft submissions for review*, and cite record ids in the same paragraph.
6. **Legal text only from `legal` records.** These are verbatim from `legal-library.md` or a
   verified source. Any item marked ⚠ or "(not from corpus)" must have a `verified: checked: <url>`
   record before it is used.
7. **Numbers.** Every figure on a line carries a citation on that line. Keep currencies separate and
   name each one. Percentages are copied from script output, never recomputed.
8. **No other case's text.** Exemplars are for voice only. The lint fails on any ticker the ledger
   never mentions.
9. **Defined terms** are introduced in the form ("XYZ"), and collected in Appendix A.
10. **Citations:** write `[E###]` inline in the draft; they become footnotes when rendered.
    Appendix B lists each record with title, publisher, type, date, locator and link.
11. **Coverage (Appendix C):** sources searched with date ranges, quarters checked, and open
    questions, each with the source that would settle it.

## 3. Length and density
Match the case. A Pass memo can be 1,500 words with the recommendation up front (Paladin). A Pursue
memo with several themes runs 4,000–6,000 words with 30–60 footnotes (Ascot, Global Atomic). Do not
pad. Andrew's best memos are dense with quotes and dates, not with commentary.

## 4. Lint, then reply
```
python3 scripts/ledger.py check runs/<date>/<TICKER>/ledger.jsonl
python3 scripts/ledger.py quotes runs/<date>/<TICKER>/ledger.jsonl
python3 scripts/ledger.py memo runs/<date>/<TICKER>/ledger.jsonl runs/<date>/<TICKER>/memo.md
```
Fix every problem before replying. Then reply with:
- the recommendation
- the 3–5 records it rests on
- the deal-sheet figures
- the nearest limitation date
- the open questions that matter most
- the path to `memo.md`

## 5. Google Docs (only when asked)
Andrew's memos live as Word or Google Docs in the firm's Drive. When the user asks for a Doc:
- create it with the Google Drive connector (`create_file`, Google Docs MIME type) from the
  rendered memo, with footnotes as numbered endnotes
- title it "Memo from Morganti to File («Issuer»)(«Month D, YYYY»)"
- put it in the folder the user names; never guess a shared drive
- give the user the link

Creating a file in the firm's Drive puts it where others can see it. Confirm the destination folder
first.
