#!/usr/bin/env python3
"""EDGAR helpers: filings with true acceptance times, full-text search, Form 4 rows, document text.

  edgar.py filings <TICKER|CIK> --from YYYY-MM-DD --to YYYY-MM-DD [--forms 8-K,10-Q] [--no-index] [--json out.json]
  edgar.py fts "<phrase>" <TICKER|CIK> --from YYYY-MM-DD --to YYYY-MM-DD [--forms 8-K,10-Q] [--json out.json]
  edgar.py form4 <TICKER|CIK> --from YYYY-MM-DD --to YYYY-MM-DD [--json out.json]
  edgar.py fetch <url> --out runs/<date>/<TICKER>/sources/E0xx.txt

`filings` takes `public_at` from the "Accepted" line of each filing's index page (Eastern Time),
never from the submissions-JSON acceptanceDateTime, which is mislabelled UTC and can be hours off.
`after_close` = accepted at/after 16:00 ET, `before_open` = before 09:30 ET. With --no-index,
public_at is left empty. Filings accepted after 17:30 ET carry the next business day as filing
date. Acceptance is when EDGAR made the filing public; a press release in it may have reached the
market earlier through a newswire, so check both.
`form4` prints one row per non-derivative transaction; `10b5-1` is "yes" when the 10b5-1 box is
checked or a referenced footnote/remark mentions Rule 10b5-1 (adoption date if the text gives one).
`fetch` saves plain text so `ledger.py quotes` can match quotes against it.

SEC requires a User-Agent with a contact: set SEC_USER_AGENT_EMAIL (the default placeholder
"replace-me@example.com" must be replaced). Max 8 requests/second; 3 retries on 429/5xx.
Raw responses are cached in .cache/edgar/ (Archives documents forever, other endpoints per day).
"""
import argparse, datetime as dt, hashlib, html, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UA = "research-analyst " + os.environ.get("SEC_USER_AGENT_EMAIL", "replace-me@example.com")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".cache", "edgar")
MIN_GAP, _last = 1 / 8, [0.0]


def get(url):
    immutable = "/Archives/edgar/data/" in url
    key = re.sub(r"[^A-Za-z0-9._-]", "_", url.split("://", 1)[-1])
    key = (key[:150] + "_" + hashlib.sha1(url.encode()).hexdigest()[:10]) if len(key) > 160 else key
    path = os.path.join(CACHE, key + ("" if immutable else "_" + dt.date.today().isoformat()))
    if os.path.exists(path):
        return open(path, "rb").read()
    for attempt in range(4):
        time.sleep(max(0, _last[0] + MIN_GAP - time.time()))
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if (e.code == 429 or e.code >= 500) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"HTTP {e.code} for {url}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"{e.reason} for {url}")
    os.makedirs(CACHE, exist_ok=True)
    open(path, "wb").write(data)
    return data


def get_json(url):
    return json.loads(get(url))


def resolve_cik(who):
    if who.isdigit():
        return int(who)
    cik = find_cik(get_json("https://www.sec.gov/files/company_tickers.json"), who)
    if cik is None:
        raise SystemExit(f"ticker {who} not in company_tickers.json")
    return cik


def submissions(cik, start, end):
    js = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    rows = parse_submissions(js["filings"]["recent"])
    for f in js["filings"].get("files", []):
        if f["filingFrom"] <= end and f["filingTo"] >= start:
            rows += parse_submissions(get_json("https://data.sec.gov/submissions/" + f["name"]))
    return [r for r in rows if start <= r["filed"] <= end]


def archive(cik, acc):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/"


def find_cik(tickers, ticker):
    t = ticker.upper().replace(".", "-")
    return next((int(v["cik_str"]) for v in tickers.values() if v["ticker"].upper() == t), None)


def parse_submissions(cols):
    keys = ("accessionNumber", "filingDate", "reportDate", "acceptanceDateTime", "form", "items", "primaryDocument", "primaryDocDescription")
    out = []
    for i in range(len(cols["accessionNumber"])):
        c = {k: (cols.get(k) or [""] * (i + 1))[i] for k in keys}
        out.append({"accession": c["accessionNumber"], "filed": c["filingDate"], "form": c["form"], "items": c["items"],
                    "period": c["reportDate"], "doc": c["primaryDocument"], "desc": c["primaryDocDescription"],
                    "json_acceptance": c["acceptanceDateTime"]})
    return out


