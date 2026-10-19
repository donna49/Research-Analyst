#!/usr/bin/env python3
"""Andrew's step 7: daily close and volume from one year plus 30 days before the drop through the drop day.

  price_history.py EXCH:TICKER YYYY-MM-DD [--out runs/<date>/<TICKER>/price_history.csv]

Prices are split-adjusted, not dividend-adjusted (the quoted market prices). Each row also carries
the day's percentage change and its volume as a multiple of the prior 30-session average, so that
the drop and any earlier storm warnings stand out. Uses the TradingView chart feed via market_event.history().
"""
import argparse, csv, datetime as dt, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_event  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol")
    ap.add_argument("date", type=dt.date.fromisoformat)
    ap.add_argument("--out")
    a = ap.parse_args()
    start = a.date - dt.timedelta(days=365 + 30)
    market_event.ensure_history_for(start - dt.timedelta(days=60))
    h = market_event.history(a.symbol, "splits")
    rows = [r for r in h["rows"] if r["close"]]
    out = a.out or f"price_history_{a.symbol.replace(':', '_')}_{a.date}.csv"
    n, big = 0, []
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "close", "volume", "change_pct", "volume_x_30d_avg"])
        for i, r in enumerate(rows):
            if not (start.isoformat() <= r["date"] <= a.date.isoformat()):
                continue
            prev = rows[i - 1]["close"] if i else None
            ch = (r["close"] / prev - 1) if prev else None
            vols = [x["volume"] for x in rows[max(0, i - 30):i] if x["volume"]]
            vx = (r["volume"] / (sum(vols) / len(vols))) if vols and r["volume"] else None
            w.writerow([r["date"], r["close"], r["volume"], "" if ch is None else f"{ch:.4f}", "" if vx is None else f"{vx:.2f}"])
            n += 1
            if ch is not None and ch <= -0.10:
                big.append((r["date"], ch, vx))
    print(f"wrote {out}: {n} sessions {start} to {a.date} ({h['source']}, {h.get('currency')})")
    for d, ch, vx in big:
        print(f"  fall of 10%+ on {d}: {ch:+.1%}" + (f", volume {vx:.1f}x" if vx else ""))


if __name__ == "__main__":
    main()
