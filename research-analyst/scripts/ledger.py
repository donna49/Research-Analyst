#!/usr/bin/env python3
"""Structural checks for a case ledger (references/evidence-ledger.md).

  ledger.py check runs/<date>/<TICKER>/ledger.jsonl
  ledger.py quotes runs/<date>/<TICKER>/ledger.jsonl   # quote match against saved sources/
  ledger.py memo runs/<date>/<TICKER>/ledger.jsonl runs/<date>/<TICKER>/memo.md   # memo lint

`check` catches broken records; it cannot decide whether evidence is true or whether a citation
supports a claim. `quotes` exact-matches every quote against the saved text in sources/<id>*.txt
(whitespace and typographic quotes normalized). `memo` checks the rendered memo: every [E###]
resolves, no template markers or placeholders remain, every line with a figure carries a citation,
no ticker appears that the ledger never mentions (text carried over from another case), the
required sections and a recommendation are present. Exit code 1 on any failure.
"""
import glob, json, os, re, sys

STAGES = {"market-event", "trigger", "issue", "statement", "comparison", "knowledge", "external", "timeline", "verify",
          "parties", "economics", "claim"}
KINDS = {"market", "revelation", "statement", "comparison", "knowledge", "external", "event", "alternative",
         "gap", "search", "issue", "party", "capital", "offering", "proceeding", "economics", "legal", "decision"}
RECOMMENDATIONS = {"pursue", "pursue-hold", "monitor", "pass"}
STATUSES = {"fact", "attributed", "inference", "assumption", "estimate", "gap"}
STATEMENT_TYPES = {"fact", "forward-looking", "opinion", "risk-hypothetical", "reassurance", "omission", "puffery"}
BANNED = re.compile(r"\b(fraud\w*|lied|lying|deceiv\w*|scheme|misled|liable)\b", re.I)


def load(path):
    recs = []
    for n, line in enumerate(open(path), 1):
        if line.strip():
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError as e:
                recs.append({"_error": f"line {n}: invalid JSON ({e})"})
    return recs


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
        for f in ("id", "stage", "kind", "claim", "status"):
            if not r.get(f):
                errs.append(f"{rid}: missing {f}")
        if r.get("stage") and r["stage"] not in STAGES:
            errs.append(f"{rid}: unknown stage {r['stage']}")
        if r.get("kind") and r["kind"] not in KINDS:
            errs.append(f"{rid}: unknown kind {r['kind']}")
        if r.get("status") and r["status"] not in STATUSES:
            errs.append(f"{rid}: unknown status {r['status']}")
        if r.get("status") not in ("inference", "gap") and r.get("kind") not in ("search", "issue", "decision") and not r.get("source"):
            errs.append(f"{rid}: {r.get('status')} record has no source")
        src = r.get("source") or {}
        if src and src.get("doc_type") != "script output":
            for f in ("title", "url", "tier", "retrieved_at"):
                if not src.get(f):
                    errs.append(f"{rid}: source missing {f}")
        if r.get("kind") in ("statement", "revelation") and not r.get("quote"):
            errs.append(f"{rid}: {r['kind']} without verbatim quote")
        if r.get("kind") in ("statement", "revelation") and not r.get("public_at"):
            errs.append(f"{rid}: {r['kind']} without public_at")
        if r.get("kind") == "statement" and r.get("statement_type") not in STATEMENT_TYPES:
            errs.append(f"{rid}: statement_type must be one of {sorted(STATEMENT_TYPES)}")
        if r.get("status") == "inference" and not r.get("refs"):
            errs.append(f"{rid}: inference without refs")
        if r.get("kind") == "comparison":
            for f in ("statement_id", "revelation_ids", "apparent_inconsistency", "innocent_explanation", "confidence"):
                if not r.get(f):
                    errs.append(f"{rid}: comparison missing {f}")
        if r.get("kind") == "economics" and (r.get("source") or {}).get("doc_type") != "script output":
            errs.append(f"{rid}: economics record must cite economics.py output (script output)")
        if r.get("kind") == "legal" and not r.get("citation"):
            errs.append(f"{rid}: legal record without citation")
        if r.get("kind") == "decision":
            if r.get("recommendation") not in RECOMMENDATIONS:
                errs.append(f"{rid}: decision.recommendation must be one of {sorted(RECOMMENDATIONS)}")
            if not r.get("refs"):
                errs.append(f"{rid}: decision without refs")
        if r.get("kind") == "proceeding" and not r.get("forum"):
            errs.append(f"{rid}: proceeding without forum")
        if r.get("kind") == "gap" and not r.get("would_be_settled_by"):
            errs.append(f"{rid}: gap without would_be_settled_by")
        if BANNED.search(r.get("claim", "")) and r.get("status") != "attributed":
            errs.append(f"{rid}: conclusory wording in claim (see language-rules.md)")
        if str(r.get("verified", "")).startswith("failed") and not any(o.get("supersedes") == rid for o in recs):
            errs.append(f"{rid}: verification failed and not superseded")
    for r in recs:
        for f in ("refs", "revelation_ids", "contrary_evidence_ids"):
            for ref in r.get(f) or []:
                if ref not in ids:
                    errs.append(f"{r.get('id')}: {f} points to unknown id {ref}")
        if r.get("statement_id") and r["statement_id"] not in ids:
            errs.append(f"{r.get('id')}: statement_id points to unknown id {r['statement_id']}")
    return recs, errs


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("…", "...").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def quotes(path):
    recs, errs = load(path), []
    src_dir = os.path.join(os.path.dirname(path), "sources")
    for r in recs:
        q = r.get("quote")
        if not q:
            continue
        files = glob.glob(os.path.join(src_dir, f"{r['id']}*.txt")) + glob.glob(os.path.join(src_dir, f"{(r.get('source') or {}).get('doc_id', '__none__')}*.txt"))
        if not files:
            errs.append(f"{r['id']}: no saved source text in sources/ to match the quote")
            continue
        text = " ".join(norm(open(f, errors="ignore").read()) for f in files)
        parts = [p for p in norm(q).split("...") if p.strip()]
        if not all(p.strip() in text for p in parts):
            errs.append(f"{r['id']}: quote not found verbatim in {', '.join(os.path.basename(f) for f in files)}")
    return recs, errs


