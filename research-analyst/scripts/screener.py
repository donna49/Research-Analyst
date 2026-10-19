#!/usr/bin/env python3
"""Andrew's daily screen: every stock that fell more than 10% in the last closed trading session before
today and meets his trigger (references/trigger.md).

  (a) TSX, TSXV, CSE, Cboe Canada (NEO) listings with a market cap over C$200M; or
  (b) Canadian companies whose security fell on NYSE, Nasdaq, NYSE American or US OTC, with a market cap
      over C$200M (USD caps converted at the current USD/CAD rate).

The session screened is always the last one that closed before today: on a Tuesday, Monday's; on a Monday
or over a weekend, Friday's; after a holiday, the session before it. The date is read from each market's
own daily bars (TSX index for Canada, S&P 500 for the US), so exchange holidays are handled. Market cap is
rebased to the close before the drop.

Usage:
  screener.py [--out runs/<session date>] [--min-cap 200e6] [--drop 10]

Writes <out>/screener.md (the trigger names; the input to triage), <out>/screener_outside.md (10%+ falls
that missed the trigger, with the reason) and <out>/screener.json.
Requires: websocket-client (for the session dates).
"""
import argparse, datetime as dt, json, os, sys, time, urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from market_event import _tv_bars  # noqa: E402

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
BASE = ["name", "description", "exchange", "market_cap_basic", "currency", "country", "is_primary", "type",
        "average_volume_30d_calc", "close"]
US_EXCH = ["NYSE", "NASDAQ", "AMEX", "OTC"]
SESSION_INDEX = {"canada": ("TSX:TSX", "America/Toronto"), "america": ("SP:SPX", "America/New_York")}
FLOW_CHART_CAP = 250e6  # his flow chart; his Oct 19, 2026 message lowered it to 200M
FALLBACK_USDCAD = 1.38


def scan(market, body):
    req = urllib.request.Request(f"https://scanner.tradingview.com/{market}/scan", data=json.dumps(body).encode(),
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)["data"]
        except Exception:
            if i == 2:
                raise
            time.sleep(3 * (i + 1))


def last_closed_session(market):
    """(k, session date): k is the scanner bar offset of the last session that closed before today."""
    symbol, tz = SESSION_INDEX[market]
    _, bars = _tv_bars(symbol, "dividends", 5)
    dates = sorted(dt.datetime.fromtimestamp(b["v"][0], dt.timezone.utc).date() for b in bars)
    today = dt.datetime.now(ZoneInfo(tz)).date()
    if dates[-1] >= today:
        return 1, dates[-2]
    return 0, dates[-1]


def cols(k):
    s = f"[{k}]" if k else ""
    return BASE + [f"change{s}", f"close{s}", f"close[{k + 1}]", f"volume{s}"]


def rows(market, k, filters):
    c = cols(k)
    data = scan(market, {"columns": c, "range": [0, 2000], "filter": filters,
                         "sort": {"sortBy": c[-4], "sortOrder": "asc"}})
    out = []
    for x in data:
        r = dict(zip(BASE, x["d"]), symbol=x["s"])
        r["chg"], r["px"], r["prev_close"], r["vol"] = x["d"][len(BASE):]
        out.append(r)
    return out


def usdcad():
    try:
        d = scan("forex", {"columns": ["close"], "range": [0, 1],
                           "filter": [{"left": "name", "operation": "equal", "right": "USDCAD"}]})
        return float(d[0]["d"][0]), "TradingView FX:USDCAD"
    except Exception:
        return FALLBACK_USDCAD, f"fallback {FALLBACK_USDCAD} (FX lookup failed)"


