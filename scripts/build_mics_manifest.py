"""Build a manifest of MICS survey report PDFs.

mics.unicef.org sits behind bot protection, so survey records are taken from the
UNICEF MICS collection in the World Bank Microdata Library. Each survey's
"related materials" page links to the report PDFs that UNICEF hosts.

Usage:
  python3 scripts/build_mics_manifest.py [--all-materials]

By default only reports (final reports, key findings, summaries) are kept.
--all-materials also keeps questionnaires, manuals and other PDFs.
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, write_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = "https://microdata.worldbank.org/index.php"

ANCHOR = re.compile(r"<a\b([^>]*\bclass=\"download[^\"]*\"[^>]*)>", re.S)
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def list_surveys():
    surveys, offset = [], 0
    while True:
        url = f"{WB}/api/catalog/search?repo=MICS&ps=100&page={offset // 100 + 1}"
        res = json.loads(fetch(url))["result"]
        surveys.extend(res["rows"])
        offset += 100
        if offset >= int(res["found"]):
            return surveys


def survey_pdfs(survey, all_materials):
    page = fetch(f"{WB}/catalog/{survey['id']}/related-materials").decode("utf-8", "replace")
    rows, seen = [], set()
    for m in ANCHOR.finditer(page):
        attrs = dict(ATTR.findall(m.group(1)))
        href = html.unescape(attrs.get("href", "")).strip()
        if attrs.get("data-extension", "").lower() != "pdf" or href in seen:
            continue
        doc_type = attrs.get("data-dctype", "")
        if not all_materials and "doc/rep" not in doc_type:
            continue
        seen.add(href)
        name = urllib.parse.unquote(attrs.get("data-filename") or os.path.basename(href))
        rows.append({
            "source": "MICS",
            "series": "MICS Report" if "doc/rep" in doc_type else (doc_type or "Related material"),
            "code": survey["idno"],
            "title": survey["title"],
            "country": survey["nation"],
            "year": survey["year_start"],
            "survey_id": survey["idno"],
            "url": href,
            "filename": f"{survey['idno']}_{name}",
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all-materials", action="store_true")
    args = ap.parse_args()

    surveys = list_surveys()
    print(f"MICS surveys in catalog: {len(surveys)}", file=sys.stderr)
    with ThreadPoolExecutor(4) as pool:
        per_survey = list(pool.map(lambda s: survey_pdfs(s, args.all_materials), surveys))
    rows = [r for rs in per_survey for r in rs]
    rows.sort(key=lambda r: (r["country"], str(r["year"]), r["filename"]))

    out = os.path.join(ROOT, "manifests")
    os.makedirs(out, exist_ok=True)
    write_manifest(os.path.join(out, "mics_reports.csv"), rows)
    missing = sum(1 for rs in per_survey if not rs)
    print(f"MICS report PDFs: {len(rows)} ({missing} surveys had none listed)", file=sys.stderr)


if __name__ == "__main__":
    main()
