"""Offline tests for scripts/market_event.py on synthetic price series (no network).

  python3 -m unittest discover tests
"""
import datetime as dt, os, sys, unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import market_event as me

N = 300


def sessions(n=N, end="2026-10-16"):
    out, d = [], dt.date.fromisoformat(end)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d -= dt.timedelta(days=1)
    return out[::-1]


def series(rets, dates, start=100.0, volume=1e6, missing=()):
    rows, p = [], start
    for d, r in zip(dates, rets):
        p *= 1 + r
        if d not in missing:
            rows.append({"date": d, "close": p, "volume": volume})
    return {"symbol": "X", "source": "synthetic", "currency": "USD", "timezone": "America/New_York", "rows": rows}


class Fake:
    """Patches the network functions with synthetic data for one stock."""

    def __init__(self, drop=-0.15, peers=True, n=N, missing=(), raw_drop=None, cap=1e9, theme_corr=False):
        rng = np.random.default_rng(1)
        self.dates = sessions()
        m = rng.normal(0, 0.01, N)
        p = m + rng.normal(0, 0.008, N)
        s = 0.8 * m + 0.5 * p + rng.normal(0, 0.015, N)
        s[-1] = drop
        d = self.dates
        live = set(d[-n:])
        miss = set(missing) | {x for x in d if x not in live}
        self.h = {("NASDAQ:TEST", "dividends"): series(s, d, missing=miss),
                  ("SP:SPX", "dividends"): series(m, d)}
        raw = s.copy()
        if raw_drop is not None:
            raw[-1] = raw_drop
        self.h[("NASDAQ:TEST", "splits")] = series(raw, d, missing=miss)
        self.peers = [f"NASDAQ:P{i}" for i in range(5)] if peers else []
        for i, sym in enumerate(self.peers):
            self.h[(sym, "dividends")] = series(p + rng.normal(0, 0.002, N), d)
        last = self.h[("NASDAQ:TEST", "splits")]["rows"][-1]["close"]
        self.tv = {"description": "Test Co", "country": "United States", "industry": "Widgets" if peers else None,
                   "close": last, "change": drop * 100, "market_cap_basic": cap}

    def __enter__(self):
        self.saved = me.history, me.tv_lookup, me.tv_peers
        me.history = lambda sym, adj="dividends": self._get(sym, adj)
        me.tv_lookup = lambda market, exch, ticker: self.tv
        me.tv_peers = lambda market, industry, symbol, n=10, field="industry": self.peers
        return self

    def _get(self, sym, adj):
        if (sym, adj) not in self.h:
            raise RuntimeError(f"{sym}: no data")
        return self.h[(sym, adj)]

    def __exit__(self, *a):
        me.history, me.tv_lookup, me.tv_peers = self.saved


