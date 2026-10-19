#!/usr/bin/env python3
"""Case economics for a Layer 2 memo (references/economics.md).

  economics.py runs/<date>/<TICKER>/economics_input.json [--json out.json]
  economics.py --moves EXCH:TICKER 2026-05-07 2026-08-06 ...   # price move on each disclosure date

The input file lists the venues, the Class Period start, the corrections and the shares
outstanding, each with the ledger id that supports it. The script computes the price reaction to
each correction, the ten-day look-back, the Class Period volume per venue, damaged-share and damages
ranges, the 5% liability cap, a settlement target and the limitation dates. Every output number
carries the formula that produced it, so the memo can show its work.

Prices: the TradingView chart feed via market_event.history(), split-adjusted only (no dividend
adjustment), so figures match the quoted market prices Andrew writes in his memos. A share
consolidation inside the window is flagged because split adjustment rescales earlier prices.
"""
import argparse, datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market_event import history  # noqa: E402

DEFAULT_RETENTION = [0.25, 0.40, 0.50]
SETTLEMENT_RATIOS = [0.10, 0.20]
CAP_PCT, CAP_FLOOR = 0.05, 1_000_000


def series(symbol):
    h = history(symbol, "splits")
    rows = [r for r in h["rows"] if r["close"]]
    return h, [r["date"] for r in rows], rows


def idx_on_or_after(dates, d):
    for i, x in enumerate(dates):
        if x >= d:
            return i
    return None


def reaction(dates, rows, day0):
    i = idx_on_or_after(dates, day0)
    if i is None or i == 0:
        return {"day0": day0, "error": "no session on or after this date in the price history"}
    prev, c0 = rows[i - 1]["close"], rows[i]["close"]
    look = rows[i:i + 10]
    vols = [r["volume"] for r in rows[max(0, i - 30):i] if r["volume"]]
    avg_vol = sum(vols) / len(vols) if vols else None
    lv = sum(r["volume"] or 0 for r in look)
    out = {
        "day0": dates[i], "prev_date": dates[i - 1], "prev_close": prev, "close0": c0,
        "drop_per_share": prev - c0, "drop_pct": c0 / prev - 1,
        "volume0": rows[i]["volume"], "avg_volume_30d": avg_vol,
        "volume_ratio": rows[i]["volume"] / avg_vol if rows[i]["volume"] and avg_vol else None,
        "lookback_sessions": len(look), "lookback_end": look[-1]["date"],
        "lookback_avg_10d": sum(r["close"] for r in look) / len(look),
        "lookback_vwap_10d": (sum(r["close"] * (r["volume"] or 0) for r in look) / lv) if lv else None,
    }
    out["recovered_share_of_drop"] = ((out["lookback_avg_10d"] - c0) / (prev - c0)) if prev != c0 else None
    if len(look) < 10:
        out["flag"] = f"only {len(look)} sessions available after day 0; look-back incomplete"
    if dates[i] != day0:
        out["note"] = f"{day0} was not a session; day 0 moved to {dates[i]}"
    return out


def moves(symbol, ds):
    _, dates, rows = series(symbol)
    print(f"Price move on each date for {symbol} (split-adjusted closes)")
    print("| Date | Session | Prev close | Close | Change | Volume x avg |")
    print("|---|---|---|---|---|---|")
    res = []
    for d in ds:
        r = reaction(dates, rows, d)
        res.append(r)
        if "error" in r:
            print(f"| {d} | | | | ERROR {r['error']} | |")
            continue
        ch = "nil%" if abs(r["drop_pct"]) < 0.0005 else f"{r['drop_pct']:+.1%}"
        vr = "n/a" if r["volume_ratio"] is None else f"{r['volume_ratio']:.1f}x"
        print(f"| {d} | {r['day0']} | {r['prev_close']:.4g} | {r['close0']:.4g} | {ch} | {vr} |")
    return res


def add_years(d, n):
    try:
        return d.replace(year=d.year + n)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + n, day=28)


