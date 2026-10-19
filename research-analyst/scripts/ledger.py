#!/usr/bin/env python3
"""Checks and renderings for a case ledger (references/evidence-ledger.md).

  ledger.py check    <ledger.jsonl>             # structure, references, dates, wording
  ledger.py quotes   <ledger.jsonl>             # quote match against saved sources/
  ledger.py summary  <ledger.jsonl>             # counts, open gaps, unverified records
  ledger.py timeline <ledger.jsonl>             # stage 8 chronology table (Markdown)
  ledger.py sources  <ledger.jsonl>             # memo Sources list (Markdown)
  ledger.py memo     <ledger.jsonl> <memo.md>   # stage 10 gate: citations, wording, figures
  ledger.py add-market <ledger.jsonl> <market_event.json> [EXCH:TICKER]   # stage 1 records

`check` catches broken records; it cannot decide whether evidence is true or whether a citation
supports a claim. `quotes` exact-matches every quote against the saved text in sources/<id>*.txt
(whitespace and typographic quotes normalized). `memo` checks that every cited id exists and is
live, that no conclusory wording appears outside quotations, that every line stating a percentage
or money figure cites a record, and that percentages cited to `market` records match them.
Superseded records (named in another record's `supersedes`) are left out of every rendering.
Exit code 1 on any problem.
"""
import datetime as dt, glob, json, os, re, sys
from collections import Counter

STAGES = {"market-event", "trigger", "issue", "statement", "comparison", "knowledge", "external", "timeline", "verify"}
KINDS = {"market", "revelation", "statement", "comparison", "knowledge", "external", "event", "alternative",
         "gap", "search", "issue"}
STATUSES = {"fact", "attributed", "inference", "assumption", "estimate", "gap"}
STATEMENT_TYPES = {"fact", "forward-looking", "opinion", "risk-hypothetical", "reassurance", "omission", "puffery"}
LEVELS = ("high", "moderate", "low")
WEIGHTS = ("primary", "contributing", "unlikely")
DIRECTIONS = {"supports", "undercuts"}
BANNED = re.compile(r"\b(fraud\w*|lied|lying|deceiv\w*|scheme|misled|liable|clearly|obviously|undeniabl\w*|"
                    r"actionable|viable claim|strong case)\b", re.I)
DATE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
CITE = re.compile(r"\[([A-Z][A-Z0-9]*-?\d+)\]")
MAX_QUOTE_WORDS = 120


def load(path):
    recs = []
    for n, line in enumerate(open(path), 1):
        if line.strip():
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError as e:
                recs.append({"_error": f"line {n}: invalid JSON ({e})"})
    return recs


def superseded(recs):
    return {r["supersedes"] for r in recs if r.get("supersedes")}


def live(recs):
    gone = superseded(recs)
    return [r for r in recs if "_error" not in r and r.get("id") not in gone]


def bad_time(v):
    """None if v is a date (YYYY, YYYY-MM, YYYY-MM-DD) or an ISO timestamp with a time zone."""
    if DATE.match(v):
        return None
    try:
        t = dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return "not ISO 8601"
    return None if t.tzinfo else "timestamp without time zone"


def when(r):
    """Sort key and display string for a record's date."""
    v = r.get("public_at") or r.get("event_at")
    if not v:
        return None, None
    if DATE.match(v):
        return v, v
    t = dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
    return t.astimezone(dt.timezone.utc).isoformat(), t.strftime("%Y-%m-%d %H:%M ") + (t.strftime("%z")[:3] + ":" + t.strftime("%z")[3:])


