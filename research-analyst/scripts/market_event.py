#!/usr/bin/env python3
"""Drop standard: is a one-day fall company-specific?

For each screener row this script measures the fall against the stock's own
normal behaviour relative to its home market index and an equal-weighted index
of same-industry peers, then classifies it (see references/drop-standard.md).

Usage:
  market_event.py EXCH:TICKER [EXCH:TICKER ...] [--date YYYY-MM-DD] [--json out.json]
  market_event.py --screener screener_output.md [--date ...] [--json ...]

Prices: TradingView chart feed (daily bars). Classification data: TradingView
scanner. Every series is cached in .cache/ so a run can be audited and reproduced.
Requires: numpy, websocket-client.
"""
import argparse, datetime as dt, json, os, random, re, string, time, urllib.request
import numpy as np
import websocket

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache")

# Screener exchange prefix -> TradingView scanner market
MARKETS = {
    "NASDAQ": "america", "NYSE": "america", "AMEX": "america", "NYSE ARCA": "america", "OTC": "america",
    "CBOE": "america",
    "TSX": "canada", "TSXV": "canada", "CSE": "canada", "NEO": "canada",
    "LSE": "uk", "LSIN": "uk", "AQUIS": "uk",
    "XETR": "germany", "FWB": "germany", "GETTEX": "germany", "TRADEGATE": "germany",
    "SWB": "germany", "HAM": "germany", "DUS": "germany", "MUN": "germany", "BER": "germany",
}
# Home market index per scanner market (TradingView symbols)
INDEX = {"america": "SP:SPX", "canada": "TSX:TSX", "uk": "FTSE:ASX", "germany": "XETR:HDAX"}

# v1 thresholds; calibrate on Andrew's past cases (references/drop-standard.md)
AR_CLEAR, AR_BORDER = -0.07, -0.05
T_CLEAR, T_BORDER = -2.58, -1.96
EST_LEN, EST_GAP, MIN_OBS, N_PEERS, BARS = 120, 10, 60, 10, 800
# Theme factors: fixed list, never chosen by outcome. Each stock gets the one it tracked most
# closely over the estimation window (if correlation >= THEME_MIN_CORR).
THEMES = {"IBIT": "Bitcoin", "XBI": "Biotech", "SMH": "Semiconductors", "IGV": "Software",
          "WCLD": "Cloud software", "ARKK": "Speculative growth", "IWM": "US small caps",
          "QTUM": "Quantum and AI computing", "BOTZ": "Robotics and AI", "TAN": "Solar",
          "LIT": "Batteries and lithium", "URA": "Uranium", "GDX": "Gold miners", "XLE": "Energy",
          "XME": "Metals and mining", "KRE": "Regional banks", "XRT": "Retail", "ITA": "Aerospace and defense"}
THEME_MIN_CORR = 0.4


# ---------- TradingView chart feed ----------

def _frame(m, p):
    s = json.dumps({"m": m, "p": p}, separators=(",", ":"))
    return f"~m~{len(s)}~m~{s}"


def _split(raw):
    out, i = [], 0
    while i < len(raw):
        m = re.match(r"~m~(\d+)~m~", raw[i:])
        if not m:
            break
        n, s = int(m.group(1)), i + m.end()
        out.append(raw[s:s + n])
        i = s + n
    return out


def _tv_bars(symbol, adjustment, n=BARS):
    ws = websocket.create_connection("wss://data.tradingview.com/socket.io/websocket",
                                     header=["Origin: https://www.tradingview.com"], timeout=20)
    cs = "cs_" + "".join(random.choices(string.ascii_lowercase, k=12))
    sym = json.dumps({"symbol": symbol, "adjustment": adjustment, "session": "regular"})
    for m, p in [("set_auth_token", ["unauthorized_user_token"]), ("chart_create_session", [cs, ""]),
                 ("resolve_symbol", [cs, "sym", "=" + sym]), ("create_series", [cs, "s1", "s1", "sym", "1D", n, ""])]:
        ws.send(_frame(m, p))
    rows, info, t0 = [], {}, time.time()
    try:
        while time.time() - t0 < 40:
            for msg in _split(ws.recv()):
                if msg.startswith("~h~"):
                    ws.send(f"~m~{len(msg)}~m~{msg}")
                    continue
                d = json.loads(msg)
                m = d.get("m")
                if m == "symbol_resolved":
                    info = d["p"][2]
                elif m in ("timescale_update", "du"):
                    rows += d["p"][1].get("s1", {}).get("s", [])
                elif m == "series_completed":
                    return info, rows
                elif m in ("symbol_error", "series_error", "critical_error", "protocol_error"):
                    raise RuntimeError(f"{symbol}: {m} {d['p'][-1]}")
    finally:
        ws.close()
    raise RuntimeError(f"{symbol}: timed out")


