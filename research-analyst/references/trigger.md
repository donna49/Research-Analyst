# Andrew's triggering event (stated by Andrew, 2026-10-19; his flow chart of 2026-08-15 in `andrew-flowchart.md`)

A security is a candidate when **all** of the following hold:

1. **A single-day drop of more than 10%.** Measured close to close, on the session that reacted.
2. **A market capitalization over $200 million.** Measured before the drop: the close of the prior
   session × shares outstanding. The figure comes from `market_event.py` (`market_cap`, rebased to day 0).
3. **One of two venue tests:**
   - (a) the security trades on the **TSX, TSXV, CSE, Cboe Canada, Nasdaq Canada or another Canadian
     electronic market**; or
   - (b) the company is **Canadian-registered and files on SEDAR+**, and the security that dropped trades
     on **Nasdaq, NYSE or US OTC**.

   For (b), check the SEDAR+ profile (or the 40-F / 10-K cover, the AIF and the incorporating statute). Some
   Canadian companies whose securities trade only in the US have no SEDAR+ entry. Record that, and test the
   Canadian registration from the incorporation records (OpenCorporates, the provincial registry, the
   10-K/20-F cover).

The abnormal-return drop standard (`drop-standard.md`) still runs on every candidate. It answers "was it
the market?" and feeds triage. It does not change whether the trigger is met.

The flow chart sets the market-cap threshold at $250M; his October 19 message says $200M. The plugin uses
$200M and flags names between $200M and $250M as "below the flow-chart threshold".

## Other triggers (no price drop needed)

These come from his flow chart. Each starts a first review in the same way:
- **Regulator notices of a new investigation or enforcement action:** SEC, OSC, AMF (Quebec), BCSC,
  CFTC, UK FCA, ASIC.
- **Company disclosures** from his daily Google alerts. For a non-Canadian company, check SEDAR
  reporting.
- **Verteris.com** alerts (his subscription).
- **New filings in the CBA Class Action database.** This also serves as the "already filed?" check.

## Scope note

Under this trigger, the triage universe is **Canadian issuers**: Canadian listings plus Canadian-registered
companies listed in the US. His flow chart does not track UK or German markets, so **UK- and German-listed drops are out of the
daily screen**. The UK and German material stays in the plugin for three uses: competing or parallel
proceedings (BP's FSMA s. 90A, Volkswagen's KapMuG, Australia's class actions); UK RNS announcements of
SEDAR-reporting issuers (Investegate); and FCA notices as triggers.

## In triage

Triage step 0 applies the trigger to every screener row and records `trigger_met`
(`yes` / `no: reason` / `unclear: what to check`). Names failing the trigger go to a separate
"Outside the trigger" table with the reason. They are never silently dropped.