def check(path):
    recs, errs = load(path), []
    ids = {}
    for r in recs:
        if "_error" in r:
            errs.append(r["_error"])
            continue
        rid = r.get("id", "?")
        if rid in ids:
            errs.append(f"{rid}: duplicate id")
        ids[rid] = r
        kind, status = r.get("kind"), r.get("status")
        for f in ("id", "stage", "kind", "claim", "status"):
            if not r.get(f):
                errs.append(f"{rid}: missing {f}")
        if r.get("stage") and r["stage"] not in STAGES:
            errs.append(f"{rid}: unknown stage {r['stage']}")
        if kind and kind not in KINDS:
            errs.append(f"{rid}: unknown kind {kind}")
        if status and status not in STATUSES:
            errs.append(f"{rid}: unknown status {status}")
        if status not in ("inference", "gap") and kind not in ("search", "issue") and not r.get("source"):
            errs.append(f"{rid}: {status} record has no source")
        src = r.get("source") or {}
        if src and src.get("doc_type") != "script output":
            for f in ("title", "url", "tier", "retrieved_at"):
                if not src.get(f):
                    errs.append(f"{rid}: source missing {f}")
        if src.get("tier") is not None and src["tier"] not in (1, 2, 3):
            errs.append(f"{rid}: source tier must be 1, 2 or 3")
        for f in ("public_at", "event_at"):
            if r.get(f) and bad_time(r[f]):
                errs.append(f"{rid}: {f} {r[f]!r} is {bad_time(r[f])} (use YYYY-MM-DD or a timestamp with offset)")
        if kind in ("statement", "revelation") and not r.get("quote"):
            errs.append(f"{rid}: {kind} without verbatim quote")
        if kind in ("statement", "revelation") and not r.get("public_at"):
            errs.append(f"{rid}: {kind} without public_at")
        if r.get("quote") and len(r["quote"].split()) > MAX_QUOTE_WORDS:
            errs.append(f"{rid}: quote longer than {MAX_QUOTE_WORDS} words; split it into records")
        if kind == "statement" and r.get("statement_type") not in STATEMENT_TYPES:
            errs.append(f"{rid}: statement_type must be one of {sorted(STATEMENT_TYPES)}")
        if kind == "market":
            if not r.get("metric"):
                errs.append(f"{rid}: market record without metric")
            if not isinstance(r.get("value"), (int, float)) and r.get("value") is not None:
                errs.append(f"{rid}: market value must be a number from the script output")
            if src and src.get("doc_type") == "script output" and not src.get("location"):
                errs.append(f"{rid}: market record without JSON path in source.location")
        if status == "inference" and not r.get("refs"):
            errs.append(f"{rid}: inference without refs")
        if kind == "comparison":
            for f in ("statement_id", "revelation_ids", "apparent_inconsistency", "innocent_explanation", "confidence"):
                if not r.get(f):
                    errs.append(f"{rid}: comparison missing {f}")
        if r.get("confidence") and kind in ("comparison", "alternative") or status == "inference":
            if not str(r.get("confidence", "")).lower().startswith(LEVELS):
                errs.append(f"{rid}: confidence must start with high / moderate / low")
        if kind == "alternative" and not str(r.get("weight", "")).lower().startswith(WEIGHTS):
            errs.append(f"{rid}: alternative weight must be primary / contributing / unlikely")
        if kind == "knowledge" and r.get("direction") not in DIRECTIONS:
            errs.append(f"{rid}: knowledge direction must be supports or undercuts")
        if kind == "search" and not (r.get("tool") and r.get("query")):
            errs.append(f"{rid}: search without tool and query")
        if kind == "gap" and not r.get("would_be_settled_by"):
            errs.append(f"{rid}: gap without would_be_settled_by")
        if BANNED.search(r.get("claim", "")) and status != "attributed":
            errs.append(f"{rid}: conclusory wording in claim (see language-rules.md)")
        if str(r.get("verified", "")).startswith("failed") and not any(o.get("supersedes") == rid for o in recs):
            errs.append(f"{rid}: verification failed and not superseded")
    for r in recs:
        for f in ("refs", "revelation_ids", "contrary_evidence_ids"):
            for ref in r.get(f) or []:
                if ref not in ids:
                    errs.append(f"{r.get('id')}: {f} points to unknown id {ref}")
        if r.get("statement_id"):
            if r["statement_id"] not in ids:
                errs.append(f"{r.get('id')}: statement_id points to unknown id {r['statement_id']}")
            elif ids[r["statement_id"]].get("kind") != "statement":
                errs.append(f"{r.get('id')}: statement_id {r['statement_id']} is a {ids[r['statement_id']].get('kind')} record")
        if r.get("supersedes") and r["supersedes"] not in ids:
            errs.append(f"{r.get('id')}: supersedes unknown id {r['supersedes']}")
    return recs, errs


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("…", "...").replace(" ", " ").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def quotes(path):
    recs, errs = load(path), []
    src_dir = os.path.join(os.path.dirname(path), "sources")
    for r in live(recs):
        q = r.get("quote")
        if not q:
            continue
        files = glob.glob(os.path.join(src_dir, f"{r['id']}*.txt")) + glob.glob(os.path.join(src_dir, f"{(r.get('source') or {}).get('doc_id', '__none__')}*.txt"))
        if not files:
            errs.append(f"{r['id']}: no saved source text in sources/ to match the quote")
            continue
        text = " ".join(norm(open(f, errors="ignore").read()) for f in files)
        parts = [p for p in re.split(r"\.\.\.|\[\.\.\.\]|\[…\]", norm(q).replace("[...]", "...")) if p.strip(" []")]
        missing = [p.strip(" []") for p in parts if p.strip(" []") not in text]
        if missing:
            errs.append(f"{r['id']}: quote not found verbatim in {', '.join(os.path.basename(f) for f in files)}: "
                        f"first missing part \"{missing[0][:80]}\"")
    return recs, errs