def primary_listing(description, sessions):
    """The company's primary listing (Canada first, then the US), found by company name, on the same session."""
    name = (description or "").replace(" Unsponsored ADR", "").replace(" Sponsored ADR", "")
    if not name:
        return None
    for market in ("canada", "america"):
        for r in rows(market, sessions[market][0], [{"left": "description", "operation": "equal", "right": name},
                                                    {"left": "is_primary", "operation": "equal", "right": True}]):
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="folder for the outputs (default runs/<session date>)")
    ap.add_argument("--min-cap", type=float, default=200e6, help="market cap threshold in CAD")
    ap.add_argument("--drop", type=float, default=10.0, help="minimum one-day fall, in percent")
    a = ap.parse_args()
    sessions = {m: last_closed_session(m) for m in SESSION_INDEX}
    session = sessions["canada"][1]
    out = a.out or os.path.join("runs", session.isoformat())
    os.makedirs(out, exist_ok=True)
    fx, fx_src = usdcad()
    stock = {"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]}

    def fall(market):
        k = sessions[market][0]
        return {"left": f"change[{k}]" if k else "change", "operation": "less", "right": -a.drop}

    cands = [dict(r, venue_test="a") for r in rows("canada", sessions["canada"][0], [fall("canada"), stock])]
    cands += [dict(r, venue_test="b") for r in rows("america", sessions["america"][0], [
        fall("america"), stock, {"left": "country", "operation": "equal", "right": "Canada"},
        {"left": "exchange", "operation": "in_range", "right": US_EXCH}])]

    hits, outside, seen = [], [], {}
    for r in cands:
        cap, reason = r.get("market_cap_basic"), None
        # cap before the drop: today's cap rebased from the latest close to the close before the drop
        ratio = r["prev_close"] / r["close"] if r.get("close") and r.get("prev_close") else None
        if (r.get("px") or 0) < 0.001 or (ratio and not 0.05 < ratio < 20):
            reason = "unreliable quote (sub-cent price or a near-total move); check by hand if the name matters"
        elif cap and ratio:
            cap = cap * ratio
        cap_cad = cap * (fx if r.get("currency") == "USD" else 1) if cap else None
        r["market_cap_cad"] = cap_cad
        r["session"] = sessions["america" if r["venue_test"] == "b" else "canada"][1].isoformat()
        flags = []
        desc = r.get("description") or ""
        if r["venue_test"] == "a" and ("Depositary Receipt" in desc or "Depository Receipt" in desc):
            reason = "Canadian Depositary Receipt of a foreign issuer"
        if cap_cad is None:
            reason = reason or "no market cap reported"
        elif cap_cad <= a.min_cap:
            reason = reason or f"market cap C${cap_cad / 1e6:,.0f}M, not over C${a.min_cap / 1e6:,.0f}M"
        elif cap_cad <= FLOW_CHART_CAP:
            flags.append("cap between C$200M and C$250M (below the flow-chart threshold)")
        if r["venue_test"] == "b":
            flags.append("verify Canadian registration and SEDAR+ reporting")
        if not reason and (r["venue_test"] == "b" or r.get("is_primary") is False):
            home = primary_listing(desc, sessions)
            if home and home["symbol"] != r["symbol"] and home.get("chg") is not None:
                if home["chg"] > -a.drop:
                    flags.append(f"primary listing {home['symbol']} moved only {home['chg']:.1f}%: "
                                 "likely a stale secondary quote")
                else:
                    flags.append(f"primary listing {home['symbol']} also fell {home['chg']:.1f}%")
            elif r.get("is_primary") is False:
                flags.append("not the primary listing")
        if (r.get("vol") or 0) < 0.2 * (r.get("average_volume_30d_calc") or 0):
            flags.append("thin volume")
        r["flags"] = flags
        key = desc.lower()
        if reason:
            r["reason"] = reason
            outside.append(r)
        elif key and key in seen:
            seen[key]["also_fell_on"].append(f"{r['symbol']} ({r['chg']:.1f}%)")
        else:
            r["also_fell_on"] = []
            seen[key] = r
            hits.append(r)

    hits.sort(key=lambda r: (any("stale" in f for f in r["flags"]), r["venue_test"], r["chg"]))
    us_note = ""
    if sessions["america"][1] != session:
        us_note = f" US listings: session of {sessions['america'][1]} (US and Canadian holidays differ)."
    with open(os.path.join(out, "screener.md"), "w") as f:
        f.write(f"# Screen of the session of {session}: falls over {a.drop:g}% meeting Andrew's trigger\n\n")
        f.write(f"Source: TradingView scanner, last session closed before today.{us_note} USD/CAD {fx:.4f} "
                f"({fx_src}). Market cap at the close before the drop. {len(hits)} names; {len(outside)} other "
                f"{a.drop:g}%+ falls in `screener_outside.md`.\n")
        f.write("\n| Company | Ticker | Close | Drop % | Market cap before (C$M) | Venue test | Also fell on | Flags |\n"
                "|---|---|---|---|---|---|---|---|\n")
        for r in hits:
            f.write(f"| {r['description']} | {r['symbol']} | {r['px']} {r['currency']} | {r['chg']:.2f}% | "
                    f"{r['market_cap_cad'] / 1e6:,.0f} | {r['venue_test']} | {', '.join(r['also_fell_on'])} | "
                    f"{'; '.join(r['flags'])} |\n")
    with open(os.path.join(out, "screener_outside.md"), "w") as f:
        f.write(f"# Falls over {a.drop:g}% outside the trigger (session of {session})\n\n"
                "| Company | Listing | Drop % | Reason |\n|---|---|---|---|\n")
        for r in outside:
            f.write(f"| {r['description']} | {r['symbol'].replace(':', ' ')} | {r['chg']:.2f}% | {r['reason']} |\n")
    with open(os.path.join(out, "screener.json"), "w") as f:
        json.dump({"session": session.isoformat(),
                   "sessions": {m: {"offset": k, "date": d.isoformat()} for m, (k, d) in sessions.items()},
                   "usdcad": fx, "usdcad_source": fx_src, "min_cap_cad": a.min_cap, "drop_pct": a.drop,
                   "hits": hits, "outside": outside}, f, indent=1)
    print(f"Session {session}: {len(hits)} names meet the trigger; {len(outside)} outside. Wrote {out}/screener.md")


if __name__ == "__main__":
    main()