class Classify(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(me.classify(-0.08, -3.0, False), "Company-specific")
        self.assertEqual(me.classify(-0.08, -2.0, False), "Borderline")
        self.assertEqual(me.classify(-0.06, -5.0, False), "Borderline")
        self.assertEqual(me.classify(-0.04, -5.0, False), "Not company-specific")
        self.assertEqual(me.classify(-0.06, 0, True), "Borderline (short history)")
        self.assertEqual(me.classify(None, None, False), "Insufficient data")


class Calibrate(unittest.TestCase):
    def test_flagged_respects_thresholds(self):
        import calibrate
        r = {"abnormal_return": -0.06, "t_stat": -2.2}
        self.assertTrue(calibrate.flagged(r, -0.05, -1.96))
        self.assertFalse(calibrate.flagged(r, -0.07, -1.96))
        self.assertFalse(calibrate.flagged(r, -0.05, -2.58))
        self.assertTrue(calibrate.flagged({"abnormal_return": -0.06, "t_stat": None}, -0.05, -3.0))
        self.assertIsNone(calibrate.flagged({"error": "x"}, -0.05, -1.96))


class Analyse(unittest.TestCase):
    def run_one(self, **kw):
        with Fake(**kw) as f:
            return me.analyse("NASDAQ:TEST", dt.date.fromisoformat(f.dates[-1]))

    def test_company_specific(self):
        r = self.run_one()
        self.assertEqual(r["class"], "Company-specific")
        self.assertAlmostEqual(r["return"], -0.15, places=9)
        self.assertLess(r["t_stat"], -2.58)
        self.assertIsNotNone(r["beta_peers"])
        self.assertAlmostEqual(r["expected_return"] + r["abnormal_return"], r["return"], places=12)

    def test_no_peers_is_not_short_history(self):
        r = self.run_one(peers=False)
        self.assertEqual(r["class"], "Company-specific")
        self.assertIsNotNone(r["t_stat"])
        self.assertIsNone(r["beta_peers"])
        self.assertTrue(any(f.startswith("no peer index") for f in r["flags"]))
        self.assertFalse(any(f.startswith("short") for f in r["flags"]))

    def test_short_history(self):
        r = self.run_one(n=40)
        self.assertEqual(r["class"], "Borderline (short history)")
        self.assertIsNone(r["t_stat"])

    def test_small_move_not_company_specific(self):
        self.assertEqual(self.run_one(drop=-0.01)["class"], "Not company-specific")

    def test_thin_trading_flag(self):
        d = sessions()
        r = self.run_one(missing=set(d[-120:-20:2]))
        self.assertTrue(any(f.startswith("thin trading") for f in r["flags"]))

    def test_dividend_flag(self):
        r = self.run_one(raw_drop=-0.18)
        self.assertTrue(any(f.startswith("dividend effect") for f in r["flags"]))

    def test_market_value_lost_uses_share_count(self):
        r = self.run_one(cap=1e9)
        # scanner close == day-0 close here, so shares = cap / close and loss = shares * (prev - close)
        self.assertAlmostEqual(r["market_cap_lost"], 1e9 * 0.15 / 0.85, delta=1)

    def test_gbx_market_cap_currency(self):
        with Fake() as f:
            for h in f.h.values():
                h["currency"] = "GBX"
            r = me.analyse("NASDAQ:TEST", dt.date.fromisoformat(f.dates[-1]))
        self.assertEqual(r["market_cap_currency"], "GBP")
        self.assertIn("prices in pence (GBX)", r["flags"])

    def test_day0_not_a_session(self):
        with Fake() as f:
            f.h[("SP:SPX", "dividends")]["rows"].pop()
            r = me.analyse("NASDAQ:TEST", dt.date.fromisoformat(f.dates[-1]))
        self.assertIn("error", r)

    def test_unmapped_exchange(self):
        self.assertIn("error", me.analyse("TSE:7203"))

    def test_event_windows_not_truncated(self):
        r = self.run_one()  # day 0 is the last bar: day +1 does not exist yet
        self.assertIsNone(r["car_0_1"])
        self.assertIsNone(r["car_1_5_rebound"])
        self.assertIsNone(r["ar_p1"])
        self.assertIsNotNone(r["pre_drift_m5_m1"])
        self.assertIsNotNone(r["ar_m1"])


class PartialBar(unittest.TestCase):
    def h(self, last):
        return {"timezone": "America/New_York", "rows": [{"date": "2026-10-16", "close": 1}, {"date": last, "close": 2}]}

    def test_drops_in_progress_bar(self):
        now = dt.datetime(2026, 10, 19, 17, 0, tzinfo=dt.timezone.utc)  # 13:00 New York
        self.assertEqual(me.complete_only(self.h("2026-10-19"), now)["rows"][-1]["date"], "2026-10-16")

    def test_keeps_closed_bar(self):
        now = dt.datetime(2026, 10, 19, 21, 0, tzinfo=dt.timezone.utc)  # 17:00 New York
        h = self.h("2026-10-19")
        self.assertIs(me.complete_only(h, now), h)

    def test_keeps_previous_day(self):
        now = dt.datetime(2026, 10, 19, 14, 0, tzinfo=dt.timezone.utc)
        h = self.h("2026-10-16")
        self.assertIs(me.complete_only(h, now), h)


class Screener(unittest.TestCase):
    def test_parse(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
            t.write("| Symbol | Chg |\n|---|---|\n| NASDAQ:FOXF | -13% |\n| NYSE:BRK.B | -10% |\n| LSE:BP. | x |\n")
        try:
            self.assertEqual(me.parse_screener(t.name), ["NASDAQ:FOXF", "NYSE:BRK.B", "LSE:BP."])
        finally:
            os.unlink(t.name)


if __name__ == "__main__":
    unittest.main()