def parse_index(page):
    info = dict((re.sub(r"\s+", " ", k).strip(), v) for k, v in re.findall(
        r'<div class="infoHead">(.*?)</div>\s*<div class="info">(.*?)</div>', page, re.S))
    items = [html.unescape(re.sub(r"<[^>]+>", "", s)).strip() for s in re.split(r"<br\s*/?>", info.get("Items", ""))]
    return {"accepted": info.get("Accepted", "").strip() or None, "filing_date": info.get("Filing Date", "").strip() or None,
            "period": info.get("Period of Report", "").strip() or None, "items_text": [s for s in items if s]}


def session(accepted):
    """'YYYY-MM-DD HH:MM:SS' in ET -> (iso with offset, after_close, before_open)."""
    t = dt.datetime.strptime(accepted, "%Y-%m-%d %H:%M:%S").replace(tzinfo=NY)
    hm = (t.hour, t.minute)
    return t.isoformat(), hm >= (16, 0), hm < (9, 30)


def parse_fts(js):
    out = []
    for h in js.get("hits", {}).get("hits", []):
        s, (acc, _, fname) = h["_source"], h["_id"].partition(":")
        cik = int(s["ciks"][0]) if s.get("ciks") else 0
        out.append({"form": s.get("form") or (s.get("root_forms") or [""])[0], "file_type": s.get("file_type"),
                    "filed": s.get("file_date"), "period": s.get("period_ending"), "accession": acc, "file": fname,
                    "url": archive(cik, acc) + fname, "names": "; ".join(s.get("display_names") or [])})
    return out


MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DATE = rf"(?:{MONTHS}\s+\d{{1,2}},?\s+\d{{4}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}}|\d{{4}}-\d{{2}}-\d{{2}})"


def plan_date(text):
    for sent in re.split(r"(?<=[.;])\s+", text):
        if re.search(r"10b5-?1", sent, re.I) and re.search(r"adopt|entered into|established", sent, re.I):
            m = re.search(DATE, sent)
            if m:
                return m.group(0)
    m = re.search(rf"(?:adopt\w*|entered into|established)\D{{0,60}}?({DATE})", text, re.I)
    return m.group(1) if m else None


def parse_form4(xml):
    root = ET.fromstring(xml.strip() if isinstance(xml, str) else xml.strip().decode("utf-8", "ignore"))
    v = lambda el, p: (el.findtext(p + "/value") if el.find(p + "/value") is not None else el.findtext(p) or "").strip()
    owners, roles = [], []
    for o in root.findall("reportingOwner"):
        owners.append(o.findtext("reportingOwnerId/rptOwnerName", "").strip())
        r = o.find("reportingOwnerRelationship")
        flag = lambda k: (r.findtext(k) or "").strip().lower() in ("1", "true") if r is not None else False
        roles.append(", ".join(filter(None, ["Director" if flag("isDirector") else "",
                                             (r.findtext("officerTitle") or "Officer").strip() if flag("isOfficer") else "",
                                             "10% owner" if flag("isTenPercentOwner") else "",
                                             (r.findtext("otherText") or "Other").strip() if flag("isOther") else ""])))
    notes = {f.get("id"): " ".join((f.text or "").split()) for f in root.findall("footnotes/footnote")}
    remarks = " ".join((root.findtext("remarks") or "").split())
    box = (root.findtext("aff10b5One") or "").strip().lower() in ("1", "true")
    rows = []
    for t in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        texts = [notes.get(f.get("id"), "") for f in t.iter("footnoteId")]
        hit = [s for s in texts if re.search(r"10b5-?1", s, re.I)] or ([remarks] if re.search(r"10b5-?1", remarks, re.I) else [])
        rows.append({"owner": "; ".join(owners), "role": "; ".join(roles), "security": v(t, "securityTitle"),
                     "date": v(t, "transactionDate"), "code": t.findtext("transactionCoding/transactionCode", "").strip(),
                     "acq_disp": v(t, "transactionAmounts/transactionAcquiredDisposedCode"),
                     "shares": v(t, "transactionAmounts/transactionShares"),
                     "price": v(t, "transactionAmounts/transactionPricePerShare"),
                     "owned_after": v(t, "postTransactionAmounts/sharesOwnedFollowingTransaction"),
                     "direct": v(t, "ownershipNature/directOrIndirectOwnership"),
                     "plan_10b5_1": bool(hit) or box, "plan_adopted": next(filter(None, map(plan_date, hit)), None),
                     "plan_text": " | ".join(hit) or None})
    return rows


BLOCK = r"p|div|br|tr|li|h[1-6]|table|ul|ol|section|article|blockquote|pre|hr|title|center"


