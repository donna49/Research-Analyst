#!/usr/bin/env python3
"""Structural checks for a case ledger (references/evidence-ledger.md).

  ledger.py check runs/<date>/<TICKER>/ledger.jsonl
  ledger.py quotes runs/<date>/<TICKER>/ledger.jsonl   # quote match against saved sources/

`check` catches broken records; it cannot decide whether evidence is true or whether a citation
supports a claim. `quotes` exact-matches every quote against the saved text in sources/<id>*.txt
(whitespace and typographic quotes normalized). Exit code 1 on any failure.
"""
import glob, json, os, re, sys

STAGES = {"market-event", "trigger", "issue", "statement", "comparison", "knowledge", "external", "timeline", "verify"}
KINDS = {"market", "revelation", "statement", "comparison", "knowledge", "external", "event", "alternative",
         "gap", "search", "issue"}
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
        if r.get("status") not in ("inference", "gap") and r.get("kind") not in ("search", "issue") and not r.get("source"):
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


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("check", "quotes"):
        sys.exit(__doc__)
    recs, errs = (check if sys.argv[1] == "check" else quotes)(sys.argv[2])
    print(f"{len(recs)} records, {len(errs)} problems")
    for e in errs:
        print(" -", e)
    sys.exit(1 if errs else 0)
