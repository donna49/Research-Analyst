# Memo annex — Global Atomic Corporation (TSX: GLO)

Internal companion to `memo.md` (Form B, IRAC). Nothing here goes in the memo.
Run folder: `runs/2025-01-24/GLO/`; ledger 227 records; memo footnote trace in `memo_trace.json`.
The earlier blended-layout memo is kept as `memo_v1_blended.md`.

## Form
- **Form B (IRAC)**, README selection order rule 4: governing case type 3 (conditional government
  financing). Framing record E227.
- Ambiguity: the issue record (E036) also lists case type 2 (mining project). Read literally, rule 3
  (type 2 → Form C, Ascot variant) comes before rule 4. Form B was chosen because the theory is the
  omission of the loan's status, delays and pre-conditions, not a construction or ramp-up promise, and
  corpus.md lists the Global Atomic memos as IRAC. Switch to Form C if Andrew prefers.
- Model read for voice: Li-Cycle (June 4, 2026). Andrew's own Global Atomic memos were not opened.

## Decision record
- **Pursue: issue the claim and serve the s. 138.8 leave motion before November 10, 2026** (E212).
- Rests on: E008/E009 (abnormal −31.3%, t −10.2); E169 (serial date drift); E076/E075/E134 (DFC 2024
  board records show no Dasa item); E071/E095/E172 (pause "before and after" the election vs.
  October 29 and November 12, 2024 statements); E124/E221 (primary-market class).
- Would change if: the bank's records show the dates came from the bank and stayed live; the
  February 19, 2026 Ontario action belongs to another firm and leave has been served (carriage); D&O
  insurance is nominal; the September 2026 DFC approval and price recovery are argued to break loss
  causation (E212 `would_change_if`).

## Deadlines and next catalyst
| Item | Date | Ledger |
|---|---|---|
| s. 138.14 (three years from November 10, 2023) | **2026-11-10** (22 days from 2026-10-19) | E222, E193 |
| Common law (proxy: two years from the 2025-01-23 release) | 2027-01-23 (96 days) | E222, E224 |
| s. 130 (October 2024 prospectus): 180 days from knowledge / 3 years from transaction | confirm | E212 |
| Next catalyst | Service of leave motion; DFC Facility closing conditions (late 2026) | E212 |

## Economics refresh (2026-10-19)
`economics_input.json` now dates both corrections on the release day with `after_close: true`
(2024-07-16 and 2025-01-23) and adds the October 16, 2024 offering (33,542,050 units at C$1.20, E124).
The previous output is kept as `economics_v1.json`. New records E214–E226 supersede stale ones:

| Figure | Value | New | Supersedes |
|---|---|---|---|
| Storm warning 2024-07-17: close on 10th session (2024-07-30) | C$1.29 (avg C$1.438); max per share C$0.73 | E214, E225 | E175 |
| Correction 2025-01-24: close on 10th session (2025-02-06) | C$0.53 (avg C$0.597); max per share C$0.41 | E215, E225 | E176 |
| TSX Class Period volume (2023-11-10 to 2025-01-23) | 260,208,469 shares; VWAP C$1.888 | E216 | E179 |
| Per-share m1 / m2 / m3 | 0.4753 / 0.8839 / 1.291 | E217 | E182 |
| Common-law rough damages (TSX) | mid C$92.0M; range C$30.9M–C$115.0M | E218 | E184 |
| Settlement target | C$10.2M–C$18.4M | E219 | E185 |
| Statutory capped (5% cap) | C$20.4M (market cap C$407.3M) | E220, E190 | E191 |
| Primary market (s. 130) | C$20.2M (C$0.603 × 33,542,050) | E221 | E198 (gap) |
| OTC:GLATF (USD, not added) | 96,916,313 shares; m2 at 0.40 US$24.1M | E223 | E186 |
| Limitations | 2026-11-10 / 2027-01-23 | E222 | E192 |
| Volume-window gap | resolved: window now runs to the final correction | E226 | E195 |