REQUIRED_SECTIONS = ["OVERVIEW", "TOTAL MIX OF INFORMATION", "PUBLIC CORRECTIVE DISCLOSURE", "PARTIES",
                     "POTENTIAL CLASS PROCEEDING", "THE MISREPRESENTATION", "PARALLEL AND COMPETING PROCEEDINGS",
                     "BEAR v. BULL", "CONCLUSIONS"]
PLACEHOLDER = re.compile(r"«|»|\[(add|number|tbd|insert|todo)[^\]]*\]|\breserved\b|\bTBD\b|PART __|\?\?\?|XX+\b", re.I)
CITE = re.compile(r"\[(E\d{3,})\]")
FIGURE = re.compile(r"(\$\s?\d|\bC\$|\bUS\$|\bUSD\s?\d|\bCAD\s?\d|\d[\d,.]*\s?%|\d[\d,.]*\s?(million|billion|M|B)\b)")
TICKER = re.compile(r"\b(?:TSXV?|CSE|NEO|NYSE|NASDAQ|Nasdaq|OTCQX|OTCQB|OTC|ASX|LSE|XETR|FRA|Cboe Canada|CBOE)\s*:\s*[\"“']?([A-Z][A-Z0-9.]{0,7})|\(\s*[\"“]([A-Z][A-Z0-9.]{1,7})[\"”]\s*\)")


def memo(ledger_path, memo_path):
    recs, errs = check(ledger_path)
    ids = {r.get("id") for r in recs}
    corpus = " ".join(json.dumps(r) for r in recs)
    text = open(memo_path).read()
    lines = text.splitlines()
    for e in sorted(set(CITE.findall(text)) - ids):
        errs.append(f"memo cites {e}, which is not in the ledger")
    in_code = False
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if PLACEHOLDER.search(line):
            errs.append(f"memo line {n}: placeholder or template marker left: {line.strip()[:90]}")
        body = line.strip()
        if in_code or not body or body.startswith("#") or body.startswith("|---"):
            continue
        if FIGURE.search(body) and not CITE.search(body):
            errs.append(f"memo line {n}: figure without a ledger citation: {body[:90]}")
    for m in TICKER.finditer(text):
        tk = m.group(1) or m.group(2)
        if tk and tk not in corpus:
            errs.append(f"memo mentions ticker {tk}, which appears nowhere in the ledger (text from another case?)")
    up = text.upper()
    for sec in REQUIRED_SECTIONS:
        if sec.upper() not in up:
            errs.append(f"memo missing section: {sec}")
    if not re.search(r"\b(Pursue|Monitor|Pass)\b", text):
        errs.append("memo has no recommendation (Pursue / Pursue — issue and hold / Monitor / Pass)")
    if not any(r.get("kind") == "decision" for r in recs):
        errs.append("ledger has no decision record (claim-framing stage)")
    return recs, errs


if __name__ == "__main__":
    if sys.argv[1:2] == ["memo"] and len(sys.argv) == 4:
        recs, errs = memo(sys.argv[2], sys.argv[3])
        print(f"{len(recs)} records, {len(errs)} problems")
        for e in errs:
            print(" -", e)
        sys.exit(1 if errs else 0)
    if len(sys.argv) != 3 or sys.argv[1] not in ("check", "quotes"):
        sys.exit(__doc__)
    recs, errs = (check if sys.argv[1] == "check" else quotes)(sys.argv[2])
    print(f"{len(recs)} records, {len(errs)} problems")
    for e in errs:
        print(" -", e)
    sys.exit(1 if errs else 0)
