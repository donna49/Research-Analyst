---
name: triage-method
description: Layer 1 of the research-analyst workflow. Takes one day's screener output of stocks that fell 10%+ and sorts every name into Full investigation, Watch or Exclude with a checkable reason, using the drop standard, the trigger scan, a quick prior-statement check and an existing-litigation check. Use when given screener output or asked which of today's drops are worth investigating.
---

# Triage (Layer 1)

Goal: for every screened stock, a disposition Andrew can check in one glance, without doing Layer 2
work. Nothing is silently dropped: excluded names stay in the output with their reason.

Adapted from financial-services `deal-screening` (pass/fail against fixed criteria) and the
Bigdata.com `company-brief` sweep (mandatory litigation query, category sweep).

## Steps

### 0a. The screen (when no screener output is given)

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/screener.py"
```

This is Andrew's step one: every fall of more than 10% in the **last trading session that closed before
today** (a Monday run screens Friday; holidays are read from each market's own bars). It writes to
`runs/<session date>/`. It uses the TradingView scanner, and keeps a fall
only if it meets his trigger (`references/trigger.md`): a TSX, TSXV, CSE or Cboe Canada listing, or a
Canadian company whose security fell on NYSE, Nasdaq or US OTC, and a market cap over C$200M (USD
converted at the day's rate). Everything else goes to `screener_outside.md` with its reason. Its flags carry
into triage:
- **likely a stale secondary quote:** the primary listing barely moved. Usually an unsponsored ADR or a
  thin Cboe Canada line. Send to Exclude as `X-MECH` unless the primary listing's own move is confirmed.
- **verify Canadian registration and SEDAR+ reporting:** venue test (b). Settle it at step 0b.
- **cap between C$200M and C$250M:** below his flow-chart threshold. Keep it, and note this in the row.

Market cap is taken at the close before the drop. Sub-cent and near-total-move quotes go to the outside
list as unreliable.


### 1. Measure every drop (script, all names at once)

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/market_event.py" --screener runs/<date>/screener.md --date <date> \
  --json runs/<date>/market_event.json > runs/<date>/market_event.md
```

Read `market_event.json`. Do not recompute anything. Apply the overrides in
`references/drop-standard.md` only after you know the trigger (step 3).

### 2. Pre-exclude without searching

A name goes straight to **Exclude** (no searches spent) when the script shows any of:

| Code | Rule |
|---|---|
| `X-MARKET` | Class "Not company-specific": the market, peer or theme move (e.g. bitcoin for miners) explains the fall |
| `X-MECH` | Dividend effect explains most of the fall, or another mechanical cause |
| `X-THIN` | OTC or thin trading with no measurable volume history: price signal unreliable. Exception: send to Watch if the company is also listed on a home exchange where the fall is confirmed |

Everything else continues. When in doubt, continue: a wrong exclusion is worse than a wasted search.

### 3. Trigger scan (per remaining name)

Window: from two sessions before day 0 to the day 0 close (exchange time zone). Budget: 3–5 searches.

1. Bigdata.com news, fast mode, entity filter, timestamp = window:
   "what happened to <Company> stock", then "<Company> announcement".
2. Company announcements in the window.
   US: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/edgar.py" filings <TICKER> --from <d-2> --to <d+1>` (acceptance times from
   the EDGAR index pages, with before-open / after-close flags); Canada/UK/Germany via the sources
   in `references/source-hierarchy.md`. An 8-K's acceptance time is when EDGAR published it; the
   press release inside may have reached the market earlier on a newswire. Record both times.
3. Litigation and regulators, one search: "<Company> lawsuit OR investigation OR subpoena OR
   class action" in the window and the prior 90 days.

Record each search as a `search` record in `runs/<date>/triage_ledger.jsonl`, and each candidate
trigger as a `revelation` record with `public_at` and source.

Rank the likely trigger with the competing-hypotheses discipline from intel `intel-diagnose`: list
every candidate explanation (company news, sector or group move, market, mechanical, unexplained);
for each, what evidence supports and what undercuts it; pick the one the evidence best fits and say
how confident.

Assign a tier from `references/trigger-tiers.md`.

### 4. Quick prior-statement check (only for Tier A or B triggers)

