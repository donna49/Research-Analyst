# Memo forms: choosing the exact form

Andrew writes in four forms. Each file in this folder reproduces one of them exactly, copied from his
own memos: the header lines, the headings (capitalization and punctuation as he writes them), the
order, the way paragraphs open, the footnote style and the sign-off. The memo-writer picks **one**
form per case and follows it exactly. It never blends forms, and it adds no section, label or table
that the form does not have.

| Form | File | His models | Use when |
|---|---|---|---|
| **A. 2026 form** | `form-A-2026.md` | Slate Grocery (Sept 25, 2026), FiServ II (Sept 24, 2026) | Pursue / pursue-hold on guidance cuts, dividend cuts, regulatory or enforcement matters, accounting, M&A, CDR or cross-listed issuers, US parallel actions. **Default** when nothing else fits |
| **B. IRAC form** | `form-B-irac.md` | Global Atomic (Jan 26, 2025 / Jan 28, 2026), Li-Cycle (June 4, 2026) | Pursue on omission-driven theories needing a structured legal analysis: conditional financing, government loans, insider trading, oppression and certification strategy |
| **C. Litigation Opportunity form** | `form-C-opportunity.md` | Ascot Resources (Aug 3, 2025), Alamos Gold (Oct 24, 2025) | Pursue on mining, project and ramp-up cases and contract terminations (Ascot); **every Monitor** (Alamos variant) |
| **D. Pass form** | `form-D-pass.md` | Paladin Energy (Dec 18, 2023 / June 12, 2025) | **Every Pass**: the recommendation comes first in an Executive Summary |

Selection order (when the issue record lists several case types, use the type of the **lead
misrepresentation theme**, i.e. the one the theory turns on, not the first rule that matches):
1. The decision is `pass` → D.
2. The decision is `monitor` → C, Alamos variant.
3. The case type (`case-types.md`) is 2 (mining/project) or 4 (contract termination) → C, Ascot variant.
4. The case type is 3 (conditional financing), 8 (insider trading) or 12 (derivative) → B.
5. Otherwise → A.

Record the choice and its rule as a `framing` record (`element: "form"`). If the user names a form, use
it.

## Rules common to all four forms

- **Footnotes, not inline citations.** The body carries pandoc footnotes (`[^1]`), numbered in order.
  The footnote text is written the way he writes it:
  - "Q1 2024 MD&A (May 13, 2024), at pages 4 and 6."
  - "Affidavit of Derek White (November 1, 2024), at paragraph 33."
  - "News Release NR24.05, Ascot Provides Construction Update on the Premier Gold Project (February 20, 2024)."
  - "OSC Form 13–502F1 (SEDAR, August 29, 2024)."
  - "[Article](url)." or "[News Release](url)." for web sources
  - case cites in his form, e.g. "*LBP Holdings Ltd v. Hycroft Mining Corp*, 2020 ONSC 59, at para. 20."

  A footnote may carry his kind of commentary: "CURIOUS. The date casually changes from Q3 to the
  second half of 2024 without reason; compare to the statement released on May 13, 2024." or "A FOIA
  Request topic."
- **No ledger ids in the memo.** The trace lives in `memo_trace.json`, which maps each footnote and
  each figure line to ledger ids. `ledger.py memo` checks it.
- **Figures** come from scripts or quoted documents, as always. He writes prices as "$0.94 down to
  $0.64 (down 31.9%)" or "from $0.44 to $0.19", and adds "on record volume of 14.4 million shares" when
  the volume figure supports it.
- **His working notes** go in brackets inside quoted material, as he does: "[No reference to lack of ore
  to mill]", "[Emphasis added]".
- **Nothing he does not write.** No "Draft submissions for review" labels. No Sources, Coverage or
  pipeline appendices. No owners on next steps. No ledger tables. All of that goes in `memo_annex.md`,
  the internal companion file. A Defined Terms list appears only where the form has one.
- **Market and economics figures** are footnoted the way he would source them, not as "script
  output": "TSX trading data, close on July 30, 2024 (tenth trading day after the correction)." or
  "Calculated from TSX trading volume, November 10, 2023 to January 23, 2025." The ledger id goes in
  `memo_trace.json`.
- **Copy his structure and stock phrases, but correct his grammar slips** ("misrepresentations that
  is", "materials facts", "if leave it granted", "Pubic"). The forms already give the corrected text.
- **Dates** are written as "January 23, 2025" in the body, and "Q3 2023 MD&A", "F/2023 AIF", "1Q", "2Q"
  as he writes them.
- **Rendering:** `scripts/render_memo.py` turns `memo.md` into a Word file with real footnotes and his
  letterhead footer. The memo-writer uploads it to the user's Drive as a Google Doc (see memo-writer §5).