def html_to_text(page):
    page = re.sub(r"(?is)^\s*<DOCUMENT>.*?<TEXT>\s*", "", page)
    if not re.search(r"<(html|body|div|p|table|font|br)\b", page[:20000], re.I):
        return page
    s = re.sub(r"(?is)<(script|style|head|ix:header)\b.*?</\1\s*>|<!--.*?-->", " ", page)
    s = re.sub(rf"(?i)</?(?:{BLOCK})\b[^>]*>", "\n", s)
    s = re.sub(r"(?i)</t[dh]\s*>", " ", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ").replace("​", "")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in s.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def table(rows, cols):
    print("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join(str(r.get(c, "") if r.get(c) is not None else "").replace("|", "/") for c in cols) + " |")


def cmd_filings(a):
    cik = resolve_cik(a.who)
    forms = set(a.forms.split(",")) if a.forms else None
    rows = [r for r in submissions(cik, a.start, a.end) if not forms or r["form"] in forms]
    for r in rows:
        r["index_url"] = archive(cik, r["accession"]) + r["accession"] + "-index.htm"
        r["doc_url"] = archive(cik, r["accession"]) + re.sub(r"^xsl[^/]+/", "", r["doc"]) if r["doc"] else None
        r["public_at"] = r["after_close"] = r["before_open"] = None
        if not a.no_index:
            ix = parse_index(get(r["index_url"]).decode("utf-8", "ignore"))
            r["period"], r["items_text"] = ix["period"] or r["period"], ix["items_text"]
            if ix["accepted"]:
                r["public_at"], r["after_close"], r["before_open"] = session(ix["accepted"])
        r["session"] = "" if r["public_at"] is None else "after close" if r["after_close"] else "before open" if r["before_open"] else "market hours"
    table(rows, ["filed", "form", "items", "period", "public_at", "session", "accession", "doc"])
    return rows


def cmd_fts(a):
    cik = resolve_cik(a.who)
    q = {"q": f'"{a.phrase}"' if " " in a.phrase and not a.phrase.startswith('"') else a.phrase,
         "ciks": f"{cik:010d}", "startdt": a.start, "enddt": a.end}
    if a.forms:
        q["forms"] = a.forms
    rows, frm = [], 0
    while True:
        js = get_json("https://efts.sec.gov/LATEST/search-index?" + urllib.parse.urlencode({**q, "from": frm}))
        page = parse_fts(js)
        rows += page
        frm += len(page)
        if not page or frm >= js["hits"]["total"]["value"] or frm >= 1000:
            break
    rows.sort(key=lambda r: (r["filed"] or "", r["accession"]), reverse=True)
    print(f"{len(rows)} hits for {q['q']} (CIK {cik}, {a.start}..{a.end})\n")
    table(rows, ["filed", "form", "file_type", "accession", "file", "url"])
    return rows


def cmd_form4(a):
    cik = resolve_cik(a.who)
    rows = []
    for f in submissions(cik, a.start, a.end):
        if f["form"] not in ("4", "4/A") or not f["doc"]:
            continue
        url = archive(cik, f["accession"]) + re.sub(r"^xsl[^/]+/", "", f["doc"])
        for t in parse_form4(get(url)):
            rows.append({"filed": f["filed"], "form": f["form"], "accession": f["accession"], "url": url, **t})
    rows.sort(key=lambda r: (r["date"], r["filed"]))
    table([{**r, "10b5-1": ("yes" + (f" (adopted {r['plan_adopted']})" if r["plan_adopted"] else "")) if r["plan_10b5_1"] else ""}
           for r in rows], ["date", "filed", "owner", "role", "code", "acq_disp", "shares", "price", "owned_after", "direct", "10b5-1", "accession"])
    return rows


def cmd_fetch(a):
    text = html_to_text(get(a.url).decode("utf-8", "ignore"))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w").write(text)
    print(f"{len(text)} chars -> {a.out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("filings", "fts", "form4"):
        s = sub.add_parser(name)
        if name == "fts":
            s.add_argument("phrase")
        s.add_argument("who")
        s.add_argument("--from", dest="start", required=True)
        s.add_argument("--to", dest="end", required=True)
        if name != "form4":
            s.add_argument("--forms")
        if name == "filings":
            s.add_argument("--no-index", action="store_true")
        s.add_argument("--json")
    s = sub.add_parser("fetch")
    s.add_argument("url")
    s.add_argument("--out", required=True)
    a = p.parse_args()
    rows = {"filings": cmd_filings, "fts": cmd_fts, "form4": cmd_form4, "fetch": cmd_fetch}[a.cmd](a)
    if getattr(a, "json", None):
        json.dump(rows, open(a.json, "w"), indent=1)
        print(f"\n{len(rows)} records -> {a.json}")