One or two searches over the past 2 years of the company's own filings and calls on the trigger's
subject (Bigdata.com fast mode, entity filter, categories filings + transcripts; for US also
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/edgar.py" fts "<phrase>" <TICKER> --from <d-2y> --to <d>`). Outcome, with the passage quoted:

| Outcome | Meaning |
|---|---|
| `reassured` | Company addressed the subject and played it down |
| `silent` | Company never addressed the subject |
| `warned specifically` | Company described the specific risk concretely, before the drop |
| `unclear` | Not enough found to say |

### 5. Existing litigation (always, never excludes)

US: CourtListener dockets, nature of suit 850, party name = company, filed in the last 3 years.
All countries: Bigdata.com news for "class action" or "securities lawsuit" with the company in the
last 12 months, plus plaintiff-firm "investigation" announcements after day 0.

### 0b. Andrew's trigger (applied to every row before step 2)

Apply `references/trigger.md` to every screener row: a drop of more than 10%, a market cap over $200M,
and either a Canadian listing or a Canadian-registered SEDAR+ filer listed in the US. Record
`trigger_met` in the name's JSON. Names that fail go to the "Outside the trigger" table with the
reason. Only names that meet the trigger can be Full investigation. For names that fail, add
`unclear: <what to check>` where the Canadian registration cannot be settled quickly.

### 6. Disposition

| Drop class | Trigger tier | Prior-statement check | Disposition |
|---|---|---|---|
| Company-specific | A | any | **Full investigation** |
| Company-specific | B | reassured / silent | **Full investigation** |
| Company-specific | B | warned specifically / unclear | Watch |
| Borderline (incl. short history) | A | any | **Full investigation** |
| Borderline | B | any | Watch |
| any | Unexplained | — | Watch (re-scan in 5 sessions) |
| any | C | — | Exclude `X-TIERC` |
| Not company-specific | — | — | Exclude (code from step 2) |

A plaintiff-firm "investigation" announcement or a filed suit never lowers a disposition; it is
reported, and for Watch names it is a reason to look again.

### 6b. Andrew's forum and size note (Full investigation and Watch names only; never excludes)

For each name, add a one-line note to the name's JSON (`forum_size_note`) so the list can be ranked
the way Andrew would rank it (`references/andrew-method.md` §4):
- **Forum:** Canadian listing (TSX, TSXV, CSE, Cboe Canada) / US listing with a Canadian footprint or
  CDRs / other. Canadian-listed names come first; a foreign issuer needs a Canadian hook.
- **Size:** market value lost from the drop standard (`market_cap_lost`). Flag "small" below about
  25M in local currency. Andrew passed on cases with a recoverable class of about $5M or less.
- **Parallel action:** a US suit already filed is a reason to rank a Canadian-listed or CDR name
  *higher* (issue and hold), not lower.

The note orders the Full-investigation list. It never moves a name between dispositions.

### 7. Reviewer pass

Read every disposition against the evidence before rendering. Where the evidence or a rule (e.g.
step 2 thin-trading) calls for a different result, add `reviewer_override`
(`disposition`, `code`, `reason`) to the name's `triage/<TICKER>.json`; never edit the researcher's
own fields. Timing checks that commonly change the picture:
- a disclosure made before the open on day −1 (the reaction may span two sessions);
- a filing accepted after the day-0 close belongs to day +1 (use `edgar.py filings`, which reads the
  index-page ET time; never convert the submissions-JSON `acceptanceDateTime`, which is mislabelled UTC);
- plaintiff-firm "investigation" notices are signals, not filed suits.

Render with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_triage.py" runs/<date>`.

## Output: `runs/<date>/triage.md`

```markdown
# Triage: <date> screener (<n> names: US <a>, Canada <b>, UK <c>, Germany <d>)

Data: prices TradingView chart feed; news and filings Bigdata.com, SEC EDGAR, CourtListener …
Searched: <n> searches, window <from> to <to>.

## Full investigation (<k>)
| Company | Ticker | Country | Drop | Abnormal (t) | Market value lost | Likely trigger | Tier | Prior statements | Existing suit | Forum / size |
|---|---|---|---|---|---|---|---|---|---|---|
One line per name; the trigger cell links its source; a short paragraph below the table per name
(3–5 sentences: what happened, when, from whom, the quoted prior statement, why it was kept).

## Watch (<k>)
Same table + "What would move it up".

## Excluded (<k>)
| Company | Ticker | Drop | Abnormal (t) | Reason code | Reason |
```

Close with the coverage line (sources searched, windows) and the list of names whose data failed,
if any. Never fill a failed name from memory.