Scenario B (`economics_B.json`, final correction only) remains a sensitivity: C$35.7M mid (E187).
The s. 130 figure uses the ten-day look-back **average** (the script's method), not the 10th-session
close; on the 10th-session close it would be larger.

## Sources by ledger id (as used in the memo)
- Company news releases: E028–E031 (2025-01-23/24), E037–E040 (2023-11-10), E041/E122 (2023-12-19),
  E042 (2024-01-10), E043/E044 (2024-03-05), E049 (2024-05-13), E051–E053 (2024-06-17), E054/E055
  (2024-07-16), E056/E057 (2024-08-12), E059 (2024-10-03), E112/E121 (2024-10-07), E060 (2024-10-29),
  E061–E063/E117/E123/E124 (2024-11-12), E065/E066 (2024-12-17), E070 (2025-02-12), E071 (2025-03-27),
  E072/E097 (2025-08-12), E073 (2025-12-11), E128 (2026-02-25), E074 (2026-09-16), E079 (2023-10-10).
- MD&A: E046–E048 (2023 MD&A), E050 (Q1 2024), E058 (Q2 2024), E064 (Q3 2024), E114 (Q2 2023).
- AIF 2024: E103, E104, E106, E108, E109; identifiers E105; ESIA notice E078, E107.
- Presentation: E067. SEDI: E085–E092. News: E045, E081, E082, E125, E129.
- DFC records: E075, E076, E077, E134.
- Market and economics: E008, E009, E011, E017, E102, E137–E167, E181, E190, E214–E225.
- Legal: E200, E201, E203–E208.
- Framing: E209 (Class Period), E210 (s. 130 class), E211 (defendants), E212 (decision), E227 (form).

## Coverage and gaps
- Q3 2023 MD&A not retrieved (E068); the news release carries the financing passage.
- October 2024 prospectus supplement and its incorporated documents not retrieved; SEDAR+ blocked
  automated access (E126, E127). Needed to confirm which releases are incorporated by reference.
- No earnings-call transcripts (E069).
- State Department s. 7008 determination not retrieved (E080).
- FOIA not yet made (E083): DFC credit/investment committee calendars and the Dasa (SOMIDA) file;
  DFC board resolutions; State guidance; EDC access-to-information request.
- US docket (RECAP) search incomplete (E132, E133).
- D&O insurance not disclosed (E119); management circulars not read.
- Auditor change PwC → EY in 2023, reason unknown (E100, E101).
- No resource or reserve figures, capex or feasibility economics for Dasa are in the ledger; the Form B
  Overview would normally carry them. Only the US$295M / 60% facility (E060) and the 2026 total
  project cost of US$698M (E077) are recorded.
- Share count for the s. 249 cap is the nearest reported figure (2023-08-10), not the 10-day average
  (E114, E190).
- "Record volume": no record-volume check was run, so the memo states the 30-day multiple instead.

## Open questions
1. Is the February 19, 2026 Ontario action (E128) the firm's own? The January 29, 2026 investor alert
   came from Berger Montague (Canada) PC (E129). If it is the firm's own action, serve the leave motion
   in it before November 10, 2026. If not, consider carriage or co-counsel.
2. Who certified the MD&A (NI 52-109 certificates)? The memo's closing sentence names Roman and Lehari
   (E108, E109, E211). The certificates themselves are not in the ledger.
3. Should the Class Period start on November 10, 2023 or March 27, 2024 (E209)?
4. Should directors (E110) and Red Cloud (s. 130 only) be named? E211 proposes both. The Form B
   closing sentence names only the issuer and officers.

## Pipeline fields
- Issuer: Global Atomic Corporation; OBCA; Toronto; TSX: GLO, OTCQX: GLATF, FRA: G12.
- ISIN CA37957M1068; CUSIP 37957M106 (E105).
- Stage: memo (Form B) complete; Drive upload pending the user's folder choice.
- Next step: leave motion and claim before 2026-11-10.

## Google Doc
Not uploaded. The user asked for no Drive upload in this run.