def summary(path):
    recs = load(path)
    rs = live(recs)
    out = [f"{len(recs)} records ({len(recs) - len(rs)} superseded or unreadable)",
           "kinds: " + ", ".join(f"{k} {n}" for k, n in Counter(r.get("kind") for r in rs).most_common()),
           "status: " + ", ".join(f"{k} {n}" for k, n in Counter(r.get("status") for r in rs).most_common())]
    unver = [r["id"] for r in rs if r.get("kind") not in ("search", "issue", "gap") and not r.get("verified")]
    out.append(f"not yet verified: {len(unver)}" + (f" ({', '.join(unver[:20])}{' …' if len(unver) > 20 else ''})" if unver else ""))
    comps = [r for r in rs if r.get("kind") == "comparison"]
    if comps:
        out.append("comparisons: " + ", ".join(f"{r['id']} ({str(r.get('confidence', '')).split()[0]})" for r in comps))
    gaps = [r for r in rs if r.get("kind") == "gap" or r.get("status") == "gap"]
    out.append(f"open gaps: {len(gaps)}")
    out += [f"  {r['id']}: {r.get('claim')} -> {r.get('would_be_settled_by')}" for r in gaps]
    return recs, out


TYPE = {"market": "Price reaction", "statement": "Company statement", "revelation": "Revelation",
        "knowledge": "Knowledge indicator", "event": "Event", "external": "External"}


def fmt_value(r):
    v = r.get("value")
    if not isinstance(v, (int, float)):
        return str(r.get("text") or v)
    if r.get("unit") == "fraction":
        return f"{v:+.1%}"
    if r.get("unit") in ("number", "multiple"):
        return f"{v:.2f}"
    return (f"{v:,.2f}" if abs(v) < 1e4 else f"{v / 1e6:,.1f}M" if abs(v) < 1e9 else f"{v / 1e9:,.2f}B") + f" {r.get('unit') or ''}".rstrip()


TIMELINE_METRICS = ("Day-0 return", "Abnormal return", "t-statistic", "Two-day abnormal return", "Volume / 30-day average",
                    "Drop standard class")


def timeline(path):
    recs = load(path)
    rows, undated, market = [], [], {}
    for r in live(recs):
        if r.get("kind") == "market":
            if r.get("event_at"):
                market.setdefault(r["event_at"][:10], []).append(r)
            continue
        if r.get("kind") not in TYPE:
            continue
        key, shown = when(r)
        if key is None:
            undated.append(r["id"])
            continue
        if r.get("stage") == "market-event":
            rows.append((key, r["id"], f"| {shown} | {cell(r.get('claim'))} | Price reaction | [{r['id']}] | yes (market price) |"))
            continue
        typ = TYPE[r["kind"]]
        if r["kind"] == "external":
            typ = (r.get("forum") or "External").split()[0].capitalize()
        if r.get("indicator", "").lower().startswith("insider"):
            typ = "Insider trade"
        both = f" (underlying: {r['event_at']})" if r.get("public_at") and r.get("event_at") and r["event_at"] != r["public_at"] else ""
        public = "yes" if r.get("public_at") else "not established"
        url = (r.get("source") or {}).get("url")
        src = f"[{r['id']}]({url})" if url and url.startswith("http") else f"[{r['id']}]"
        rows.append((key, r["id"], f"| {shown}{both} | {cell(r.get('claim'))} | {typ} | {src} | {public} |"))
    for d, ms in market.items():
        ms = [r for r in ms if str(r.get("metric", "")).startswith(TIMELINE_METRICS)] or ms
        what = "; ".join(f"{r.get('metric').split(' (')[0]} {fmt_value(r)}" for r in ms)
        rows.append((d, ms[0]["id"], f"| {d} | {cell(what)} | Price reaction | {' '.join('[' + r['id'] + ']' for r in ms)} | yes (market price) |"))
    out = ["| Date (time, zone) | What | Type | Source | Publicly known? |", "|---|---|---|---|---|"]
    out += [x[2] for x in sorted(rows)]
    if undated:
        out += ["", "Date not established (gaps): " + ", ".join(undated)]
    return recs, out


