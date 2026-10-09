"""Add citation counts from NIH iCite to the PubMed paper list.

Adds two columns to literature/pubmed_dhs_mics_papers.csv:
  citations   number of citing PubMed papers (iCite citation_count)
  rcr         relative citation ratio (field- and age-adjusted; 1.0 = NIH median)

Usage:
  python3 scripts/add_citations.py [path/to/papers.csv]
"""

import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICITE = "https://icite.od.nih.gov/api/pubs?fl=pmid,citation_count,relative_citation_ratio&pmids="


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "literature", "pubmed_dhs_mics_papers.csv")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = [c for c in reader.fieldnames if c not in ("citations", "rcr")]
        rows = list(reader)

    stats = {}
    pmids = [r["pmid"] for r in rows]
    for i in range(0, len(pmids), 200):
        data = json.loads(fetch(ICITE + ",".join(pmids[i:i + 200])))["data"]
        for d in data:
            rcr = d.get("relative_citation_ratio")
            stats[str(d["pmid"])] = (d.get("citation_count", ""), f"{rcr:.2f}" if rcr is not None else "")
        print(f"  {min(i + 200, len(pmids))}/{len(pmids)}", file=sys.stderr)
        time.sleep(0.3)

    for r in rows:
        r["citations"], r["rcr"] = stats.get(r["pmid"], ("", ""))
    insert = fields.index("open_access") + 1
    fields[insert:insert] = ["citations", "rcr"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    have = sum(1 for r in rows if str(r["citations"]).isdigit())
    print(f"Citation counts added for {have} of {len(rows)} papers", file=sys.stderr)


if __name__ == "__main__":
    main()
