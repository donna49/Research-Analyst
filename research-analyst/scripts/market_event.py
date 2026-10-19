#!/usr/bin/env python3
"""Drop standard: is a one-day fall company-specific?

For each screener row this script measures the fall against the stock's own
normal behaviour relative to its home market index and an equal-weighted index
of same-industry peers, then classifies it (see references/drop-standard.md).

Usage:
  market_event.py EXCH:TICKER [EXCH:TICKER ...] [--date YYYY-MM-DD] [--json out.json]
  market_event.py --screener screener_output.md [--date ...] [--json ...]

Every number in the output comes from the fetched series, which are cached in
.cache/ so a run can be audited and reproduced.
"""
import argparse, datetime as dt, json, math, os, re, sys, time, urllib.request
import numpy as np

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache")

# Screener exchange prefix -> (Yahoo suffix, TradingView market, home market index)
EXCHANGES = {
    "NASDAQ": ("", "america", "^GSPC"), "NYSE": ("", "america", "^GSPC"),
    "AMEX": ("", "america", "^GSPC"), "NYSE ARCA": ("", "america", "^GSPC"),
    "OTC": ("", "america", "^GSPC"),
    "TSX": (".TO", "canada", "^GSPTSE"), "TSXV": (".V", "canada", "^GSPTSE"),
    "CSE": (".CN", "canada", "^GSPTSE"), "NEO": (".NE", "canada", "^GSPTSE"),
    "LSE": (".L", "uk", "^FTAS"), "AQUIS": (".AQ", "uk", "^FTAS"),
    "XETR": (".DE", "germany", "^GDAXI"), "FWB": (".F", "germany", "^GDAXI"),
    "GETTEX": (".DE", "germany", "^GDAXI"), "TRADEGATE": (".DE", "germany", "^GDAXI"),
}

# v1 thresholds; calibrate on Andrew's past cases (references/drop-standard.md)
AR_CLEAR, AR_BORDER = -0.07, -0.05
T_CLEAR, T_BORDER = -2.58, -1.96
EST_LEN, EST_GAP, MIN_OBS, N_PEERS = 120, 10, 60, 10


def _get(url, data=None, tries=5):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Content-Type": "application/json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # rate limits are common on Yahoo; back off and retry
            err = e
            if "429" in str(e) and "yahoo" in url and i >= 1:
                break  # persistent rate limit: let the caller fall back
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"{url}: {err}")


def yahoo_symbol(exch, ticker):
    suffix = EXCHANGES[exch][0]
    return ticker.replace(".", "-") + suffix if not suffix else ticker + suffix


def nasdaq_history(symbol, start, end):
    """US fallback: Nasdaq.com daily history (unadjusted; stocks and ETFs only)."""
    sym = {"^GSPC": "SPY"}.get(symbol, symbol)
    for cls in ("stocks", "etf"):
        url = (f"https://api.nasdaq.com/api/quote/{sym}/historical?assetclass={cls}"
               f"&fromdate={start}&todate={end}&limit=400")
        data = (_get(url, tries=2) or {}).get("data")
        if data and data.get("tradesTable", {}).get("rows"):
            break
    else:
        raise RuntimeError(f"no Nasdaq history for {sym}")
    num = lambda s: float(s.replace("$", "").replace(",", "")) if s not in (None, "", "N/A") else None
    rows = [{"date": dt.datetime.strptime(r["date"], "%m/%d/%Y").date().isoformat(),
             "close": num(r["close"]), "adj": num(r["close"]), "volume": num(r["volume"])}
            for r in reversed(data["tradesTable"]["rows"])]
    return {"symbol": sym, "source": "nasdaq.com (unadjusted)", "currency": "USD", "rows": rows,
            "events": {}, "retrieved": dt.datetime.utcnow().isoformat() + "Z"}


