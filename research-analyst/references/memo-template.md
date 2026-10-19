# Memo content checklist

> **Structure and wording now come from `references/memo-forms/`**: four exact forms copied from
> Andrew's memos, chosen by case. This file is kept as the content checklist, i.e. what the research
> must be able to support. It is not a layout. The deal-sheet table, PARTIES heading, labels and
> appendices below belong in `memo_annex.md`, not in the memo.


This template combines the shape of Slate Grocery (Sept 25, 2026) and FiServ II (Sept 24, 2026),
the summary block at the top of Ascot and Alamos, the corrective-disclosure method of Aurora
(Dec 2023), and the IRAC analysis of Global Atomic and Li-Cycle. Sections appear in this order.
A section that does not apply stays in the memo with one line explaining why ("No offerings during
the Class Period.").

Fill-in markers used below:
- `«…»` marks content to supply. Every `«…»` must be replaced before the memo is final;
  `ledger.py memo` fails on any that remain.
- `[E###]` is a ledger citation, rendered as a footnote.

---

```
CONFIDENTIAL
LAWYER WORK-PRODUCT

Date: «memo date»«; updated from «earlier date» if this is a revision»
From: Andrew Morganti
To: «File | firm leadership | co-counsel named by the user»
Re: In re «Issuer full name» («"TICKER"») Securities Litigation«: subtitle naming the theme or the individual defendants, optional»
—------------------------------------------------------------------------------------- /
```

## Deal sheet (always; one block, before the Overview)

| | |
|---|---|
| Exchanges and tickers | «TSX: "X"; NYSE: "X"; OTCQX: "XF"; …» |
| CUSIP / ISIN | «…» |
| Drop | «$A to $B (−x%) on «date», volume «n»× the 30-day average; abnormal −y% (t = z)» |
| Proposed Class Period | «start» to «end» (statutory) / «…» (common law) |
| Public Corrective Disclosure(s) | «dates»; storm warning(s): «dates or "none"» |
| Class Period market capitalization | «range, currency» ; post-correction «value» |
| Damages (rough) | statutory «range» ; common law «range» |
| Liability limit (5% cap) | «value» |
| D&O insurance / cash | «amount or "not disclosed"» / «cash at last balance sheet» |
| Settlement target | «range» |
| Case analogy | «closest prior case from corpus.md / legal-library.md» |
| Recommendation | **«Pursue — issue the claim / Pursue — issue and hold / Monitor until «catalyst, date» / Pass — «reason»»** |
| Limitation clock | s. 138.14 runs «date»; common law runs «date» |

## OVERVIEW

The issuer's identity in one paragraph: «Issuer» («"TICKER"» and CUSIP), a «statute / jurisdiction of
incorporation» company headquartered at «address», which describes itself as:

> «self-description, quoted from the AIF / 10-K» [E…]

Then:
- Listings and securities (each class, each exchange); reporting-issuer provinces.
- Market capitalization range during the Class Period; shares outstanding [E…].
- Business segments and key assets relevant to the theory.
- Insiders, controlling holders and related parties, with holdings.
- **The theory in one paragraph:** what was said, what was omitted, what came out, and the market's
  reaction ("The market's reaction was harsh and immediate…" only when the figures support it).

## TOTAL MIX OF INFORMATION

Chronological, from about a year before the Class Period to the correction. One entry per
disclosure:

> On «date», «TICKER» published its «document» and reported, in relevant part:
> - «verbatim quote» [E…]
> - «verbatim quote» [E…]
>
> «Price: $a to $b («±x%» or "nil%"), volume «n»× average [E…]»

Rules:
- Divide into **pre–Class Period**, **Class Period** and, where relevant, **post–Class Period**
  disclosures.
- Name the speaker on calls and the analyst who asked the question («UBS. Response, …»).
- Put working notes in brackets, labelled: «[Note: the Q3 date becomes "second half" without
  explanation]».
- Insert a **drift table** when the company gave dated promises or guidance:

| Disclosure | «date 1» | «date 2» | … | Correction |
|---|---|---|---|---|
| «metric / promised date» | «value» [E…] | … | … | «value» [E…] |

## PUBLIC CORRECTIVE DISCLOSURE

For each correction (storm warnings labelled **STORM WARNING**):
- When it reached the market (time stamp and session) and how (release, filing, call, article,
  analyst note, court filing).
- The corrective words, quoted, with each passage **linked** to the misrepresentation it corrects.
- Market impact: «close before → close after, −x%; abnormal −y% (t), volume n× average, market value
  lost; price on the 10th trading day afterward» [E… from market/economics records].
- Competing explanations for the drop (other news that day, market moves), each with its weight.

Then **Insider trading.** List trades by officers and directors in the six months before the Class
Period and during it (SEDI / Form 4 / PDMR), or state "none reported" with the search record [E…].

## PARTIES

- Plaintiff: «to be identified»; note any client already in hand.
- Corporate defendant, plus subsidiaries that carry the operations.
- Individual defendants: certifying CEO and CFO for each impugned document; directors; tenure
  dates; compensation for the year before the correction (from the circular / proxy).
- Gatekeepers: auditor (opinion dates, fees, any change); underwriters and agents of offerings in
  the Class Period.
- Offerings during or near the Class Period (table): date, security, price, gross proceeds,
  agents, use of proceeds [E…].

## POTENTIAL CLASS PROCEEDING

**A. Forum and jurisdiction.** Why this forum: reporting-issuer status, or a real and substantial
connection (responsible issuer), CDRs, Canadian holders, US listing. State the alternative forums
and the forum non conveniens risk. (See `jurisdictions.md`.)

**B. Causes of action.** Lettered, one sentence each, as questions in his form: "Did «TICKER»
release statements within its «documents» negligently containing a misrepresentation (by
omitting material facts) that «…», in breach of (i) common law; and (ii) «statute»?" Add oppression,
s. 130 primary-market claims and foreign state statutes where the facts support them.

**C. Class Period and class definitions.** One definition per cause of action (the statutory class
and the common-law class differ). Use his wording: "All «persons» that purchased «TICKER»'s «security»
between «date» and the close of «date», and held all or some of those «securities» after the close of
«date»." Note any exclusions (Excluded Persons; US-exchange purchasers covered by a US class).

## THE MISREPRESENTATION(S)

For each named misrepresentation theme (e.g. "Fully Funded", "Commercial production in Q3 2024",
"The dividend"):
1. The impugned statements (cite the statement records).
2. What existed at the time and was omitted or contradicted (cite knowledge and external records,
   with dates).
3. The link to the correction.
4. **Submission** (his voice, labelled as a draft for his review): "It is my submission that …"
5. The defences he expects on this theme (forward-looking safe harbour, s. 138.4(6) reasonable
   investigation, materiality, business judgment) and the reply.

Close with the **linkage matrix**:

| Impugned document (date) | Misrepresentation theme | Omitted / contradicting fact (date, record) | Correction (date) |
|---|---|---|---|

Then the **constituent elements** for each cause of action, verbatim from `legal-library.md`, with
their citations. Only the elements for the forum and the causes of action actually pleaded.

## PARALLEL AND COMPETING PROCEEDINGS

A table with one row per proceeding: court, docket, filed, counsel, class period, causes of action,
corrective dates, status (MTD / leave / certification / settlement), confidential witnesses.
Note what can be used (CW allegations, MTD findings on loss causation) and where proceedings
overlap or compete (carriage, the first-to-file rule, a foreign class absorbing the float).
"None found" requires search records [E…].

## BEAR v. BULL SUBMISSIONS

- **Bear:** the strongest case against. Adverse precedent on the same theory (name, citation,
  holding), the defences, causation breaks, jurisdiction and standing attacks, crowded carriage,
  firm capacity.
- **Bull:** why this case is distinguishable, point by point against each bear item.
- What evidence would move the assessment either way, with the source that would supply it.

## CONCLUSIONS

- **Recommendation** (one of four) and the three to five records it rests on.
- Damages: «statutory range; common-law range; method and inputs» [E… from economics records].
- Liability limit: «5% × market cap = value» [E…].
- Collectability: D&O insurance, cash, other assets.
- Strategy: pre-issue offer, issue and hold, serve the leave motion with the claim, venue.
- Limitations: «s. 138.14 expiry; common-law expiry; tolling step and date».
- Next steps, each with an owner placeholder and a date.
- Pipeline fields: CUSIP / ISIN / stage («Investigation and Pre-Filing») / next step / deadline.

```
Sincerely,

Andrew Morganti
```

## Appendices

- **A. Defined Terms** (alphabetical).
- **B. Sources**: each [E###] with title, publisher, type, date, locator and link.
- **C. Coverage and open questions**: the sources searched and date ranges covered, quarters
  checked, and gaps, each with the source that would settle it.