def run(path):
    cfg = json.load(open(path))
    flags, out = [], {"input": os.path.abspath(path), "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                      "price_basis": "TradingView chart feed, split-adjusted, not dividend-adjusted"}
    start = cfg["class_period"]["start"]
    corrections = sorted(cfg["corrections"], key=lambda c: c["date"])
    retention = cfg.get("retention") or DEFAULT_RETENTION
    venues = []
    for v in cfg["venues"]:
        h, dates, rows = series(v["symbol"])
        cur = v.get("currency") or h.get("currency")
        reacts = [dict(reaction(dates, rows, c["date"]), label=c.get("label", ""),
                       storm_warning=bool(c.get("storm_warning")), ledger=c.get("ledger")) for c in corrections]
        ok = [r for r in reacts if "error" not in r]
        vinfo = {"symbol": v["symbol"], "role": v.get("role", ""), "currency": cur, "corrections": reacts}
        if not ok:
            vinfo["error"] = "no usable correction sessions"
            venues.append(vinfo)
            continue
        first_day0, last = ok[0]["day0"], ok[-1]
        cp = [r for r in rows if start <= r["date"] < first_day0]
        if not cp:
            vinfo["error"] = "no sessions between Class Period start and first correction"
            venues.append(vinfo)
            continue
        cvol = sum(r["volume"] or 0 for r in cp)
        cvwap = sum(r["close"] * (r["volume"] or 0) for r in cp) / cvol if cvol else None
        m1 = sum(r["drop_per_share"] for r in ok)
        m2 = ok[0]["prev_close"] - last["lookback_avg_10d"]
        m3 = (cvwap - last["lookback_avg_10d"]) if cvwap else None
        vinfo.update({
            "class_period": {"start": start, "end_session": cp[-1]["date"], "sessions": len(cp)},
            "class_volume": cvol,
            "class_vwap": cvwap,
            "per_share": {
                "m1_day0_drops": {"value": m1, "formula": " + ".join(f"({r['prev_close']:.4g}-{r['close0']:.4g})" for r in ok)},
                "m2_statutory": {"value": m2, "formula": f"{ok[0]['prev_close']:.4g} - lookback_avg_10d {last['lookback_avg_10d']:.4g}"},
                "m3_upper": {"value": m3, "formula": None if m3 is None else f"class_vwap {cvwap:.4g} - lookback_avg_10d {last['lookback_avg_10d']:.4g}"},
            },
            "damaged_shares": {str(k): cvol * k for k in retention},
            # a negative per-share figure means the price recovered past the pre-correction close: no loss on that measure
            "damages": {str(k): {"m1": cvol * k * max(m1, 0), "m2": cvol * k * max(m2, 0),
                                 "m3": None if m3 is None else cvol * k * max(m3, 0)}
                        for k in retention},
        })
        if m2 <= 0:
            flags.append(f"{v['symbol']}: price on the 10-day look-back is at or above the pre-correction close (no statutory loss)")
        rec = last.get("recovered_share_of_drop")
        if rec is not None and rec > 0.75:
            flags.append(f"{v['symbol']}: 10-day look-back recovered {rec:.0%} of the final day-0 drop (Alamos pattern)")
        venues.append(vinfo)
    out["venues"] = venues

    tot = sum(v.get("class_volume", 0) for v in venues)
    if tot:
        out["volume_split"] = {v["symbol"]: v.get("class_volume", 0) / tot for v in venues}
        for v in venues:
            if v.get("class_volume", 0) / tot > 0.8 and v.get("role") != "primary":
                flags.append(f"{v['symbol']} holds {v['class_volume']/tot:.0%} of Class Period volume (Paladin pattern)")

    # liability cap from the primary venue
    prim = next((v for v in cfg["venues"] if v.get("role") == "primary"), cfg["venues"][0])
    _, dates, rows = series(prim["symbol"])
    i = idx_on_or_after(dates, start)
    cap = None
    if i is not None:
        win = rows[max(0, i - 10):i]
        if win:
            avg_p = sum(r["close"] for r in win) / len(win)
            classes = []
            mcap = 0.0
            for s in cfg.get("shares_outstanding", []):
                val = s["shares"] * (s.get("price_override") or avg_p)
                classes.append({**s, "price_used": s.get("price_override") or avg_p, "value": val})
                mcap += val
            mcap += cfg.get("other_equity_fmv", 0)
            if classes:
                cap = max(CAP_PCT * mcap, CAP_FLOOR)
                out["liability_cap"] = {
                    "window": f"{win[0]['date']} to {win[-1]['date']} ({len(win)} sessions before {start})",
                    "avg_close": avg_p, "classes": classes, "other_equity_fmv": cfg.get("other_equity_fmv", 0),
                    "market_cap": mcap, "cap": cap, "currency": prim.get("currency"),
                    "formula": "max(5% x market_cap, 1,000,000); market_cap = sum(shares x 10-day avg close) + other FMV",
                    "note": "s. 249 averages the shares outstanding over the same 10 days; the reported figure nearest the window is used, see each class's as_of"}
            else:
                flags.append("no shares_outstanding supplied: liability cap not computed")

    # headline ranges on the primary venue
    pv = next((v for v in venues if v["symbol"] == prim["symbol"] and "damages" in v), None)
    if pv:
        mid = str(retention[len(retention) // 2])
        vals = [x for k in pv["damages"].values() for x in (k["m1"], k["m2"]) if x is not None]
        cl_mid = pv["damages"][mid]["m2"]
        out["headline"] = {
            "venue": prim["symbol"], "currency": pv["currency"],
            "common_law_rough": {"mid": cl_mid, "low": min(vals), "high": max(vals), "retention_mid": float(mid)},
            "statutory_capped": None if cap is None else min(cl_mid, cap),
            "settlement_target": {"low": max(SETTLEMENT_RATIOS[0] * cl_mid, 0.5 * min(cl_mid, cap) if cap else 0),
                                   "high": SETTLEMENT_RATIOS[1] * cl_mid},
            "basis": "damaged shares = Class Period volume on this venue x retention; per share = measure m2 unless stated",
        }
        if out["headline"]["settlement_target"]["low"] < 5_000_000:
            flags.append("settlement target low end below 5M: below the targets in Andrew's origination memos")

    fid = dt.date.fromisoformat(cfg.get("first_impugned_date", start))
    lastc = dt.date.fromisoformat(corrections[-1]["date"])
    today = dt.date.today()
    lim = {"s138_14_expiry": add_years(fid, 3).isoformat(), "common_law_expiry_proxy": add_years(lastc, 2).isoformat(),
           "basis": "s. 138.14: 3 years after first impugned document; common law: 2 years after correction (discovery proxy)"}
    for k in ("s138_14_expiry", "common_law_expiry_proxy"):
        days = (dt.date.fromisoformat(lim[k]) - today).days
        lim[k + "_days_left"] = days
        if days < 183:
            flags.append(f"{k} is {days} days away")
    out["limitations"] = lim
    for k in ("d_and_o", "cash"):
        if cfg.get(k):
            out[k] = cfg[k]
    out["flags"] = flags
    return out


def fmt(x, cur=""):
    if x is None:
        return "n/a"
    a = abs(x)
    s = f"{x/1e9:.2f}B" if a >= 1e9 else f"{x/1e6:.1f}M" if a >= 1e6 else f"{x:,.0f}"
    return f"{cur} {s}".strip()


def report(o):
    for v in o["venues"]:
        print(f"\n## {v['symbol']} ({v.get('role') or 'venue'}, {v.get('currency')})")
        if v.get("error"):
            print("ERROR:", v["error"])
        for r in v["corrections"]:
            if "error" in r:
                print(f"- {r['day0']}: ERROR {r['error']}")
                continue
            tag = "STORM WARNING" if r["storm_warning"] else "Correction"
            vr = "n/a" if r["volume_ratio"] is None else f"{r['volume_ratio']:.1f}x"
            print(f"- {tag} {r['day0']}: {r['prev_close']:.4g} -> {r['close0']:.4g} ({r['drop_pct']:+.1%}), volume {vr} avg; "
                  f"10-day look-back avg {r['lookback_avg_10d']:.4g} (to {r['lookback_end']})")
        if "class_volume" in v:
            print(f"- Class Period {v['class_period']['start']} to {v['class_period']['end_session']}: volume {v['class_volume']:,.0f}, VWAP {v['class_vwap']:.4g}")
            for k, m in v["per_share"].items():
                val = "n/a" if m["value"] is None else f"{m['value']:.4g}"
                print(f"- per share {k}: {val}  [{m['formula']}]")
            for k, d in v["damages"].items():
                print(f"- retention {k}: shares {v['damaged_shares'][k]:,.0f}; damages m1 {fmt(d['m1'], v['currency'])}, m2 {fmt(d['m2'], v['currency'])}, m3 {fmt(d['m3'], v['currency'])}")
    if o.get("volume_split"):
        print("\nVolume split: " + "; ".join(f"{k} {x:.0%}" for k, x in o["volume_split"].items()))
    c = o.get("liability_cap")
    if c:
        print(f"\nLiability cap: market cap {fmt(c['market_cap'], c['currency'])} (avg close {c['avg_close']:.4g}, {c['window']}) -> cap {fmt(c['cap'], c['currency'])}")
    h = o.get("headline")
    if h:
        cl = h["common_law_rough"]
        print(f"Headline ({h['venue']}): common law ~{fmt(cl['mid'], h['currency'])} (range {fmt(cl['low'], h['currency'])}-{fmt(cl['high'], h['currency'])}); "
              f"statutory capped {fmt(h['statutory_capped'], h['currency'])}; settlement target {fmt(h['settlement_target']['low'], h['currency'])}-{fmt(h['settlement_target']['high'], h['currency'])}")
    lim = o["limitations"]
    print(f"Limitations: s. 138.14 {lim['s138_14_expiry']} ({lim['s138_14_expiry_days_left']} days); common law ~{lim['common_law_expiry_proxy']} ({lim['common_law_expiry_proxy_days_left']} days)")
    for f in o["flags"]:
        print("FLAG:", f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("--json")
    ap.add_argument("--moves", nargs="+", metavar=("SYMBOL", "DATE"))
    a = ap.parse_args()
    if a.moves:
        res = moves(a.moves[0], a.moves[1:])
        if a.json:
            json.dump(res, open(a.json, "w"), indent=1)
        return
    if not a.input:
        sys.exit(__doc__)
    o = run(a.input)
    if a.json:
        json.dump(o, open(a.json, "w"), indent=1, default=str)
    report(o)


if __name__ == "__main__":
    main()
