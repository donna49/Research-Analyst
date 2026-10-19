# Language rules

The memo is internal lawyer work product. It contains two kinds of text, and each has its own rule.

## 1. Findings (ledger claims; the factual parts of every section)

Every sentence of fact must survive being read aloud to the company's counsel.

| Avoid in findings | Write instead |
|---|---|
| fraud, fraudulent, scheme, lied, deceived, concealed | "did not disclose", "the later disclosure stated…", "appears inconsistent with" |
| misled investors | "investors were told X on [date]; on [date] Y became public" |
| knew (as a conclusion) | "evidence bearing on knowledge includes…" |
| false, untrue (as a conclusion) | "appears inconsistent with [record]" |
| caused the losses | "the price fell X% (abnormal −Y%) on the day the information became public" |
| clearly, obviously, undeniably | state the evidence and let it speak |

- Attribute allegations: "the short-seller report alleges…", "the US complaint alleges (para. 57)…".
- Distinguish a court's finding from a party's argument, and a ruling under appeal from a final one.
- Give the date with every statement and every revelation.
- `ledger.py check` enforces these rules on ledger claims.

## 2. Draft submissions (Andrew's voice)

These appear in THE MISREPRESENTATION(S), BEAR v. BULL and CONCLUSIONS, and only there.

- Write as Andrew drafts: "It is my submission that…", "I recognize that there are tangible concerns
  that…", "I recommend…".
- Use the legal terms of art: misrepresentation, omission of a material fact, public correction,
  reasonable investigation, oppression. These are the elements being pleaded, not findings.
- Every submission rests on cited records, and the record ids appear in the same paragraph.
- Fraud and knowledge appear only as what discovery may show ("With the benefit of discovery, the
  Plaintiff may be able to add a cause of action for common law fraud…"). The memo never states
  them as facts.
- No "draft" labels in the memo. Andrew's forms do not have them, and the memo is his internal work
  product. Drafts are drafts until he adopts them.

## Never, in either kind of text

- A number not produced by a script or quoted from a document.
- A citation not in `legal-library.md`, or not verified and recorded as a `legal` record.
- A name, ticker or fact from another case. Exemplar memos teach method only.
