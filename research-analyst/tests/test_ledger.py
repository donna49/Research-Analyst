"""Offline tests for scripts/ledger.py on a small synthetic case.

  python3 -m unittest discover tests
"""
import json, os, shutil, sys, tempfile, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import ledger

SRC = {"title": "Form 10-Q", "publisher": "Issuer", "doc_type": "10-Q", "url": "https://www.sec.gov/x", "doc_id": "ACC1",
       "location": "Item 2", "tier": 1, "retrieved_at": "2026-10-19T10:00:00Z"}
SCRIPT = {"title": "market_event.py output", "publisher": "research-analyst", "doc_type": "script output",
          "url": "runs/d/T/market_event.json", "location": "$[0].abnormal_return", "tier": 1, "retrieved_at": "2026-10-19T10:00:00Z"}
GOOD = [
    {"id": "E001", "stage": "market-event", "kind": "market", "status": "fact", "claim": "Abnormal return", "metric": "Abnormal return",
     "value": -0.1276, "unit": "fraction", "event_at": "2026-10-16", "source": SCRIPT},
    {"id": "E002", "stage": "statement", "kind": "statement", "status": "fact", "claim": "Q2 call reaffirmed the outlook.",
     "quote": "We remain confident in our full year outlook", "statement_type": "reassurance", "speaker": "CFO",
     "public_at": "2026-08-06T16:30:00-04:00", "source": SRC},
    {"id": "E003", "stage": "trigger", "kind": "revelation", "status": "fact", "claim": "Outlook cut before the open.",
     "quote": "Updates Fiscal 2026 Outlook", "public_at": "2026-10-16T08:20:06-04:00", "source": {**SRC, "doc_id": "ACC2"}},
    {"id": "E004", "stage": "comparison", "kind": "comparison", "status": "inference", "claim": "The reassurance appears inconsistent with the cut.",
     "statement_id": "E002", "revelation_ids": ["E003"], "apparent_inconsistency": "x", "innocent_explanation": "y",
     "confidence": "low - knowledge timing unknown", "refs": ["E002", "E003"]},
    {"id": "E005", "stage": "trigger", "kind": "gap", "status": "gap", "claim": "Release time not retrieved.", "would_be_settled_by": "wire page"},
]


class Case(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "sources"))
        open(os.path.join(self.d, "sources", "ACC1.txt"), "w").write("…we remain   confident in our full-year outlook… no wait: We remain confident in our full year outlook.")
        open(os.path.join(self.d, "sources", "ACC2.txt"), "w").write("Preliminary results; Updates Fiscal 2026 Outlook for divestiture")
        self.path = os.path.join(self.d, "ledger.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, recs):
        with open(self.path, "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")

    def errs(self, recs, fn=ledger.check):
        self.write(recs)
        return fn(self.path)[1]

    def mutate(self, i, **kw):
        recs = json.loads(json.dumps(GOOD))
        recs[i].update(kw)
        return self.errs(recs)

    def test_good_passes(self):
        self.assertEqual(self.errs(GOOD), [])
        self.assertEqual(self.errs(GOOD, ledger.quotes), [])

    def test_structure_errors(self):
        cases = [
            (1, {"quote": ""}, "without verbatim quote"),
            (1, {"statement_type": "boast"}, "statement_type"),
            (1, {"public_at": "2026-08-06T16:30:00"}, "without time zone"),
            (1, {"public_at": "Aug 6"}, "not ISO"),
            (1, {"quote": "word " * 121}, "longer than"),
            (3, {"statement_id": "E003"}, "is a revelation record"),
            (3, {"statement_id": "E999"}, "unknown id"),
            (3, {"confidence": "fairly sure"}, "confidence"),
            (0, {"value": "-12.8%"}, "must be a number"),
            (2, {"claim": "The company misled investors."}, "conclusory"),
            (4, {"would_be_settled_by": ""}, "would_be_settled_by"),
            (1, {"source": {**SRC, "tier": 4}}, "tier"),
        ]
        for i, kw, msg in cases:
            with self.subTest(msg=msg):
                self.assertTrue(any(msg in e for e in self.mutate(i, **kw)), self.mutate(i, **kw))

    def test_supersede(self):
        recs = json.loads(json.dumps(GOOD))
        recs[1]["verified"] = "failed: quote not in source"
        self.assertTrue(any("not superseded" in e for e in self.errs(recs)))
        recs.append({**GOOD[1], "id": "E006", "supersedes": "E002"})
        recs[3]["statement_id"] = "E006"
        self.assertEqual(self.errs(recs), [])
        recs.append({**GOOD[4], "id": "E007", "supersedes": "E099"})
        self.assertTrue(any("supersedes unknown" in e for e in self.errs(recs)))

    def test_quote_mismatch_and_ellipsis(self):
        self.write([{**GOOD[1], "quote": "We remain confident ... full year outlook"}])
        self.assertEqual(ledger.quotes(self.path)[1], [])
        self.write([{**GOOD[1], "quote": "We remain very confident in our full year outlook"}])
        self.assertTrue(ledger.quotes(self.path)[1])

    def test_renderings(self):
        self.write(GOOD)
        tl = ledger.timeline(self.path)[1]
        self.assertTrue(tl[2].startswith("| 2026-08-06 16:30 -04:00"))
        self.assertTrue(any("Abnormal return -12.8%" in x for x in tl))
        self.assertEqual(len(ledger.sources(self.path)[1]), 3)
        self.assertTrue(any("E005" in x for x in ledger.summary(self.path)[1]))

    def test_memo_gate(self):
        self.write(GOOD)
        memo = os.path.join(self.d, "memo.md")

        def run(text):
            open(memo, "w").write(text)
            return ledger.memo(self.path, memo)[1]

        self.assertEqual(run("# Memo\n\nThe stock fell with an abnormal return of -12.8% [E001].\n\n"
                             "The CFO said \"we are clearly on track\" [E002].\n\n## Sources\n[E001] x 50%\n"), [])
        self.assertTrue(any("no record citation" in e for e in run("Abnormal return was -12.8%.\n")))
        self.assertTrue(any("does not match" in e for e in run("Abnormal return was -14.2% [E001].\n")))
        self.assertTrue(any("unknown record" in e for e in run("See [E042].\n")))
        self.assertTrue(any("conclusory" in e for e in run("This is clearly a problem [E004].\n")))
        self.assertTrue(any("no record citation" in e for e in run("Value lost was $103 million.\n")))


class AddMarket(unittest.TestCase):
    def test_add_market_idempotent(self):
        d = tempfile.mkdtemp()
        try:
            case = os.path.join(d, "runs", "2026-10-16", "T")
            os.makedirs(case)
            me = os.path.join(case, "market_event.json")
            json.dump([{"symbol": "NASDAQ:T", "day0": "2026-10-16", "currency": "USD", "market_index": "SP:SPX",
                        "close": 16.04, "return": -0.133, "abnormal_return": -0.128, "t_stat": -5.7, "car_0_1": None,
                        "class": "Company-specific", "flags": ["OTC-traded"]}], open(me, "w"))
            path = os.path.join(case, "ledger.jsonl")
            ledger.add_market(path, me)
            n = len(ledger.load(path))
            self.assertEqual(n, 6)  # close, return, abnormal, t, class, one flag
            ledger.add_market(path, me)
            self.assertEqual(len(ledger.load(path)), n)
            self.assertEqual(ledger.check(path)[1], [])
            self.assertEqual(ledger.load(path)[0]["source"]["url"], "runs/2026-10-16/T/market_event.json")
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
