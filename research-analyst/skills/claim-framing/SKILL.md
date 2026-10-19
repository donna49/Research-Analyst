---
name: claim-framing
description: Stage 10 of a research-analyst investigation, where Andrew's legal judgment is applied. Turns the evidence into the frame of a potential claim, as `legal`, `proceeding` and `decision` ledger records. Covers the forum and jurisdiction, causes of action, class periods and class definitions, the impugned-document × misrepresentation × correction linkage matrix, the parallel and competing proceedings map, limitations, Bear v. Bull, and a recommendation of Pursue, Pursue-hold, Monitor or Pass. Use after stages 4–9, or when asked whether there is a claim worth issuing.
---

# Claim framing (stage 10)

Read first: `references/andrew-method.md` (§1–4), `references/case-types.md` (the playbook for this
case type), `references/legal-library.md`, `references/jurisdictions.md`, and the one or two
closest exemplars in `references/corpus.md` (read them through the Google Drive connector). The
exemplars teach method and voice. Never copy their facts.

Everything here is a **draft for Andrew's review**. You build the strongest frame the records
support, then attack it as hard as defence counsel would.

## 1. Forum and jurisdiction
Work through `jurisdictions.md` steps 1–4. Record one `legal` record for the chosen forum hook
(reporting issuer / responsible issuer / CDR), citing the library. Then record:
- the alternatives
- the forum non conveniens and jurisdiction risks
- the residual Canadian class after US and foreign carve-outs (from the economics volume split)

## 2. Parallel and competing proceedings (`proceeding` records)
Search for each of the following, one `search` record per query:
- US class actions: CourtListener NOS 850 with the party name, and plaintiff-firm announcements.
  Record the docket, class period, counsel and CWs. Read the complaint's misrepresentation and
  corrective-date paragraphs; they are a roadmap, attributed as allegations.
- Canadian class actions: news, firm websites, and the Class Proceedings registries where available.
- Foreign actions: Australia, UK, Germany KapMuG.
- Derivative suits, demand letters, regulator proceedings, CCAA or bankruptcy (monitor reports are a
  source).

Plaintiff-firm "investigation" notices are signals, not suits. Record them as `external`.

## 3. Class Period and impugned documents
- **Start:** the first impugned document. Andrew keeps the set lean: the MD&As and the offering
  documents. Add other statements only where they carry the theory, e.g. an earnings-call
  reaffirmation or a "fully funded" release. Note alternative starts tied to specific documents
  (Barrick: "Could start on February 15, 2017 when MD&A released").
- **End:** the last correction, at the close of the reacting session.
- **Statutory class vs common-law class:** these can differ. In Slate the common-law class covered
  all holders before the correction, while the OSA class began on Aug 6, the first impugned
  document. Write both in his wording (see `memo-template.md`).
- **Primary-market classes:** one for each offering in the period (s. 130).
- Re-run `economics.py` if the start date moved.

## 4. Causes of action (`legal` records)
For each cause, record the elements verbatim from the library, with their citations:
- statutory (OSA s. 138.3 or the provincial equivalent)
- common-law negligent misrepresentation
- fraud, flagged "with the benefit of discovery"
- s. 130 where there were offerings
- oppression (s. 248) where insiders benefited or expectations were set by public statements
- a foreign state statute for US-incorporated issuers sued in Canada
- the US claim, if any, for referral

Add a cause only when the facts support it, and say which facts.

## 5. The linkage matrix
One row per impugned document × misrepresentation theme. Each row has: the statement record(s);
the omitted or contradicting fact with its date and record, which must have existed at the
statement date; and the correction that links back, quoting the linking words. Name each theme the
way Andrew does ("Fully Funded", "Commercial Production in Q3 2024", "The Dividend"). Leave out any
row whose contradicting fact post-dates the statement, and record it in Bear v. Bull as an
innocent explanation.

## 6. Defendants
- The issuer.
- Certifying officers for each impugned document.
- Directors, for the statutory claim.
- The auditor as expert, only if a misrepresentation sits in audited statements or the opinion.
- Underwriters, only for primary-market claims, or if they did "something more" than conventional
  banking.
- Related parties, for oppression.

Cite the `party` records for each.

## 7. Limitations
Copy the dates from economics. State the tolling step: serve the s. 138.8 leave motion with the
claim. Flag anything less than 6 months away.

## 8. Bear v. Bull
- **Bear.** Work through every item, and write "n/a: reason" where an item does not apply:
  - adverse precedent on the same theory (library table; case-type playbook)
  - forward-looking safe harbour and the cautionary language actually attached
  - s. 138.4(6) reasonable investigation, applied to each individual defendant using the
    s. 138.4(7) factors
  - materiality and price impact (abnormal return; look-back recovery)
  - causation breaks and competing explanations (stage 2 `alternative` records)
  - act of state or force majeure
  - jurisdiction and standing (foreign issuer, CDRs, *Leon v. VW*)
  - leave threshold and the judge's record (Leave tracker)
  - carriage and competing firms; certification of the common-law class
  - collectability (cash, D&O)
  - firm capacity, and defence counsel's posture if known
- **Bull.** For each bear item, give the distinguishing facts with record ids.
- **What would move it:** each piece of evidence that would change the assessment, the source that
  would supply it, and whether it is reachable now (FOIA, registries, a US docket) or only through
  discovery.

## 9. Decision (`decision` record)
Apply Andrew's rules from `andrew-method.md` §4:
- **pursue**: issue the claim.
- **pursue-hold**: issue and hold for the US or foreign mediation.
- **monitor**: name `next_catalyst` and its date, e.g. the next MD&A or a regulator report.
- **pass**: give the reason: too small, no lasting price effect, redundant, crowded, no supportable
  misrepresentation, or limitation expired.

The record must include:
- `refs`: the 3–5 records the decision rests on
- `reasons`
- `would_change_if`
- `deadlines`

Also record:
- a pre-issue offer idea where it fits (Slate: "Pay the full dividend, legal fees, notice, full
  release and bar order")
- the strategy (issue and hold; serve the leave motion with the claim; venue)

A **Pass** is a complete, valuable answer. Write it as carefully as a Pursue.

## 10. Output
Write `runs/<date>/<TICKER>/claim.md` with:
- forum
- proceedings table
- class definitions
- linkage matrix
- causes and elements
- defendants
- limitations
- Bear v. Bull
- decision

Every line cites ledger ids. Then stop and show the user the decision, the reasons and the deal
sheet figures before writing the memo. **This is the second checkpoint.**
