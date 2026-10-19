#!/usr/bin/env python3
"""Case economics for a Layer 2 memo (references/economics.md).

  economics.py runs/<date>/<TICKER>/economics_input.json [--json out.json]
  economics.py --moves EXCH:TICKER 2026-05-07 2026-08-06+ ...  # price move on each disclosure date
                                     # a trailing + means released after the close: next session reacts
  options: --asof YYYY-MM-DD (date the limitation countdown runs from; default today)

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
import market_event  # noqa: E402
from market_event import history  # noqa: E402

DEFAULT_RETENTION = [0.25, 0.40, 0.50]
SETTLEMENT_RATIOS = [0.10, 0.20]
CAP_PCT, CAP_FLOOR = 0.05, 1_000_000


def series(symbol):
    h = history(symbol, "splits")
    rows = [r for r in h["rows"] if r["close"]]
    return h, [r["date"] for r in rows], rows


def idx_on_or_after(dates, d, after_close=False):
    for i, x in enumerate(dates):
        if x > d or (x == d and not after_close):
            return i
    return None


def parse_date(d):
    """'2025-01-23+' = released after the close on Jan 23."""
    return (d[:-1], True) if d.endswith("+") else (d, False)


def reaction(dates, rows, day0, after_close=False):
    i = idx_on_or_after(dates, day0, after_close)
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
        "lookback_close_10th": look[-1]["close"],
    }
    out["recovered_share_of_drop"] = ((out["lookback_avg_10d"] - c0) / (prev - c0)) if prev != c0 else None
    if len(look) < 10:
        out["flag"] = f"only {len(look)} sessions available after day 0; look-back incomplete"
    if dates[i] != day0:
        out["note"] = (f"released after the close on {day0}; reacting session {dates[i]}" if after_close
                       else f"{day0} was not a session; day 0 moved to {dates[i]}")
    return out


def moves(symbol, ds):
    market_event.ensure_history_for(dt.date.fromisoformat(min(parse_date(d)[0] for d in ds)))
    _, dates, rows = series(symbol)
    print(f"Price move on each date for {symbol} (split-adjusted closes)")
    print("| Date | Session | Prev close | Close | Change | Volume x avg |")
    print("|---|---|---|---|---|---|")
    res = []
    for d in ds:
        r = reaction(dates, rows, *parse_date(d))
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


def run(path, asof=None):
    cfg = json.load(open(path))
    market_event.ensure_history_for(dt.date.fromisoformat(cfg["class_period"]["start"]) - dt.timedelta(days=60))
    flags, out = [], {"input": os.path.abspath(path), "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                      "price_basis": "TradingView chart feed, split-adjusted, not dividend-adjusted"}
    start = cfg["class_period"]["start"]
    corrections = sorted(cfg["corrections"], key=lambda c: c["date"])
    retention = cfg.get("retention") or DEFAULT_RETENTION
    venues = []
    for v in cfg["venues"]:
        h, dates, rows = series(v["symbol"])
        cur = v.get("currency") or h.get("currency")
        reacts = [dict(reaction(dates, rows, c["date"], bool(c.get("after_close"))), label=c.get("label", ""),
                       storm_warning=bool(c.get("storm_warning")), ledger=c.get("ledger")) for c in corrections]
        ok = [r for r in reacts if "error" not in r]
        vinfo = {"symbol": v["symbol"], "role": v.get("role", ""), "currency": cur, "corrections": reacts}
        if not ok:
            vinfo["error"] = "no usable correction sessions"
            venues.append(vinfo)
            continue
        # purchasers up to the final correction are in the class (those who bought after a storm warning
        # still lose on the later corrections)
        last = ok[-1]
        cp = [r for r in rows if start <= r["date"] < last["day0"]]
        if not cp:
            vinfo["error"] = "no sessions between Class Period start and first correction"
            venues.append(vinfo)
            continue
        cvol = sum(r["volume"] or 0 for r in cp)
        cvwap = sum(r["close"] * (r["volume"] or 0) for r in cp) / cvol if cvol else None
        lb = last["lookback_avg_10d"]
        # Segment the Class Period at each correction: shares bought before correction j bear the drops
        # from j onward. m1 = sum of later day-0 drops; m2 = pre-correction-j close minus the final
        # ten-day look-back; m3 = segment VWAP minus the final look-back (what an average buyer lost).
        bounds = [start] + [r["day0"] for r in ok]
        segs = []
        for j, r in enumerate(ok):
            rows_j = [x for x in cp if bounds[j] <= x["date"] < bounds[j + 1]]
            vol_j = sum(x["volume"] or 0 for x in rows_j)
            vwap_j = sum(x["close"] * (x["volume"] or 0) for x in rows_j) / vol_j if vol_j else None
            segs.append({"from": bounds[j], "to_before": bounds[j + 1], "volume": vol_j, "vwap": vwap_j,
                         "m1": max(sum(x["drop_per_share"] for x in ok[j:]), 0),
                         "m2": max(r["prev_close"] - lb, 0),
                         "m3": None if vwap_j is None else max(vwap_j - lb, 0)})
        m1 = sum(g["volume"] * g["m1"] for g in segs) / cvol if cvol else 0
        m2 = sum(g["volume"] * g["m2"] for g in segs) / cvol if cvol else 0
        m3 = sum(g["volume"] * (g["m3"] or 0) for g in segs) / cvol if cvol else None
        vinfo.update({
            "class_period": {"start": start, "end_session": cp[-1]["date"], "sessions": len(cp)},
            "class_volume": cvol,
            "class_vwap": cvwap,
            "segments": segs,
            "per_share": {
                "m1_day0_drops": {"value": m1, "formula": "volume-weighted over segments of the sum of later day-0 drops"},
                "m2_statutory": {"value": m2, "formula": f"volume-weighted over segments of (pre-correction close - final 10-day look-back avg {lb:.4g})"},
                "m3_upper": {"value": m3, "formula": f"volume-weighted over segments of (segment VWAP - final 10-day look-back avg {lb:.4g})"},
            },
            "damaged_shares": {str(k): cvol * k for k in retention},
            # negative per-share figures (price recovered past the pre-correction close) are floored at zero
            "damages": {str(k): {"m1": cvol * k * m1, "m2": cvol * k * m2, "m3": None if m3 is None else cvol * k * m3}
                        for k in retention},
        })
        m2 = ok[0]["prev_close"] - lb  # for the recovery flag below
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

    # Andrew's flow chart: the 5% cap is "measured at the time of the release of each impugned document"
    if cfg.get("impugned_dates") and cfg.get("shares_outstanding"):
        per = []
        shares_by_date = cfg.get("shares_by_date", {})
        for d in sorted(cfg["impugned_dates"]):
            j = idx_on_or_after(dates, d)
            win = rows[max(0, j - 10):j] if j is not None else []
            if not win:
                per.append({"date": d, "error": "no sessions before this date"})
                continue
            avg_p = sum(r["close"] for r in win) / len(win)
            shares = shares_by_date.get(d) or sum(s["shares"] for s in cfg["shares_outstanding"])
            mc = shares * avg_p + cfg.get("other_equity_fmv", 0)
            per.append({"date": d, "window": f"{win[0]['date']} to {win[-1]['date']}", "avg_close": avg_p,
                        "shares": shares, "shares_source": "shares_by_date" if d in shares_by_date else "shares_outstanding (flag: update per date)",
                        "market_cap": mc, "cap": max(CAP_PCT * mc, CAP_FLOOR)})
        out["liability_cap_by_document"] = {"currency": prim.get("currency"), "documents": per,
                                            "max_cap": max((x["cap"] for x in per if "cap" in x), default=None)}

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
            "settlement_target": {"low": min(max(SETTLEMENT_RATIOS[0] * cl_mid, 0.5 * min(cl_mid, cap) if cap else 0),
                                              SETTLEMENT_RATIOS[1] * cl_mid),
                                   "high": SETTLEMENT_RATIOS[1] * cl_mid},
            "basis": "damaged shares = Class Period volume on this venue x retention; per share = measure m2 unless stated",
        }
        if out["headline"]["settlement_target"]["low"] < 5_000_000:
            flags.append("settlement target low end below 5M: below the targets in Andrew's origination memos")

    # primary market (s. 130): offering price minus the ten-day look-back on the primary venue, x units sold
    if cfg.get("offerings") and pv:
        lb = next(r for r in reversed(pv["corrections"]) if "error" not in r)["lookback_avg_10d"]
        offs = []
        for o in cfg["offerings"]:
            per = max(o["price"] - lb, 0)
            offs.append({**o, "lookback_avg_10d": lb, "per_unit": per, "damages": per * o["units"],
                         "formula": f"max({o['price']} - {lb:.4g}, 0) x {o['units']:,}"})
        out["primary_market"] = {"offerings": offs, "total": sum(x["damages"] for x in offs), "currency": pv["currency"],
                                 "note": "kept separate from secondary-market damages; s. 130 needs a prospectus offering"}

    fid = dt.date.fromisoformat(cfg.get("first_impugned_date", start))
    lastc = dt.date.fromisoformat(corrections[-1]["date"])
    today = dt.date.fromisoformat(asof) if asof else dt.date.today()
    out["asof"] = today.isoformat()
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
                  f"10-day look-back avg {r['lookback_avg_10d']:.4g}, close on 10th session {r['lookback_close_10th']:.4g} ({r['lookback_end']})"
                  + (f" [{r['note']}]" if r.get("note") else ""))
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
    cbd = o.get("liability_cap_by_document")
    if cbd:
        for x in cbd["documents"]:
            if "cap" in x:
                print(f"Cap at impugned document {x['date']}: market cap {fmt(x['market_cap'], cbd['currency'])} (avg close {x['avg_close']:.4g}) -> cap {fmt(x['cap'], cbd['currency'])}")
    h = o.get("headline")
    if h:
        cl = h["common_law_rough"]
        print(f"Headline ({h['venue']}): common law ~{fmt(cl['mid'], h['currency'])} (range {fmt(cl['low'], h['currency'])}-{fmt(cl['high'], h['currency'])}); "
              f"statutory capped {fmt(h['statutory_capped'], h['currency'])}; settlement target {fmt(h['settlement_target']['low'], h['currency'])}-{fmt(h['settlement_target']['high'], h['currency'])}")
    pm = o.get("primary_market")
    if pm:
        for x in pm["offerings"]:
            print(f"Primary market {x.get('date')}: {x['formula']} = {fmt(x['damages'], pm['currency'])}")
    lim = o["limitations"]
    print(f"Limitations: s. 138.14 {lim['s138_14_expiry']} ({lim['s138_14_expiry_days_left']} days); common law ~{lim['common_law_expiry_proxy']} ({lim['common_law_expiry_proxy_days_left']} days)")
    for f in o["flags"]:
        print("FLAG:", f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("--json")
    ap.add_argument("--moves", nargs="+", metavar=("SYMBOL", "DATE"))
    ap.add_argument("--asof")
    a = ap.parse_args()
    if a.moves:
        res = moves(a.moves[0], a.moves[1:])
        if a.json:
            json.dump(res, open(a.json, "w"), indent=1)
        return
    if not a.input:
        sys.exit(__doc__)
    o = run(a.input, a.asof)
    if a.json:
        json.dump(o, open(a.json, "w"), indent=1, default=str)
    report(o)


if __name__ == "__main__":
    main()
