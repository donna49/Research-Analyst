# Sources and source hierarchy

Fixed source list for this plugin (decided 2026-10-19). Use only these; anything else is open-web
discovery under the rules at the bottom.

## Tiers (from InvestSkill fact-check, extended)

| Tier | What | Can support |
|---|---|---|
| 1 | Issuer filings and announcements; court documents; regulator releases; transcripts of the company's own calls; script outputs | Facts and exact quotes |
| 2 | Reputable reporting that quotes or links a primary document; data vendors | A fact only if no primary is retrievable; marked "secondary" |
| 3 | Aggregators, blogs, unattributed summaries, model memory | Discovery only; never cited as support |

An outlet republishing a company press release is the same evidence family as the release; count
origins, not URLs (intel evidence standards).

## Sources by need and country

| Need | US | Canada | UK | Germany |
|---|---|---|---|---|
| Entity, listings, ISIN, SEC CIK | Bigdata.com `find_securities`; tearsheet (CIK) | same | same | same |
| Prices, volume, market cap | `scripts/market_event.py` (TradingView chart feed + scanner) | same | same | same |
| Annual / interim reports, MD&A | SEC EDGAR (10-K, 10-Q, 20-F, 40-F, 6-K) | Bigdata.com; issuer IR site; SEDAR+ (web, manual) | Bigdata.com; issuer IR site; FCA NSM (web) | Bigdata.com; issuer IR site; Unternehmensregister (web) |
| Search inside past filings | EDGAR full-text search (`efts.sec.gov`) | Bigdata.com search | Bigdata.com search | Bigdata.com search |
| Company announcements | EDGAR 8-K and exhibits | Bigdata.com news; Newsfile | Investegate (RNS archive); LSE news | EQS News (ad hoc and corporate news) |
| Earnings calls | Bigdata.com transcripts | same | same | same |
| News around the drop | Bigdata.com news | same | same | same |
| Insider dealings | EDGAR Form 4 | SEDI (web) | RNS PDMR notices | BaFin directors' dealings database |
| Courts | CourtListener (dockets, filings, opinions; securities suits = nature of suit 850) | Bigdata.com news; court websites | UK Find Case Law API | openJur; Bundesanzeiger KapMuG register |
| Regulators | SEC litigation releases and AAERs; DOJ press releases API; Federal Register | Capital Markets Tribunal / provincial commissions | FCA notices | BaFin |
| Existing shareholder suits | CourtListener NOS 850 + party name; plaintiff-firm announcements via Bigdata.com news | Bigdata.com news | Bigdata.com news | KapMuG register |

EDGAR requires a `User-Agent` with a contact email and ≤ 10 requests per second. The
`acceptanceDateTime` in the submissions JSON carries a "Z" suffix but does not match the
Eastern-time "Accepted" stamp on the filing index page; use the index page time (ET) for
`public_at`, and check it against the market session (before open / during / after close).

CourtListener allows about 5 searches per minute; run its queries one at a time and retry on
HTTP 429. A search that never completes is recorded as a failed `search`, not as "no cases".

## Canadian filings and insider data: access routes that work

Learned in the Global Atomic backtest (2026-10-19):

| Need | Route | Notes |
|---|---|---|
| SEDAR+ documents | Blocked by captcha for automated fetches | Try Bigdata.com filings, then the issuer's document host, then news wires. If a core document is still missing, record a `gap` and ask the user to download it from SEDAR+ into `sources/` |
| Issuer IR site | Often behind Cloudflare | Many Canadian issuers serve PDFs from a static host such as `s*.q4cdn.com`. Find the link through search results rather than guessing file names. Record the URL actually opened |
| SEDI insider trades | The public SEDI search form can be submitted by script (POST) | Record the issuer number and the query parameters in the `search` record |
| Earnings calls | Bigdata.com often has slides or reports, not transcripts, for small Canadian issuers | If there is no transcript, use the webcast replay page or the news coverage of the call; record a gap for the Q&A |
| Government lenders (DFC, EDC, DOE) | Board meeting notices and minutes on the agency's website | Check the agency's own agendas against every date the company promised |
| Statutes | Ontario e-Laws (`ontario.ca/laws`); CanLII may block (403) | Record the statute section used, as a `legal` record with the URL |
| CUSIP / ISIN | Bigdata.com or a data vendor is tier 2; the prospectus or AIF cover is tier 1 | Use tier 2 only if the tier 1 source cannot be reached |

## Bigdata.com query discipline (from the Bigdata.com plugin)

One entity, one topic, one period per search. Natural-language queries. Use fast mode with explicit
filters (entity id, category, document type, timestamp) when the lane is known; smart mode to
discover. Record every search as a `search` ledger record so the memo can state coverage.
Pass `plugin_slug: "research-analyst"` on tool calls that accept it.

## Open web

Allowed for discovery and for official pages (issuer IR, regulators, courts, exchanges). Every web
fact is traced to a primary source before it is cited; if it cannot be, it is labeled
"reported by [outlet]" and never stands alone. Not allowed: social media, forums, paywall
circumvention, anything requiring someone's login.

## Not used

PACER (CourtListener instead); social media readers; TradingView desktop or cookie-based tools;
Stanford SCAC (blocked; CourtListener and news cover it); Seeking Alpha, OpenInsider, WhaleWisdom
(paywalled or secondary copies); benchmark tables from other plugins.
