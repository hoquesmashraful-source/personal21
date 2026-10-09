"""Download figure images (with captions) from open access top-cited articles.

For each article in literature/top_cited/top100.csv with a PMCID, finds the
figure files named in the JATS XML and downloads them from the PMC Open Access
dataset on AWS into literature/top_cited/figures/ (ignored by git). Writes
figures/index.csv with PMID, figure label, caption and file name.

Usage:
  python3 scripts/fetch_figures.py [--per-paper 3] [--max-papers 40]
"""

import argparse
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_corpus import PMC_OA, latest_xml, strip_ns, text_of  # noqa: E402
from common import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "literature", "top_cited")
XLINK = "{http://www.w3.org/1999/xlink}href"


def figures(pmcid):
    url = latest_xml(pmcid)
    if not url:
        return []
    raw = fetch(url, timeout=120)
    root = ET.fromstring(raw)
    hrefs = []
    for fig in root.iter():
        if not (isinstance(fig.tag, str) and fig.tag.endswith("fig")):
            continue
        g = next((e for e in fig.iter() if isinstance(e.tag, str) and e.tag.endswith("graphic")), None)
        if g is None or not g.get(XLINK):
            continue
        strip_ns(fig)
        hrefs.append((text_of(fig.find("label")), text_of(fig.find("caption")), g.get(XLINK)))
    folder = url.rsplit("/", 1)[0]
    listing = fetch(f"{PMC_OA}/?list-type=2&prefix={folder.rsplit('/', 1)[1]}/").decode("utf-8", "replace")
    keys = re.findall(r"<Key>([^<]+)</Key>", listing)
    out = []
    for label, caption, href in hrefs:
        base = os.path.splitext(os.path.basename(href))[0]
        key = next((k for k in keys if os.path.splitext(os.path.basename(k))[0] == base
                    and k.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))), None)
        if key:
            out.append((label, caption, f"{PMC_OA}/{key}"))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-paper", type=int, default=3)
    ap.add_argument("--max-papers", type=int, default=40)
    args = ap.parse_args()
    outdir = os.path.join(D, "figures")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(D, "top100.csv"), newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["pmcid"]]
    index, done = [], 0
    for r in rows:
        if done >= args.max_papers:
            break
        try:
            figs = figures(r["pmcid"])
        except Exception as e:  # noqa: BLE001
            print(f"  {r['pmid']}: {e}", file=sys.stderr)
            continue
        if not figs:
            continue
        done += 1
        for i, (label, caption, url) in enumerate(figs[: args.per_paper], 1):
            name = f"{r['rank'].zfill(3)}_{r['pmid']}_fig{i}{os.path.splitext(url)[1]}"
            path = os.path.join(outdir, name)
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(fetch(url, timeout=120))
            index.append({"rank": r["rank"], "pmid": r["pmid"], "journal": r["journal"], "year": r["year"],
                          "label": label, "caption": caption, "file": name})
    with open(os.path.join(outdir, "index.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "pmid", "journal", "year", "label", "caption", "file"])
        w.writeheader()
        w.writerows(index)
    print(f"{len(index)} figures from {done} papers in {outdir}", file=sys.stderr)


if __name__ == "__main__":
    main()
