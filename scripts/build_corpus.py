"""Download and parse full texts of highly cited open access DHS/MICS papers.

For each paper in literature/pubmed_dhs_mics_papers.csv that is open access and
has more than --min-citations citations, the JATS XML is fetched from the PMC
Open Access dataset on AWS and parsed into sections. One JSON file per paper is
written to literature/corpus/ (ignored by git, because full texts are not ours
to redistribute).

Usage:
  python3 scripts/build_corpus.py [--min-citations 50] [--workers 4]
"""

import argparse
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PMC_OA = "https://pmc-oa-opendata.s3.amazonaws.com"


def text_of(el):
    """Plain text of an element, skipping citations' bracketed numbers' markup only."""
    if el is None:
        return ""
    parts = []
    for t in el.itertext():
        parts.append(t)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def strip_ns(root):
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]
    return root


def section(sec, level=1):
    title = text_of(sec.find("title"))
    paras = [text_of(p) for p in sec.findall("p")]
    subs = [section(s, level + 1) for s in sec.findall("sec")]
    return {"title": title, "level": level, "paragraphs": paras, "subsections": subs}


def parse(xml_bytes):
    root = strip_ns(ET.fromstring(xml_bytes))
    art = root if root.tag == "article" else root.find(".//article")
    meta = art.find("front/article-meta")
    out = {"article_type": art.get("article-type", "")}

    abstracts = [a for a in meta.findall("abstract") if a.get("abstract-type") in (None, "", "structured")]
    abstract = abstracts[0] if abstracts else None
    out["abstract"] = []
    if abstract is not None:
        secs = abstract.findall("sec")
        if secs:
            out["abstract"] = [{"title": text_of(s.find("title")),
                                "text": " ".join(text_of(p) for p in s.findall("p"))} for s in secs]
        else:
            out["abstract"] = [{"title": "", "text": " ".join(text_of(p) for p in abstract.findall("p"))}]
    out["keywords"] = [text_of(k) for k in meta.findall(".//kwd-group/kwd")]

    body = art.find("body")
    out["sections"] = [section(s) for s in body.findall("sec")] if body is not None else []
    if body is not None and not out["sections"]:
        out["sections"] = [{"title": "", "level": 1, "subsections": [],
                            "paragraphs": [text_of(p) for p in body.findall("p")]}]

    def captions(tag):
        items = []
        for el in art.iter(tag):
            cap = el.find("caption")
            items.append({"label": text_of(el.find("label")),
                          "caption": text_of(cap) if cap is not None else ""})
        return items

    out["tables"] = captions("table-wrap")
    out["figures"] = captions("fig")
    out["table_footnotes"] = [text_of(f) for f in art.iter("table-wrap-foot")]
    back = art.find("back")
    out["n_references"] = len(back.findall(".//ref")) if back is not None else 0
    out["back_sections"] = []
    if back is not None:
        for s in back.findall("sec"):
            out["back_sections"].append(section(s))
        for fn in back.findall(".//fn-group/fn"):
            out["back_sections"].append({"title": text_of(fn.find("title")) or fn.get("fn-type", ""),
                                         "level": 1, "paragraphs": [text_of(fn)], "subsections": []})
    return out


def latest_xml(pmcid):
    listing = fetch(f"{PMC_OA}/?list-type=2&prefix={pmcid}.").decode("utf-8", "replace")
    keys = re.findall(rf"<Key>({pmcid}\.(\d+)/{pmcid}\.\d+\.xml)</Key>", listing)
    if not keys:
        return None
    return f"{PMC_OA}/{max(keys, key=lambda k: int(k[1]))[0]}"


def build(row, outdir):
    path = os.path.join(outdir, f"{row['pmid']}.json")
    if os.path.exists(path):
        return "cached"
    try:
        url = latest_xml(row["pmcid"])
        if not url:
            return "no-xml"
        doc = parse(fetch(url, timeout=120))
    except (ET.ParseError, AttributeError, OSError, ValueError) as e:
        return f"error: {e}"
    doc.update({k: row[k] for k in ("pmid", "pmcid", "doi", "title", "journal", "year", "series",
                                     "citations", "rcr", "countries_in_title")})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False)
    return "ok"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--papers", default=os.path.join(ROOT, "literature", "pubmed_dhs_mics_papers.csv"))
    ap.add_argument("--out", default=os.path.join(ROOT, "literature", "corpus"))
    ap.add_argument("--min-citations", type=int, default=50)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    with open(args.papers, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r["open_access"] == "yes" and r["citations"].isdigit()
                and int(r["citations"]) > args.min_citations]
    os.makedirs(args.out, exist_ok=True)
    print(f"{len(rows)} open access papers with more than {args.min_citations} citations", file=sys.stderr)
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(lambda r: build(r, args.out), rows))
    counts = {}
    for r in results:
        key = r.split(":")[0]
        counts[key] = counts.get(key, 0) + 1
    print(counts, file=sys.stderr)
    for row, res in zip(rows, results):
        if res.startswith("error"):
            print(f"  PMID {row['pmid']}: {res}", file=sys.stderr)


if __name__ == "__main__":
    main()