def sources(path):
    recs = load(path)
    out = []
    for r in live(recs):
        s = r.get("source") or {}
        if not s or r.get("kind") == "search":
            continue
        date = (r.get("public_at") or r.get("event_at") or "")[:10]
        bits = [s.get("title"), s.get("publisher"), s.get("doc_type"), date, s.get("location")]
        link = s.get("url") or ""
        out.append(f"[{r['id']}] " + ", ".join(cell(b) for b in bits if b) + (f", <{link}>" if link.startswith("http") else f", {link}" if link else ""))
    return recs, out


def cell(s):
    return str(s or "").replace("|", "/").replace("\n", " ")


PCT = re.compile(r"[−-]?\d+(?:\.\d+)?\s?%")
MONEY = re.compile(r"(?:[$€£]\s?\d|\b\d+(?:\.\d+)?\s?(?:million|billion|[MB]\b)(?:\s?(?:USD|CAD|GBP|EUR))?)")


def strip_quotes(line):
    return re.sub(r"\"[^\"]*\"|“[^”]*”|^>.*$", "", line)


def memo(path, memo_path):
    recs, errs = check(path)
    ids = {r["id"]: r for r in recs if "_error" not in r}
    gone = superseded(recs)
    in_sources = False
    for n, line in enumerate(open(memo_path), 1):
        if line.startswith("## "):
            in_sources = line.strip().lower() in ("## sources", "## coverage")
        cites = CITE.findall(line)
        for c in cites:
            if c not in ids:
                errs.append(f"memo line {n}: cites unknown record {c}")
            elif c in gone:
                errs.append(f"memo line {n}: cites superseded record {c}")
            elif str(ids[c].get("verified", "")).startswith("failed"):
                errs.append(f"memo line {n}: cites record {c} that failed verification")
        if in_sources or line.startswith("#"):
            continue
        body = strip_quotes(line)
        m = BANNED.search(body)
        if m:
            errs.append(f"memo line {n}: conclusory wording \"{m.group(0)}\" outside a quotation (language-rules.md)")
        figs = PCT.findall(body) + MONEY.findall(body)
        if figs and not cites and not re.match(r"\s*\|[-| ]+\|\s*$", line):
            errs.append(f"memo line {n}: figure {figs[0].strip()} with no record citation")
        vals = [ids[c].get("value") for c in cites if c in ids and ids[c].get("kind") == "market"]
        vals = [v for v in vals if isinstance(v, (int, float))]
        if vals:
            pcts = {f"{100 * v:.{k}f}" for v in vals for k in (0, 1, 2)} | {f"{abs(100 * v):.{k}f}" for v in vals for k in (0, 1, 2)}
            for p in PCT.findall(body):
                num = p.replace("%", "").replace("−", "-").strip().lstrip("+")
                if num not in pcts and num.lstrip("-") not in pcts:
                    errs.append(f"memo line {n}: {p.strip()} does not match any cited market record ({', '.join(c for c in cites if ids.get(c, {}).get('kind') == 'market')})")
    return recs, errs


