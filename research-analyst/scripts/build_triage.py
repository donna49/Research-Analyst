#!/usr/bin/env python3
"""Render runs/<date>/triage.md from market_event.json and the per-name triage/<TICKER>.json files.

  build_triage.py runs/<date>

Numbers come only from market_event.json; trigger findings only from triage/*.json. Names with no
triage file are listed as not yet scanned, never dropped.
"""
import glob, json, os, sys
from collections import Counter

ORDER = ["Full investigation", "Watch", "Exclude"]
EXCLUDE_CODES = {
    "Not company-specific": ("X-MARKET", "Market, peer or theme move explains most of the fall"),
    "Insufficient data": ("X-DATA", "No usable price data"),
}


def pct(x):
    return "n/a" if x is None else f"{x:+.1%}"


def money(x, ccy):
    if x is None:
        return "n/a"
    return f"{x / 1e9:.2f}B {ccy}" if abs(x) >= 1e9 else f"{x / 1e6:.0f}M {ccy}"


def cell(s):
    return (s or "").replace("|", "/").replace("\n", " ")


def norm_disposition(d):
    d = (d or "").lower()
    if d.startswith("full"):
        return "Full investigation"
    if d.startswith("watch"):
        return "Watch"
    if d.startswith("exclu"):
        return "Exclude"
    return None


def main(run):
    me = json.load(open(os.path.join(run, "market_event.json")))
    tri = {}
    for f in glob.glob(os.path.join(run, "triage", "*.json")):
        d = json.load(open(f))
        tri[d["symbol"]] = d
    rows = {k: [] for k in ORDER + ["Not yet scanned"]}
    for r in me:
        sym = r["symbol"]
        if "error" in r:
            rows["Exclude"].append((r, None, "X-DATA", f"No trade or price data on day 0 ({r['error']})"))
            continue
        t = tri.get(sym)
        if t:
            ov = t.get("reviewer_override") or {}
            disp = norm_disposition(ov.get("disposition") or t.get("disposition")) or "Watch"
            reason = t.get("disposition_reason")
            if ov:
                reason = f"Reviewer override ({ov.get('code', '')}): {ov.get('reason')} [researcher: {t.get('disposition')}]"
            rows[disp].append((r, t, ov.get("code"), reason))
        elif r["class"] in EXCLUDE_CODES:
            code, why = EXCLUDE_CODES[r["class"]]
            if any("thin trading" in f or "OTC" in f for f in r["flags"]):
                code, why = "X-THIN", "Thin or OTC trading; price signal unreliable"
            rows["Exclude"].append((r, None, code, why))
        else:
            rows["Not yet scanned"].append((r, None, None, f"{r['class']}; trigger scan not run yet"))

    day = me[0].get("day0") or os.path.basename(run)
    countries = Counter((r.get("country") or "n/a") for r in me if "error" not in r)
    out = [f"# Triage: screener of {day} ({len(me)} names)", "",
           "Research triage only; not legal advice. Dispositions follow `skills/triage/SKILL.md`.", "",
           "Company domicile: " + ", ".join(f"{c} {n}" for c, n in countries.most_common()), "",
           "| Disposition | Count |", "|---|---|"]
    out += [f"| {k} | {len(v)} |" for k, v in rows.items() if v]
    out.append("")

    for k in ["Full investigation", "Watch"]:
        if not rows[k]:
            continue
        out += [f"## {k} ({len(rows[k])})", "",
                "| Company | Ticker | Return | Abnormal (t) | Value lost | Likely trigger | Tier | Prior statements | Litigation and investigation notices |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r, t, _, _ in rows[k]:
            src = (t.get("trigger_source") or {})
            trig = cell(t.get("likely_trigger"))
            if src.get("url"):
                trig = f"[{trig}]({src['url']})"
            ps = (t.get("prior_statement_check") or {}).get("outcome", "not run")
            n_lit = len((t.get("existing_litigation") or {}).get("items") or [])
            lit = f"{n_lit} item{'s' if n_lit != 1 else ''} (see notes)" if n_lit else "none found"
            tt = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.1f}"
            out.append(f"| {cell(r['name'])} | {r['symbol']} | {pct(r['return'])} | {pct(r['abnormal_return'])} ({tt}) | "
                       f"{money(r['market_cap_lost'], r.get('market_cap_currency') or r['currency'])} | {trig} | {t.get('tier')} | {ps} | {lit} |")
        out.append("")
        for r, t, _, reason in rows[k]:
            out.append(f"**{r['symbol']} {cell(r['name'])}.** {cell(t.get('likely_trigger'))}")
            if t.get("trigger_public_at"):
                out[-1] += f" Public: {t['trigger_public_at']}."
            if t.get("trigger_quote"):
                out.append(f"> {cell(t['trigger_quote'])}")
            ps = t.get("prior_statement_check") or {}
            if ps.get("quote"):
                s = ps.get("source") or {}
                out.append(f"Prior statement ({ps.get('outcome')}; {cell(s.get('title'))}, {s.get('date')}): \"{cell(ps['quote'])}\"")
            for it in (t.get("existing_litigation") or {}).get("items", []):
                out.append(f"Existing litigation: {cell(it.get('description'))} ({it.get('court') or ''} {it.get('date') or ''}) {it.get('url') or ''}")
            out.append(f"Why: {cell(reason)}")
            if r["flags"]:
                out.append(f"Data flags: {'; '.join(r['flags'])}")
            if t.get("notes"):
                out.append(f"Notes: {cell(t['notes'])}")
            out.append("")

    if rows["Not yet scanned"]:
        out += [f"## Not yet scanned ({len(rows['Not yet scanned'])})", "",
                "| Company | Ticker | Return | Abnormal (t) | Class |", "|---|---|---|---|---|"]
        for r, _, _, _ in rows["Not yet scanned"]:
            tt = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.1f}"
            out.append(f"| {cell(r['name'])} | {r['symbol']} | {pct(r['return'])} | {pct(r['abnormal_return'])} ({tt}) | {r['class']} |")
        out.append("")

    out += [f"## Excluded ({len(rows['Exclude'])})", "",
            "| Company | Ticker | Return | Market | Peers | Theme | Abnormal (t) | Code | Reason |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r, t, code, reason in rows["Exclude"]:
        if "error" in r:
            out.append(f"| | {r['symbol']} | | | | | | {code} | {cell(reason)} |")
            continue
        tt = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.1f}"
        theme = f"{r['theme_etf']} {pct(r['theme_return'])}" if r.get("theme_etf") else "none"
        out.append(f"| {cell(r['name'])} | {r['symbol']} | {pct(r['return'])} | {pct(r['market_return'])} | "
                   f"{pct(r['peer_return'])} | {theme} | {pct(r['abnormal_return'])} ({tt}) | {code or 'X-TRIGGER'} | {cell(reason)} |")
    out += ["", "## Coverage", "",
            "Prices: TradingView chart feed and scanner (`market_event.json`). Trigger, prior-statement and "
            "litigation checks: Bigdata.com, SEC EDGAR, CourtListener; every search is listed in `triage/*.json` "
            "and `triage/ledger_*.jsonl`."]
    open(os.path.join(run, "triage.md"), "w").write("\n".join(out) + "\n")
    print(f"wrote {os.path.join(run, 'triage.md')}: " + ", ".join(f"{k} {len(v)}" for k, v in rows.items()))


if __name__ == "__main__":
    main(sys.argv[1])
