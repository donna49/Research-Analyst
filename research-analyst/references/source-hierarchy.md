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

EDGAR requires a `User-Agent` with a contact email and ≤ 10 requests per second.

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