def history(symbol, start, end):
    """Daily bars, cached per symbol and window. Yahoo first; Nasdaq.com for US symbols if Yahoo refuses."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"px_{symbol.replace('^', '_')}_{start}_{end}.json")
    if os.path.exists(path):
        return json.load(open(path))
    try:
        out = yahoo_history(symbol, start, end)
    except Exception:
        if "." in symbol or (symbol.startswith("^") and symbol != "^GSPC"):
            raise
        out = nasdaq_history(symbol, start, end)
    json.dump(out, open(path, "w"))
    return out


def yahoo_history(symbol, start, end):
    p1 = int(dt.datetime.combine(start, dt.time()).timestamp())
    p2 = int(dt.datetime.combine(end + dt.timedelta(days=1), dt.time()).timestamp())
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(symbol)}"
           f"?period1={p1}&period2={p2}&interval=1d&events=div%2Csplit")
    res = _get(url)["chart"]["result"]
    if not res or "timestamp" not in res[0]:
        raise RuntimeError(f"no price history for {symbol}")
    r = res[0]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
    gmt = r["meta"].get("gmtoffset", 0)
    rows = [{"date": dt.datetime.utcfromtimestamp(t + gmt).date().isoformat(), "close": c, "adj": a, "volume": v}
            for t, c, a, v in zip(r["timestamp"], q["close"], adj, q["volume"]) if c is not None]
    return {"symbol": symbol, "source": "Yahoo Finance (adjusted)", "currency": r["meta"].get("currency"),
            "rows": rows, "events": r.get("events", {}), "retrieved": dt.datetime.utcnow().isoformat() + "Z"}


def tv_lookup(market, ticker):
    cols = ["name", "description", "exchange", "close", "change", "market_cap_basic", "sector",
            "industry", "volume", "average_volume_30d_calc", "country", "currency"]
    body = json.dumps({"columns": cols, "filter": [{"left": "name", "operation": "equal", "right": ticker},
                                                    {"left": "is_primary", "operation": "equal", "right": True}],
                       "range": [0, 5]}).encode()
    data = _get(f"https://scanner.tradingview.com/{market}/scan", body)["data"]
    return dict(zip(cols, data[0]["d"])) if data else None


def tv_peers(market, industry, ticker, n=N_PEERS):
    """Largest same-industry primary listings in the same market, excluding the stock itself."""
    body = json.dumps({"columns": ["name", "exchange", "market_cap_basic"],
                       "filter": [{"left": "industry", "operation": "equal", "right": industry},
                                  {"left": "type", "operation": "equal", "right": "stock"},
                                  {"left": "is_primary", "operation": "equal", "right": True},
                                  {"left": "exchange", "operation": "not_in_range", "right": ["OTC"]}],
                       "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
                       "range": [0, n + 5]}).encode()
    rows = _get(f"https://scanner.tradingview.com/{market}/scan", body)["data"]
    return [(x["d"][1], x["d"][0]) for x in rows if x["d"][0] != ticker and x["d"][1] in EXCHANGES][:n]


def returns(hist):
    """Map date -> daily simple return on adjusted close."""
    rows = hist["rows"]
    return {rows[i]["date"]: rows[i]["adj"] / rows[i - 1]["adj"] - 1
            for i in range(1, len(rows)) if rows[i]["adj"] and rows[i - 1]["adj"]}


def classify(ar, t, short_history):
    if ar is None:
        return "Insufficient data"
    if short_history:
        return "Borderline (short history)" if ar <= AR_BORDER else "Not company-specific"
    if ar <= AR_CLEAR and t <= T_CLEAR:
        return "Company-specific"
    if ar <= AR_BORDER and t <= T_BORDER:
        return "Borderline"
    return "Not company-specific"


def analyse(sym, day0=None):
    exch, ticker = sym.split(":", 1)
    if exch not in EXCHANGES:
        return {"symbol": sym, "error": f"exchange {exch} not mapped"}
    suffix, market, index = EXCHANGES[exch]
    ysym = yahoo_symbol(exch, ticker)
    end = day0 or dt.date.today()
    start = end - dt.timedelta(days=260)
    stock = history(ysym, start, end)
    dates = [r["date"] for r in stock["rows"]]
    d0 = day0.isoformat() if day0 else dates[-1]
    if d0 not in dates:
        return {"symbol": sym, "error": f"{d0} is not a trading day in the price history"}
    i0 = dates.index(d0)
    tv = tv_lookup(market, ticker) or {}
    flags = []

    r_s = returns(stock)
    r_m = returns(history(index, start, end))
    peers = tv_peers(market, tv["industry"], ticker) if tv.get("industry") else []
    peer_series = []
    for pe, pt in peers:
        try:
            peer_series.append(returns(history(yahoo_symbol(pe, pt), start, end)))
        except Exception:
            continue
    r_p = {d: float(np.mean([s[d] for s in peer_series if d in s]))
           for d in dates if sum(d in s for s in peer_series) >= max(3, len(peer_series) // 2)}

    est_dates = [d for d in dates[max(0, i0 - EST_GAP - EST_LEN):max(0, i0 - EST_GAP)]
                 if d in r_s and d in r_m and d in r_p and abs(r_s[d]) < 0.10]
    y = np.array([r_s[d] for d in est_dates])
    X = np.column_stack([np.ones(len(est_dates)), [r_m[d] for d in est_dates], [r_p[d] for d in est_dates]])
    short = len(est_dates) < MIN_OBS
    ret0, m0, p0 = r_s.get(d0), r_m.get(d0), r_p.get(d0)

    if short:
        flags.append(f"short price history ({len(est_dates)} usable days); abnormal return = stock minus peer index")
        coef, sigma = None, None
        ar = (ret0 - p0) if (ret0 is not None and p0 is not None) else None
        t = None
    else:
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ coef
        sigma = float(np.std(resid, ddof=3))
        ar = ret0 - float(coef @ [1, m0, p0]) if None not in (ret0, m0, p0) else None
        t = ar / sigma if ar is not None else None

    def car(a, b):
        ds = [dates[i] for i in range(i0 + a, i0 + b + 1) if 0 <= i < len(dates)]
        if coef is None or not ds or any(d not in r_s or d not in r_m or d not in r_p for d in ds):
            return None
        return float(sum(r_s[d] - coef @ [1, r_m[d], r_p[d]] for d in ds))

    vols = [r["volume"] for r in stock["rows"][max(0, i0 - 30):i0] if r["volume"] is not None]
    avg_vol = float(np.mean(vols)) if vols else None
    vol0 = stock["rows"][i0]["volume"]
    zero_vol = sum(1 for r in stock["rows"][max(0, i0 - 120):i0] if not r["volume"])
    if zero_vol > 12:
        flags.append(f"thin trading: {zero_vol} zero-volume days in the prior 120")
    if exch == "OTC":
        flags.append("OTC-traded" + (f"; home country {tv.get('country')}" if tv.get("country") not in (None, "United States") else ""))

    # mechanical checks
    for kind in ("dividends", "splits"):
        for ev in (stock["events"].get(kind) or {}).values():
            ev_date = dt.datetime.utcfromtimestamp(ev["date"]).date().isoformat()
            if dates[max(0, i0 - 1)] <= ev_date <= d0:
                flags.append(f"{kind[:-1]} event on {ev_date}: check the drop is not mechanical")
    raw_close_ret = stock["rows"][i0]["close"] / stock["rows"][i0 - 1]["close"] - 1
    if ret0 is not None and abs(raw_close_ret - ret0) > 0.01:
        flags.append(f"adjusted and unadjusted returns differ ({raw_close_ret:.2%} vs {ret0:.2%})")
    if tv.get("close") and d0 == dates[-1] and abs(tv["close"] / stock["rows"][i0]["close"] - 1) > 0.01:
        flags.append(f"TradingView close {tv['close']} differs from Yahoo {stock['rows'][i0]['close']:.4g} by >1%")
    if (stock.get("currency") or "").endswith("p") or stock.get("currency") == "GBp":
        flags.append("prices quoted in pence")

    cap = tv.get("market_cap_basic")
    cap_lost = cap * (-ret0) / (1 + ret0) if cap and ret0 is not None else None
    out = {
        "symbol": sym, "price_symbol": ysym, "price_source": stock.get("source"), "name": tv.get("description"), "country": tv.get("country"),
        "sector": tv.get("sector"), "industry": tv.get("industry"), "currency": stock.get("currency"),
        "day0": d0, "close": stock["rows"][i0]["close"], "prev_close": stock["rows"][i0 - 1]["close"],
        "return": ret0, "market_index": index, "market_return": m0,
        "peers": [f"{e}:{t}" for e, t in peers], "peer_return": p0,
        "alpha": None if coef is None else float(coef[0]),
        "beta_market": None if coef is None else float(coef[1]),
        "beta_peers": None if coef is None else float(coef[2]),
        "sigma": sigma, "est_days": len(est_dates),
        "expected_return": None if ar is None or ret0 is None else ret0 - ar,
        "abnormal_return": ar, "t_stat": t,
        "car_0_1": car(0, 1), "pre_drift_m5_m1": car(-5, -1), "car_1_5_rebound": car(1, 5),
        "volume": vol0, "avg_volume_30d": avg_vol,
        "volume_ratio": vol0 / avg_vol if vol0 and avg_vol else None,
        "market_cap": cap, "market_cap_lost": cap_lost,
        "flags": flags,
    }
    out["class"] = classify(ar, t if t is not None else 0, short)
    return out


def parse_screener(path):
    """Pull EXCH:TICKER symbols from the screener's markdown/plain output."""
    syms = []
    for line in open(path):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        for c in cells:
            if re.fullmatch(r"[A-Z ]+:[A-Z0-9.\-]+", c):
                syms.append(c)
    return syms


def pct(x):
    return "n/a" if x is None else f"{x:+.1%}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="*")
    ap.add_argument("--screener")
    ap.add_argument("--date", type=dt.date.fromisoformat)
    ap.add_argument("--json")
    a = ap.parse_args()
    syms = a.symbols + (parse_screener(a.screener) if a.screener else [])
    results = []
    for s in syms:
        try:
            results.append(analyse(s, a.date))
        except Exception as e:
            results.append({"symbol": s, "error": str(e)})
        time.sleep(0.5)
    if a.json:
        json.dump(results, open(a.json, "w"), indent=1, default=str)
    print("| Ticker | Day 0 | Return | Market | Peers | Abnormal | t | Class | Flags |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        if "error" in r:
            print(f"| {r['symbol']} | | | | | | | ERROR | {r['error']} |")
            continue
        t = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.1f}"
        print(f"| {r['symbol']} | {r['day0']} | {pct(r['return'])} | {pct(r['market_return'])} | "
              f"{pct(r['peer_return'])} | {pct(r['abnormal_return'])} | {t} | {r['class']} | {'; '.join(r['flags'])} |")


if __name__ == "__main__":
    main()
