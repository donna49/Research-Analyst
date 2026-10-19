#!/usr/bin/env python3
"""Render a memo written in one of Andrew's forms (references/memo-forms/) to Word with real footnotes.

  render_memo.py runs/<date>/<TICKER>/memo.md [--letterhead] [--out memo.docx]

memo.md is pandoc markdown: blank-line separated paragraphs, footnotes as [^n]. Heading lines (his
capitalised headings such as OVERVIEW, PART A. FACTS, Preamble, Conclusion) are set in bold. The
Word file uses Times New Roman 12 pt; --letterhead adds his Washington letterhead as the page footer
(Form A memos carry it). Upload the .docx with the Google Drive connector to get a Google Doc with
native footnotes (see skills/memo-writer §5). Requires pandoc and python-docx.
"""
import argparse, os, re, subprocess, sys, tempfile
from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
LETTERHEAD = os.path.join(HERE, "..", "references", "memo-forms", "letterhead.txt")
MIXED_HEADINGS = {"Preamble", "Proposed Class Period", "Defined Terms", "Overview", "Background",
                  "The Beginning of the Class Period", "Post Class Disclosures", "The Causes of Action",
                  "The Rules and Laws", "Executive Summary", "Chronology of Events", "Overview of the Claim",
                  "The Law", "Causes of Action", "Conclusion", "Conclusions", "Side-bar submissions:",
                  "The Public Corrective Statements", "Post Class Period Disclosures", "Undisclosed Contractor Claims"}


def is_heading(line):
    s = line.strip()
    if not s or len(s) > 90 or s.startswith(("|", "-", ">", "[^", "(")) or "[^" in s:
        return False
    if s in MIXED_HEADINGS or re.match(r"^(PART [A-Z_]+\.|\([A-C]\) .+Misrepresentation|Theory No\.\d)", s):
        return True
    letters = re.sub(r"[^A-Za-z]", "", s)
    return len(letters) >= 4 and letters.isupper() and not s.endswith((".", ";", ","))


def prepare(md):
    out = []
    for line in md.splitlines():
        out.append(f"**{line.strip()}**" if is_heading(line) and not line.startswith("**") else line)
    return "\n".join(out) + "\n"


def reference_docx(path, letterhead):
    ref = subprocess.run(["pandoc", "-o", path, "--print-default-data-file", "reference.docx"], capture_output=True)
    if ref.returncode:
        sys.exit(ref.stderr.decode())
    d = Document(path)
    for name in ("Normal", "Body Text", "First Paragraph", "Footnote Text", "Compact"):
        try:
            st = d.styles[name]
        except KeyError:
            continue
        st.font.name = "Times New Roman"
        st.font.size = Pt(10 if name == "Footnote Text" else 12)
    if letterhead:
        footer = d.sections[0].footer
        footer.paragraphs[0].text = open(LETTERHEAD).read().strip()
    d.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("memo")
    ap.add_argument("--out")
    ap.add_argument("--letterhead", action="store_true")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.memo)[0] + ".docx"
    md = prepare(open(a.memo).read())
    with tempfile.TemporaryDirectory() as td:
        ref = os.path.join(td, "ref.docx")
        reference_docx(ref, a.letterhead)
        src = os.path.join(td, "memo.md")
        open(src, "w").write(md)
        r = subprocess.run(["pandoc", src, "-f", "markdown+footnotes-smart", "-t", "docx",
                            "--reference-doc", ref, "-o", out], capture_output=True)
        if r.returncode:
            sys.exit(r.stderr.decode())
    n = len(set(re.findall(r"\[\^(\w+)\]:", md)))
    print(f"wrote {out} ({n} footnotes)")


if __name__ == "__main__":
    main()