# Local close per exchange time zone; a bar dated today before close + 20 minutes is still in progress.
CLOSES = {"America/New_York": (16, 0), "America/Toronto": (16, 0), "Europe/London": (16, 35), "Europe/Berlin": (17, 35)}


def complete_only(h, now=None):
    """Drop today's bar if its session has not closed yet (running the script during market hours)."""
    tz = h.get("timezone")
    if not h["rows"] or tz not in CLOSES:
        return h
    from zoneinfo import ZoneInfo
    local = (now or dt.datetime.now(dt.timezone.utc)).astimezone(ZoneInfo(tz))
    hh, mm = CLOSES[tz]
    if h["rows"][-1]["date"] == local.date().isoformat() and (local.hour, local.minute) < (hh, mm + 20):
        return {**h, "rows": h["rows"][:-1], "dropped_partial": h["rows"][-1]["date"]}
    return h


def history(symbol, adjustment="dividends"):
    """Daily bars for a TradingView symbol, cached per symbol, adjustment and day (completed sessions only)."""
    return complete_only(_history(symbol, adjustment))


def _history(symbol, adjustment):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"tv_{symbol.replace(':', '_').replace(' ', '')}_{adjustment}_{BARS}_{dt.date.today()}.json")
    if os.path.exists(path):
        return json.load(open(path))
    for i in range(3):
        try:
            info, bars = _tv_bars(symbol, adjustment)
            break
        except RuntimeError:
            raise
        except Exception:
            if i == 2:
                raise
            time.sleep(3 * (i + 1))
    rows = {}
    for b in bars:
        t, o, h, l, c = b["v"][:5]
        rows[dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()] = {
            "close": c, "volume": b["v"][5] if len(b["v"]) > 5 else None}
    out = {"symbol": symbol, "source": f"TradingView chart feed ({adjustment}-adjusted)",
           "currency": info.get("currency_code"), "timezone": info.get("timezone"),
           "rows": [{"date": d, **rows[d]} for d in sorted(rows)],
           "retrieved": dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat() + "Z"}
    if complete_only(out) is out:  # an in-progress bar is never cached as if it were a close
        json.dump(out, open(path, "w"))
    return out


# ---------- TradingView scanner ----------

def _scan(market, body):
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


def tv_lookup(market, exch, ticker):
    cols = ["name", "description", "exchange", "close", "change", "market_cap_basic", "sector",
            "industry", "volume", "average_volume_30d_calc", "country", "currency", "fundamental_currency_code"]
    data = _scan(market, {"columns": cols, "range": [0, 10],
                          "filter": [{"left": "name", "operation": "equal", "right": ticker}]})
    rows = [x for x in data if x["s"] == f"{exch}:{ticker}"] or data
    return dict(zip(cols, rows[0]["d"])) if rows else {}


