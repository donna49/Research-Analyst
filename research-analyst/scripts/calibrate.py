#!/usr/bin/env python3
"""Calibrate the drop-standard thresholds on labelled past cases (v2, references/drop-standard.md).

  calibrate.py cases.csv [--json out.json]

cases.csv columns: symbol (EXCH:TICKER), date (day 0, YYYY-MM-DD), label (`pursue` for drops a
memo found worth investigating, `pass` for drops reviewed and set aside), note (optional).

For each case the script runs the drop standard (same code and data as market_event.py), then
scores a grid of AR / t threshold pairs: how many `pursue` cases would reach triage (Company-
specific or Borderline) and how many `pass` cases would too. A pursued case the standard would
have excluded is the costly error, so the table is sorted by misses, then false flags, then
strictest thresholds first. It reports; it does
not change the thresholds — that is a decision for the user, recorded in drop-standard.md.
"""
import argparse, csv, datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_event as me

GRID_AR = [-0.03, -0.04, -0.05, -0.06, -0.07, -0.08, -0.10]
GRID_T = [-1.64, -1.96, -2.33, -2.58, -3.0]


def flagged(r, ar_border, t_border):
    """Would this result reach the trigger scan (Company-specific or Borderline) at these thresholds?"""
    if "error" in r or r.get("abnormal_return") is None:
        return None
    short = r.get("t_stat") is None
    return me.classify(r["abnormal_return"], r.get("t_stat") or 0, short, ar_clear=min(ar_border, me.AR_CLEAR),
                       ar_border=ar_border, t_clear=min(t_border, me.T_CLEAR), t_border=t_border) != "Not company-specific"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases")
    ap.add_argument("--json")
    a = ap.parse_args()
    cases = [c for c in csv.DictReader(open(a.cases)) if c.get("symbol")]
    bad = [c for c in cases if c.get("label") not in ("pursue", "pass")]
    if bad:
        sys.exit(f"label must be pursue or pass: {[c['symbol'] for c in bad]}")
    res = []
    for c in cases:
        try:
            r = me.analyse(c["symbol"].strip(), dt.date.fromisoformat(c["date"].strip()))
        except Exception as e:
            r = {"symbol": c["symbol"], "error": str(e)[:200]}
        res.append({**r, "label": c["label"], "note": c.get("note", "")})
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=str)
    ok = [r for r in res if "error" not in r and r.get("abnormal_return") is not None]
    n_p, n_x = sum(r["label"] == "pursue" for r in ok), sum(r["label"] == "pass" for r in ok)

    print(f"{len(cases)} cases, {len(ok)} measured ({n_p} pursue, {n_x} pass)\n")
    print("| Case | Label | Day 0 | Abnormal | t | Current class |")
    print("|---|---|---|---|---|---|")
    for r in res:
        if "error" in r or r.get("abnormal_return") is None:
            print(f"| {r['symbol']} | {r['label']} | | | | ERROR {r.get('error', 'no abnormal return')} |")
            continue
        t = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.2f}"
        print(f"| {r['symbol']} | {r['label']} | {r['day0']} | {me.pct(r['abnormal_return'])} | {t} | {r['class']} |")

    rows = []
    for ar in GRID_AR:
        for t in GRID_T:
            missed = [r["symbol"] for r in ok if r["label"] == "pursue" and not flagged(r, ar, t)]
            extra = sum(1 for r in ok if r["label"] == "pass" and flagged(r, ar, t))
            rows.append((len(missed), extra, ar, t, missed))  # ties: strictest first (fewest names to search)
    rows.sort()
    cur = (me.AR_BORDER, me.T_BORDER)
    print(f"\nThreshold grid for reaching triage (current: AR <= {cur[0]:.0%}, t <= {cur[1]}), best first:\n")
    print("| AR <= | t <= | Pursued missed | Passed flagged | Missed cases |")
    print("|---|---|---|---|---|")
    for m, x, ar, t, missed in rows[:12] + [r for r in rows if (r[2], r[3]) == cur and r not in rows[:12]]:
        mark = " (current)" if (ar, t) == cur else ""
        print(f"| {ar:.0%}{mark} | {t} | {m} of {n_p} | {x} of {n_x} | {', '.join(missed) or '-'} |")


if __name__ == "__main__":
    main()