MARKET_FIELDS = [  # (JSON key, metric, unit); unit "ccy" is replaced by the result's currency
    ("close", "Day-0 close", "ccy"), ("prev_close", "Previous close", "ccy"), ("return", "Day-0 return", "fraction"),
    ("market_return", "Market index return", "fraction"), ("peer_return", "Peer index return", "fraction"),
    ("theme_return", "Theme ETF return", "fraction"), ("expected_return", "Expected return", "fraction"),
    ("abnormal_return", "Abnormal return", "fraction"), ("t_stat", "t-statistic", "number"),
    ("ar_m1", "Abnormal return day -1", "fraction"), ("ar_p1", "Abnormal return day +1", "fraction"),
    ("car_0_1", "Two-day abnormal return (days 0 to 1)", "fraction"),
    ("pre_drift_m5_m1", "Pre-event drift (days -5 to -1)", "fraction"),
    ("car_1_5_rebound", "Rebound (days 1 to 5)", "fraction"), ("volume_ratio", "Volume / 30-day average", "multiple"),
    ("market_cap_lost", "Market value lost on day 0 (observed, not attributed loss)", "ccy"),
]


def next_id(recs, prefix="E"):
    nums = [int(m.group(1)) for r in recs if (m := re.fullmatch(re.escape(prefix) + r"(\d+)", str(r.get("id", ""))))]
    return max(nums, default=0) + 1


def add_market(path, me_path, symbol=None):
    recs = load(path) if os.path.exists(path) else []
    res = [r for r in json.load(open(me_path)) if "error" not in r and (symbol is None or r["symbol"] == symbol)]
    if len(res) != 1:
        sys.exit(f"{me_path}: expected one result{' for ' + symbol if symbol else ''}, found {len(res)}; pass EXCH:TICKER")
    r, idx = res[0], json.load(open(me_path)).index(res[0])
    have = {((x.get("source") or {}).get("url"), (x.get("source") or {}).get("location")) for x in recs}
    n, new = next_id(recs), []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rel = os.path.relpath(me_path, os.path.join(os.path.dirname(os.path.abspath(path)), "..", "..", ".."))

    def rec(loc, claim, **kw):
        nonlocal n
        if (rel, loc) in have:
            return
        new.append({"id": f"E{n:03d}", "stage": "market-event", "kind": "market", "status": "fact", "claim": claim,
                    "event_at": r["day0"], **kw, "source": {"title": "market_event.py output", "publisher": "research-analyst",
                    "doc_type": "script output", "url": rel, "location": loc, "tier": 1, "retrieved_at": now}})
        n += 1

    for key, metric, unit in MARKET_FIELDS:
        v = r.get(key)
        if v is None:
            continue
        if unit == "ccy":
            unit = (r.get("market_cap_currency") if key == "market_cap_lost" else r.get("currency")) or r.get("currency") or "local currency"
        label = metric.replace("Market index", f"Market ({r.get('market_index')})").replace("Theme ETF", f"Theme ({r.get('theme_etf')})")
        rec(f"$[{idx}].{key}", f"{label} on {r['day0']}: {v}", metric=label, value=v, unit=unit)
    rec(f"$[{idx}].class", f"Drop standard class on {r['day0']}: {r['class']}", metric="Drop standard class", value=None,
        unit="class", text=r["class"])
    for i, f in enumerate(r.get("flags") or []):
        rec(f"$[{idx}].flags[{i}]", f"Data flag: {f}", metric="Data flag", value=None, unit="flag", text=f)
    with open(path, "a") as fh:
        for x in new:
            fh.write(json.dumps(x) + "\n")
    return recs + new, [f"added {len(new)} market records ({new[0]['id']}..{new[-1]['id']})" if new else "nothing new to add"]


if __name__ == "__main__":
    if len(sys.argv) in (4, 5) and sys.argv[1] == "add-market":
        print("\n".join(add_market(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else None)[1]))
        sys.exit(0)
    cmds = {"check": check, "quotes": quotes, "summary": summary, "timeline": timeline, "sources": sources}
    if len(sys.argv) == 4 and sys.argv[1] == "memo":
        recs, errs = memo(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] in cmds:
        recs, errs = cmds[sys.argv[1]](sys.argv[2])
        if sys.argv[1] in ("summary", "timeline", "sources"):
            print("\n".join(errs))
            sys.exit(0)
    else:
        sys.exit(__doc__)
    print(f"{len(recs)} records, {len(errs)} problems")
    for e in errs:
        print(" -", e)
    sys.exit(1 if errs else 0)