def tv_peers(market, industry, symbol, n=N_PEERS, field="industry"):
    """Largest same-industry (or same-sector) primary listings in the same market (no OTC), excluding the stock itself."""
    data = _scan(market, {"columns": ["name", "market_cap_basic"], "range": [0, n + 5],
                          "filter": [{"left": field, "operation": "equal", "right": industry},
                                     {"left": "type", "operation": "equal", "right": "stock"},
                                     {"left": "is_primary", "operation": "equal", "right": True},
                                     {"left": "exchange", "operation": "not_in_range", "right": ["OTC"]}],
                          "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}})
    return [x["s"] for x in data if x["s"] != symbol][:n]


# ---------- analysis ----------

def returns(hist):
    rows = hist["rows"]
    return {rows[i]["date"]: rows[i]["close"] / rows[i - 1]["close"] - 1
            for i in range(1, len(rows)) if rows[i]["close"] and rows[i - 1]["close"]}


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


def analyse(symbol, day0=None):
    exch, ticker = symbol.split(":", 1)
    market = MARKETS.get(exch)
    if not market:
        return {"symbol": symbol, "error": f"exchange {exch} not mapped"}
    flags = []
    stock = history(symbol)
    raw = history(symbol, "splits")
    index_hist = history(INDEX[market])
    mkt_dates = [r["date"] for r in index_hist["rows"]]
    d0 = day0.isoformat() if day0 else stock["rows"][-1]["date"]
    dates = [r["date"] for r in stock["rows"]]
    if d0 not in dates:
        return {"symbol": symbol, "error": f"no trade on {d0}"}
    i0 = dates.index(d0)

    tv = tv_lookup(market, exch, ticker)
    r_s, r_m = returns(stock), returns(index_hist)
    peers = tv_peers(market, tv["industry"], symbol) if tv.get("industry") else []
    peer_basis = f"industry: {tv.get('industry')}"
    if len(peers) < 3 and tv.get("sector"):
        flags.append(f"peer index from sector {tv['sector']}: industry {tv.get('industry')} has {len(peers)} other listings in this market")
        peers, peer_basis = tv_peers(market, tv["sector"], symbol, field="sector"), f"sector: {tv['sector']}"
    peer_series = []
    for p in peers:
        try:
            peer_series.append(returns(history(p)))
        except Exception:
            continue
    r_p = {d: float(np.mean([s[d] for s in peer_series if d in s])) for d in mkt_dates
           if peer_series and sum(d in s for s in peer_series) >= max(3, len(peer_series) // 2)}

    # Trading-day calendar comes from the market index, so missing stock bars show up as gaps.
    if d0 not in mkt_dates:
        return {"symbol": symbol, "error": f"{d0} is not a session of {INDEX[market]} in the chart feed"}
    m0 = mkt_dates.index(d0)
    window = mkt_dates[max(0, m0 - EST_GAP - EST_LEN):max(0, m0 - EST_GAP)]
    traded = [d for d in window if d in r_s]
    if len(traded) < 0.8 * len(window):
        flags.append(f"thin trading: stock traded on {len(traded)} of the {len(window)} sessions in the estimation window")
    factors = {"market": r_m}
    if r_p:
        factors["peers"] = r_p
    else:
        flags.append(f"no peer index: {len(peer_series)} same-industry series with price history (3 needed); expected return uses market and theme only")
    est = [d for d in traded if all(d in f for f in factors.values()) and abs(r_s[d]) < 0.10]
    ret0, mret0, pret0 = r_s.get(d0), r_m.get(d0), r_p.get(d0)

    # theme factor: the fixed-list ETF the stock tracked most closely before the event
    theme = theme_corr = tret0 = None
    best = (THEME_MIN_CORR, None)
    for tk in THEMES:
        try:
            tr = returns(history(tk))
        except Exception:
            continue
        common = [d for d in est if d in tr]
        if len(common) >= MIN_OBS and d0 in tr:
            c = float(np.corrcoef([r_s[d] for d in common], [tr[d] for d in common])[0, 1])
            if c >= best[0]:
                best = (c, (tk, tr))
    if best[1]:
        theme, tr = best[1]
        theme_corr, tret0 = best[0], tr[d0]
        factors["theme"] = tr
        est = [d for d in est if d in tr]
    short = len(est) < MIN_OBS
    names = list(factors)

    def xrow(d):
        return [1.0] + [factors[k][d] for k in names]

    def beta(k):
        return None if coef is None or k not in names else float(coef[1 + names.index(k)])

    coef = sigma = t = None
    if short:
        flags.append(f"short or sparse price history ({len(est)} usable days): abnormal return = stock minus peer index, no t-statistic")
        base = pret0 if pret0 is not None else mret0
        ar = ret0 - base if (ret0 is not None and base is not None) else None
    else:
        y = np.array([r_s[d] for d in est])
        X = np.array([xrow(d) for d in est])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        sigma = float(np.std(y - X @ coef, ddof=X.shape[1]))
        ar = ret0 - float(coef @ xrow(d0)) if ret0 is not None and all(d0 in f for f in factors.values()) else None
        t = ar / sigma if ar is not None else None

    def car(a, b):
        if coef is None or m0 + a < 0 or m0 + b >= len(mkt_dates):
            return None  # window not complete yet (or before the data): never sum part of it
        ds = mkt_dates[m0 + a:m0 + b + 1]
        if not ds or any(d not in r_s or any(d not in f for f in factors.values()) for d in ds):
            return None
        return float(sum(r_s[d] - coef @ xrow(d) for d in ds))

    vols = [r["volume"] for r in stock["rows"][max(0, i0 - 30):i0] if r["volume"]]
    avg_vol = float(np.mean(vols)) if vols else None
    vol0 = stock["rows"][i0]["volume"]
    dollar_vol0 = (vol0 or 0) * stock["rows"][i0]["close"]
    if exch == "OTC" and dollar_vol0 < 100_000:
        flags.append(f"thin trading: day-0 dollar volume about {dollar_vol0:,.0f} {stock.get('currency') or ''}".rstrip())
    if exch == "OTC":
        home = tv.get("country")
        flags.append("OTC-traded" + (f"; company based in {home}" if home and home != "United States" else ""))

    # mechanical checks: dividend adjustment and price-feed consistency
    raw_rows = {r["date"]: r["close"] for r in raw["rows"]}
    raw_dates = sorted(raw_rows)
    if d0 in raw_rows and raw_dates.index(d0) > 0:
        raw_ret = raw_rows[d0] / raw_rows[raw_dates[raw_dates.index(d0) - 1]] - 1
        if ret0 is not None and abs(raw_ret - ret0) > 0.005:
            flags.append(f"dividend effect: unadjusted {raw_ret:.1%} vs dividend-adjusted {ret0:.1%}")
    # the scanner's change is for its latest session; skip the comparison while today's session is still open
    if tv.get("change") is not None and ret0 is not None and d0 == dates[-1] and not stock.get("dropped_partial") \
            and abs(tv["change"] / 100 - ret0) > 0.01:
        flags.append(f"scanner change {tv['change']:.1f}% differs from chart-feed return {ret0:.1%}")
    if stock.get("currency") == "GBX":
        flags.append("prices in pence (GBX)")

    # Market value lost: scanner market cap is at the scanner's latest close, so convert it to a share
    # count with that close and price the day-0 move on the split-adjusted (unadjusted for dividends) series.
    cap, tv_close = tv.get("market_cap_basic"), tv.get("close")
    raw_prev = raw_rows.get(raw_dates[raw_dates.index(d0) - 1]) if d0 in raw_rows and raw_dates.index(d0) > 0 else None
    cap_lost = cap_basis = None
    if cap and tv_close and raw_prev and d0 in raw_rows:
        cap_lost, cap_basis = cap * (raw_prev - raw_rows[d0]) / tv_close, "scanner market cap / scanner close x day-0 price change"
        if raw_dates and abs(raw_rows[raw_dates[-1]] / tv_close - 1) > 0.02:
            flags.append(f"scanner close {tv_close} differs from chart-feed latest close {raw_rows[raw_dates[-1]]}: check market value lost")
    elif cap and ret0 is not None:
        cap_lost, cap_basis = cap * (-ret0) / (1 + ret0), "scanner market cap treated as day-0 close (approximate)"
    out = {
        "symbol": symbol, "name": tv.get("description"), "country": tv.get("country"),
        "sector": tv.get("sector"), "industry": tv.get("industry"), "currency": stock.get("currency"),
        "price_source": stock["source"], "day0": d0,
        "close": stock["rows"][i0]["close"], "prev_close": stock["rows"][i0 - 1]["close"] if i0 else None,
        "return": ret0, "market_index": INDEX[market], "market_return": mret0,
        "peers": peers, "peer_basis": peer_basis, "peers_used": len(peer_series), "peer_return": pret0,
        "alpha": None if coef is None else float(coef[0]),
        "beta_market": beta("market"), "beta_peers": beta("peers"),
        "theme_etf": theme, "theme": THEMES.get(theme), "theme_corr": theme_corr, "theme_return": tret0,
        "beta_theme": beta("theme"),
        "sigma": sigma, "est_days": len(est),
        "expected_return": None if ar is None else ret0 - ar,
        "abnormal_return": ar, "t_stat": t,
        "ar_m1": car(-1, -1), "ar_p1": car(1, 1),
        "car_0_1": car(0, 1), "pre_drift_m5_m1": car(-5, -1), "car_1_5_rebound": car(1, 5),
        "volume": vol0, "avg_volume_30d": avg_vol,
        "volume_ratio": vol0 / avg_vol if vol0 and avg_vol else None,
        "market_cap": cap, "market_cap_currency": tv.get("fundamental_currency_code") or ("GBP" if stock.get("currency") == "GBX" else stock.get("currency")),
        "market_cap_lost": cap_lost, "market_cap_lost_basis": cap_basis,
        "flags": flags,
        "class": classify(ar, t if t is not None else 0, short),
    }
    return out


def cluster_check(results, min_corr=0.5, min_days=60):
    """Context only: which other screened stocks normally move with this one.

    Every screened stock fell 10%+, so this group is selected on the outcome and must not be used to
    explain the fall (it always would). The theme factor in analyse() does that job without bias.
    This list helps the reader spot shared news (e.g. several bitcoin miners on one screen).
    """
    ok = [r for r in results if "error" not in r]
    series = {r["symbol"]: returns(history(r["symbol"])) for r in ok}
    for r in ok:
        mine, d0 = series[r["symbol"]], r["day0"]
        days = sorted(d for d in mine if d < d0)[-(EST_LEN + EST_GAP):-EST_GAP]
        group = []
        for o in ok:
            if o is r or o["day0"] != d0:
                continue
            common = [d for d in days if d in series[o["symbol"]]]
            if len(common) < min_days:
                continue
            c = float(np.corrcoef([mine[d] for d in common], [series[o["symbol"]][d] for d in common])[0, 1])
            if c >= min_corr:
                group.append((o["symbol"], c, o["return"]))
        r["correlated_group"] = [f"{s} (corr {c:.2f}, {x:+.1%})" for s, c, x in sorted(group, key=lambda g: -g[1])]
        if len(group) >= 2:
            r["flags"].append(f"{len(group)} other screened stocks that usually move with it also fell (context only)")
    return results


def lookback(symbol, day0, days, out_json=None):
    """Stage 1: every session in the lookback where the stock fell 5%+, run through the drop standard."""
    start = (day0 - dt.timedelta(days=days)).isoformat()
    r = returns(history(symbol))
    cands = [d for d, x in sorted(r.items()) if start <= d < day0.isoformat() and x <= -0.05]
    res = []
    for d in cands:
        try:
            res.append(analyse(symbol, dt.date.fromisoformat(d)))
        except Exception as e:
            res.append({"symbol": symbol, "day0": d, "error": str(e)[:200]})
    if out_json:
        json.dump(res, open(out_json, "w"), indent=1, default=str)
    print(f"{len(cands)} sessions with a fall of 5%+ between {start} and {day0}")
    print("| Date | Return | Abnormal | t | Class |")
    print("|---|---|---|---|---|")
    for x in res:
        if "error" in x:
            print(f"| {x['day0']} | | | | ERROR {x['error']} |")
        else:
            t = "n/a" if x["t_stat"] is None else f"{x['t_stat']:.1f}"
            print(f"| {x['day0']} | {pct(x['return'])} | {pct(x['abnormal_return'])} | {t} | {x['class']} |")
    return res


def parse_screener(path):
    """Pull EXCH:TICKER symbols from the screener's markdown/plain output."""
    syms = []
    for line in open(path):
        for c in (c.strip() for c in line.strip().strip("|").split("|")):
            if re.fullmatch(r"[A-Z ]+:[A-Z0-9.\-]+", c):
                syms.append(c)
    return syms


def theme_cell(r):
    return "none" if not r.get("theme_etf") else f"{r['theme_etf']} {pct(r['theme_return'])} (corr {r['theme_corr']:.2f})"


def pct(x):
    return "n/a" if x is None else f"{x:+.1%}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="*")
    ap.add_argument("--screener")
    ap.add_argument("--date", type=dt.date.fromisoformat)
    ap.add_argument("--json")
    ap.add_argument("--lookback", type=int, metavar="DAYS",
                    help="also scan this many calendar days before --date for other drops of 5%%+ (stage 1)")
    a = ap.parse_args()
    if a.lookback:
        if not a.date or len(a.symbols) != 1:
            ap.error("--lookback needs exactly one symbol and --date")
        return lookback(a.symbols[0], a.date, a.lookback, a.json)
    syms = a.symbols + (parse_screener(a.screener) if a.screener else [])
    results = []
    for s in syms:
        try:
            results.append(analyse(s, a.date))
        except Exception as e:
            results.append({"symbol": s, "error": str(e)[:200]})
    if len(results) > 2:
        cluster_check(results)
    if a.json:
        json.dump(results, open(a.json, "w"), indent=1, default=str)
    print("| Ticker | Day 0 | Return | Market | Peers | Theme | Abnormal | t | Class | Flags |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        if "error" in r:
            print(f"| {r['symbol']} | | | | | | | | ERROR | {r['error']} |")
            continue
        t = "n/a" if r["t_stat"] is None else f"{r['t_stat']:.1f}"
        print(f"| {r['symbol']} | {r['day0']} | {pct(r['return'])} | {pct(r['market_return'])} | "
              f"{pct(r['peer_return'])} | {theme_cell(r)} | {pct(r['abnormal_return'])} | {t} | {r['class']} | {'; '.join(r['flags'])} |")


if __name__ == "__main__":
    main()
