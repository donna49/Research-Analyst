# Backtest: plugin v0.2 vs Andrew's Global Atomic memo

The plugin's memo (`memo.md`, about 5,800 words, 213 ledger records) was written by an agent that
was not allowed to open Andrew's memo. It is compared here with "Memo from Morganti to FILE re
Global Atomic" (dated Jan 26, 2025, updated Jan 28, 2026).

**The run was not fully blind.**
- The plugin's own references name the Global Atomic pattern: the storm warning and correction pair,
  the DFC agenda check and the election excuse.
- Public news returned the Feb 2026 Ontario action, which gave away the Class Period.

The parts the references did not give away are therefore the better test: what the agent found in
the documents, what outside proof it located, and how good its economics were.

## Found by both

| Item | Andrew | Plugin |
|---|---|---|
| Theory | Omitted loan pre-conditions; serially missed credit committee and board dates | Same: five themes, including omitted conditions and dated approval promises |
| Drift table | 5 credit-committee dates and about 11 board dates | 11 dated promises, including a CURIOUS same-evening Q3/Q4 change |
| Storm warning | Jul 16, 2024, $2.02 → $1.67 (−17.3%) | Jul 17 session, −17.3%, abnormal −12.6% |
| Correction | Jan 23, 2025, $0.94 → $0.64 (−31.9%), record volume | Jan 24 session, −31.9%, 13.6× volume, abnormal −31.3% (t −10.2) |
| Outside proof | DFC agendas show the loan never went to the agenda until Q4 2025 | DFC board notices for 2024–25 show no Dasa item; the company's Dec 2025 release confirms the credit committee only then |
| Election excuse | "disingenuous": the election came before the Nov 12 statements | The Dec 17, 2024 explanation set against the Mar 27, 2025 admission of a pause "before and after" the election |
| Act of state (coup, s. 7008) | A complete defence unless the claim is framed on the company's own statements | Included in Bear v. Bull |
| Class Period | Nov 10, 2023 – Jan 23, 2025 | Same (but news of the filed action gave it away) |
| Decision | Pursue against GLO and the CEO | Pursue |

## Plugin went further

- **Insider sales:** CEO and CFO open-market sales on Aug 15–23, 2024, from SEDI. These came after
  the storm warning and before the correction. They were option exercises, so the plugin rated them
  low confidence. Andrew's memo has no insider section.
- **Auditor change** from PwC to EY in 2023.
- **Timing of the offering:** the Oct 3, 2024 "bank confirmed" release came one business day before
  the C$40M prospectus offering launched.
- **Post-memo facts for Bear v. Bull:** DFC approved US$414.2M on Sep 16, 2026.
- **Economics Andrew did not compute:** the 5% cap (C$20.4M on a C$407M s. 249 market cap), the volume
  split (TSX 73% / OTC 27%), damages and settlement ranges, and limitation dates.
- **Limitation warning:** s. 138.14 runs on **Nov 10, 2026**, three years from the Nov 10, 2023 MD&A.
  Check that the leave motion in the Feb 2026 action has been filed and served so the limitation
  is suspended.

## Andrew had, the plugin missed

- Peer-company context: Niger revoked the Orano and GoviEx permits (Jul 2024), followed by arbitrations.
- Proclamation 10692 (AGOA eligibility) and the US Air Force base withdrawals cited as dated events.
  The plugin mentions the troop withdrawal.
- **Primary-market claims for the Dec 2023 and Jul 2024 private placements.** The plugin covered
  only the Oct 2024 prospectus offering. This may be correct, since s. 130 needs a prospectus, but
  Andrew lists all three.
- Oppression, which Andrew flags as possible in a footnote.
- The DFC eligibility checklist and application form (DFC-001A) cited as proof that pre-conditions
  existed.
- His 10-day look-back as the close on the 10th session ($1.29 and $0.53). Fixed: the script now
  reports both measures and matches him exactly.

## Plugin defects found and fixed after the run

1. Market value lost used today's market cap. It is now rebased to the day-0 price, with a flag.
2. Backtests lost early price history. The history window now extends back to day 0.
3. `--lookback` left out the day-0 row. Fixed.
4. Releases after the close had to be shifted by hand. Now a `+` on a `--moves` date, or
   `"after_close": true` on a correction, shifts it to the next session.
5. Class Period volume stopped at the storm warning. It now runs to the final correction, split into
   segments, so shares bought after the storm warning bear only the later drops. The GLO midpoint
   went from C$148M (overstated) to C$92M.
6. The settlement floor could exceed the high end. Fixed.
7. There was no s. 130 computation. An `offerings` input was added: the Oct 2024 units give C$20.2M.
8. The limitation countdown used the system date. Added `--asof`.
9. Ledger fixes: added `proceeding_status`, a `framing` kind and the `issue` kind in the schema. Multi-cites
   (`[E001, E002]` and `[E001–E003]`) are now accepted. Library text in `legal` records no longer
   trips the banned-word check.
10. Documentation: added Canadian access routes (SEDAR+ captcha, the q4cdn host, SEDI by POST, DFC
    notices, e-Laws); checkpoint 1 now explicitly comes before stage 4; added a timeline output file;
    and analogies to prior cases are allowed by case name.

The memo and economics in this folder were produced **before** these fixes. The deal-sheet damages
in `memo.md` come from the old volume window. Re-run stage 9 to refresh them.

## Still open

- Future blind backtests must use a case whose details are not named in the references. Global
  Atomic, Ascot, Slate, Paladin and Alamos are all now in the method files.
- SEDAR+ remains closed to automation. Missing core documents need a manual download.
- Bigdata.com has no call transcripts with Q&A for this issuer.
