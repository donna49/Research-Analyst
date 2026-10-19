---
name: external-evidence
description: Stage 7 of a research-analyst investigation. Gathers evidence from outside the company's own disclosures (court dockets and documents, regulator actions, independent reporting, short-seller research, existing shareholder suits) and records how each describes the issue compared with the company. Use after the issue is defined, or when asked what courts, regulators or third parties say about a company's problem.
---

# External evidence (stage 7)

Company filings may describe an issue very differently from the court or regulator examining it.
This stage puts the outside descriptions next to the company's.

## Courts

- **US**: CourtListener. Search dockets (`type=d`) by party name; RECAP documents (`type=r`/`rd`)
  for the matter; opinions (`type=o`). For each relevant case record: court, docket number, filing
  date, nature of suit, parties, key entries with dates, and the text of rulings or complaints
  (read with `read_document` / `search_document`). Documents not in RECAP are listed as gaps with
  the docket entry number.
- **Existing shareholder suits**: nature of suit 850 with the company as defendant, plus
  plaintiff-firm announcements (Bigdata.com news, "class action <Company>"). Record class period,
  filing date, court, lead allegations (as `attributed`). An existing suit never stops the work.
- **Canada / UK / Germany**: Bigdata.com news; UK Find Case Law; openJur; Bundesanzeiger KapMuG
  register; court websites.

## Regulators

SEC litigation releases and administrative proceedings; DOJ press releases; Federal Register; sector
regulators relevant to the issue (e.g. FDA, FAA, environmental, mining ministries); provincial
securities commissions; FCA; BaFin. Record the action, date, and how the regulator describes the
facts.

## Registries, agencies and other outside proof (Andrew's strongest evidence)

- **Lien and security registries:** builders' liens (provincial land and personal-property
  registries), with lien numbers, dates and amounts (Ascot).
- **Insolvency:** CCAA or bankruptcy dockets, monitor reports, sworn affidavits (Wayland, Canacol,
  Chesswood).
- **Lenders and agencies:** board agendas, minutes, approval process timelines of the lender or
  agency named by the company (DFC, EDC, DOE). Use these to check promised approval dates (Global
  Atomic).
- **FOIA / access to information:** list the requests worth making (topic, agency, what it would
  prove) as `gap` records. Andrew flags "FOIA Request topic" in footnotes. Journalists' FOIA results
  count as attributed reporting (Terravest / AMF records).
- **Government and official bulletins:** incident, environmental and safety bulletins (Alamos fire
  bulletins); sanctions and aid restrictions (Global Atomic, Section 7008).
- **Counterparties and peers:** the counterparty's own statements; peers' disclosures of the same
  regulatory or market event.
- **Foreign-language press** where the operations are abroad (Canacol / El Colombiano). Record the
  original and the translation.

## Independent reporting and short sellers

Bigdata.com news (premium and public). For each report: outlet, date, whether it rests on documents,
named sources, or anonymous sources, and which statements of the company it contradicts or
supports. Short-seller reports: record each allegation separately as `attributed`, with the
evidence the report cites, and look for the company's response.

## Parallel and competing proceedings

Feed `claim-framing`: for each proceeding, write a `proceeding` record with forum, docket, filed date,
counsel, class period, corrective dates, status, and confidential witnesses relied on. A US complaint
is a roadmap: record its misrepresentation and corrective-date paragraphs as `attributed`.

## Comparison

For each external item add, where relevant, a `comparison` or `knowledge` record linking it to the
company statements (stage 5) it bears on. Note where the outside description and the company's
description of the same fact differ, quoting both.
