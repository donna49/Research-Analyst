#!/usr/bin/env python3
"""Andrew's daily screen: every stock that fell more than 10% in the latest session and meets his
trigger (references/trigger.md).

  (a) TSX, TSXV, CSE, Cboe Canada (NEO) listings with a market cap over C$200M; or
  (b) Canadian companies whose security fell on NYSE, Nasdaq, NYSE American or US OTC, with a market cap
      over C$200M (USD caps converted at the day's USD/CAD rate).

Usage:
  screener.py [--out runs/<date>] [--min-cap 200e6] [--drop 10]

Writes <out>/screener.md (the trigger names; the input to triage), <out>/screener_outside.md (10%+ falls
that missed the trigger, with the reason) and <out>/screener.json. Run after the close: the TradingView
scanner reports the latest session, so a run during trading hours sees intraday moves (flagged).
Requires nothing beyond the standard library.
"""
import argparse, datetime as dt, json, os, time, urllib.request
from zoneinfo import ZoneInfo

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
COLS = ["name", "description", "exchange", "close", "change", "market_cap_basic", "currency", "country",
        "is_primary", "type", "volume", "average_volume_30d_calc"]
US_EXCH = ["NYSE", "NASDAQ", "AMEX", "OTC"]
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


def rows(market, filters):
    data = scan(market, {"columns": COLS, "range": [0, 2000], "filter": filters,
                         "sort": {"sortBy": "change", "sortOrder": "asc"}})
    return [dict(zip(COLS, x["d"]), symbol=x["s"]) for x in data]


def usdcad():
    try:
        d = scan("forex", {"columns": ["close"], "range": [0, 1],
                           "filter": [{"left": "name", "operation": "equal", "right": "USDCAD"}]})
        return float(d[0]["d"][0]), "TradingView FX:USDCAD"
    except Exception:
        return FALLBACK_USDCAD, f"fallback {FALLBACK_USDCAD} (FX lookup failed)"


def primary_listing(description):
    """The company's primary listing (Canada first, then the US), found by company name."""
    name = (description or "").replace(" Unsponsored ADR", "").replace(" Sponsored ADR", "")
    if not name:
        return None
    for market in ("canada", "america"):
        for r in rows(market, [{"left": "description", "operation": "equal", "right": name},
                               {"left": "is_primary", "operation": "equal", "right": True}]):
            return r
    return None


def session_note():
    now = dt.datetime.now(ZoneInfo("America/Toronto"))
    if now.weekday() < 5 and dt.time(9, 30) <= now.time() < dt.time(16, 0):
        return f"run at {now:%H:%M} Toronto time, during trading: moves are intraday, re-run after 16:00"
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="folder for the outputs (default runs/<today>)")
    ap.add_argument("--min-cap", type=float, default=200e6, help="market cap threshold in CAD")
    ap.add_argument("--drop", type=float, default=10.0, help="minimum one-day fall, in percent")
    a = ap.parse_args()
    today = dt.datetime.now(ZoneInfo("America/Toronto")).date()
    out = a.out or os.path.join("runs", today.isoformat())
    os.makedirs(out, exist_ok=True)
    fx, fx_src = usdcad()
    fall = {"left": "change", "operation": "less", "right": -a.drop}
    stock = {"left": "type", "operation": "in_range", "right": ["stock", "dr", "fund"]}

    cands = [dict(r, venue_test="a") for r in rows("canada", [fall, stock])]
    cands += [dict(r, venue_test="b") for r in rows("america", [
        fall, stock, {"left": "country", "operation": "equal", "right": "Canada"},
        {"left": "exchange", "operation": "in_range", "right": US_EXCH}])]

    hits, outside, seen = [], [], {}
    for r in cands:
        cap = r.get("market_cap_basic")
        cap_cad = cap * (fx if r.get("currency") == "USD" else 1) if cap else None
        r["market_cap_cad"] = cap_cad
        flags, reason = [], None
        desc = r.get("description") or ""
        if "Depositary Receipt" in desc or "Depository Receipt" in desc:
            if r["venue_test"] == "a":
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
            home = primary_listing(desc)
            if home and home["symbol"] != r["symbol"] and home.get("change") is not None:
                if home["change"] > -a.drop:
                    flags.append(f"primary listing {home['symbol']} moved only {home['change']:.1f}%: "
                                 "likely a stale secondary quote")
                else:
                    flags.append(f"primary listing {home['symbol']} also fell {home['change']:.1f}%")
            elif r.get("is_primary") is False:
                flags.append("not the primary listing")
        if (r.get("volume") or 0) < 0.2 * (r.get("average_volume_30d_calc") or 0):
            flags.append("thin volume")
        r["flags"] = flags
        key = desc.lower()
        if reason:
            r["reason"] = reason
            outside.append(r)
        elif key and key in seen:
            seen[key]["also_fell_on"].append(f"{r['symbol']} ({r['change']:.1f}%)")
        else:
            r["also_fell_on"] = []
            seen[key] = r
            hits.append(r)

    # prefer the primary listing as the row shown, keeping the others as "also fell on"
    for r in hits:
        r["other"] = ", ".join(r["also_fell_on"])

    note = session_note()
    with open(os.path.join(out, "screener.md"), "w") as f:
        f.write(f"# Screen of {today}: falls over {a.drop:g}% meeting Andrew's trigger\n\n")
        f.write(f"Source: TradingView scanner, latest session. USD/CAD {fx:.4f} ({fx_src}). "
                f"{len(hits)} names; {len(outside)} other {a.drop:g}%+ falls in `screener_outside.md`.\n")
        if note:
            f.write(f"\n**{note}.**\n")
        f.write("\n| Company | Ticker | Price | Drop % | Market cap (C$M) | Venue test | Also fell on | Flags |\n"
                "|---|---|---|---|---|---|---|---|\n")
        for r in hits:
            f.write(f"| {r['description']} | {r['symbol']} | {r['close']} {r['currency']} | {r['change']:.2f}% | "
                    f"{r['market_cap_cad'] / 1e6:,.0f} | {r['venue_test']} | {r['other']} | {'; '.join(r['flags'])} |\n")
    with open(os.path.join(out, "screener_outside.md"), "w") as f:
        f.write(f"# Falls over {a.drop:g}% outside the trigger ({today})\n\n| Company | Listing | Drop % | Reason |\n"
                "|---|---|---|---|\n")
        for r in outside:
            f.write(f"| {r['description']} | {r['symbol'].replace(':', ' ')} | {r['change']:.2f}% | {r['reason']} |\n")
    with open(os.path.join(out, "screener.json"), "w") as f:
        json.dump({"date": today.isoformat(), "usdcad": fx, "usdcad_source": fx_src, "session_note": note,
                   "min_cap_cad": a.min_cap, "drop_pct": a.drop, "hits": hits, "outside": outside}, f, indent=1)
    print(f"{len(hits)} names meet the trigger; {len(outside)} outside. Wrote {out}/screener.md")


if __name__ == "__main__":
    main()
