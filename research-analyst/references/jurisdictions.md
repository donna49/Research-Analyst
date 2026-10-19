# Jurisdiction: forum checklist

The research method does not change with the country. What changes is the **legal module**: the
forum, the statute, the cap, the leave hurdle and the limitation periods. Andrew assesses every
issuer from the forums available to the firm, in this order:
1. Canada.
2. The US, through the firm's US colleagues or a parallel action.
3. The issuer's home forum, mainly as a competing or parallel proceeding.

Record facts. The memo states his submissions as drafts; the lawyer decides.

## Step 1: facts to record for every issuer

- Statute of incorporation and jurisdiction. Head office.
- Every listing with its ticker, plus CUSIP and ISIN. Note CDRs or ADRs: the depositary, the ratio,
  and whether they are sponsored.
- Reporting-issuer status by province (SEDAR+ profile; OSC Form 13-502F1). Any US registration
  (10-K, 20-F or 40-F filer).
- Canadian footprint: subsidiaries, offices, employees, customers, Canadian institutional holders
  (13F/fund holdings), offerings sold in Canada, and prospectus language on Canadian remedies.
- Volume by trading venue over the Class Period (`economics.py`).

## Step 2: the Canadian forum

| Situation | Hook | Notes |
|---|---|---|
| Listed on TSX, TSXV, CSE or Cboe Canada | Reporting issuer → OSA Part XXIII.1 (and the equivalent statute in each province where it reports) | Ontario is the default forum. The statutory claim is certified on a global basis; the common-law claim is limited to Canadians if contested |
| Not listed in Canada, but with Canadian operations or holders | Responsible issuer through a real and substantial connection (*Van Breda*; *Canadian Solar*) | Forum non conveniens risk (Li-Cycle dropped its OSA claims to settle the forum dispute) |
| CDRs on Cboe Canada | The CDR class plus Canadian residents who bought US shares (FiServ) | Standing as tenants-in-common; quantifiable link through the CDR ratio |
| Quebec issuer or Quebec class members | QSA s. 225.2ff; authorization | First-to-file rule in Quebec |
| Alberta or BC issuer | Provincial Securities Act; Alberta allows holders' claims | BC CPA covers BC residents only |

Also check:
- Which provinces the issuer reports in. Canacol, for example, reported in Alberta, BC and Ontario,
  but not Quebec.
- The carriage landscape: other Canadian claims already filed (Ontario's 60-day rule; Quebec
  first-to-file).
- The incorporating statute for oppression (OBCA, ABCA, BCBCA, CBCA s. 241) and for derivative claims.

## Step 3: the US forum (parallel or referral)

- Is there a US class action? Record the docket, court, class period, counsel, confidential
  witnesses, motion-to-dismiss status and settlement (CourtListener NOS 850; plaintiff-firm notices).
- If the issuer is US-listed, US purchasers fall under §10(b)/§11 (*Morrison* limits this to
  US-exchange or domestic transactions). Canadian proceedings carve out US-exchange purchasers
  already covered by the US class unless there is a reason not to (*Paniccia v. MDC*).
- Strategy Andrew has used: issue the Canadian claim and hold it until the US mediation (FiServ).

## Step 4: the home forum (UK, Germany, Australia, other)

- UK (LSE Main Market / AIM): FSMA s. 90A / Schedule 10A for published information; s. 90 for
  prospectuses. Record RNS timing: when the inside information arose and when it was announced.
- Germany (Xetra / Frankfurt regulated market): WpHG §§ 97–98 for ad hoc disclosure failures; the
  KapMuG model-case register. Record when the underlying event occurred, when the ad hoc
  announcement was published, and any self-exemption delay disclosed later.
- Australia: competing class actions can absorb most of the float (Paladin).
- For each, record whether a proceeding exists or is announced, and what share of Class Period
  volume trades on that venue. Andrew's decision turns on the residual Canadian class.

## Documents to collect, by listing

| Listing | Core documents | Timing question |
|---|---|---|
| US | 10-K, 10-Q, 8-K and exhibits, proxy, S-1/S-3, earnings calls | Minute-level time of each statement and correction |
| Canada | AIF, MD&A, financial statements, material change reports, news releases, circular, prospectus and offering memorandum, NI 43-101 reports, earnings calls | When a material change occurred vs when it was reported (NP 51-201; missing material change reports) |
| UK | Annual and half-year reports, RNS, prospectuses | When inside information arose vs when it was announced |
| Germany | Annual and half-year reports, ad hoc and corporate news, quarterly statements | Event date vs ad hoc publication; self-exemption delays |

For any company with a US listing or ADR, collect the US documents too, whatever its home country.
For a company quoted only on US OTC but listed at home, the home-market price is the meaningful one.
