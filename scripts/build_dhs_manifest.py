"""Build manifests of DHS Program publications.

Two manifests are written:
  manifests/dhs_survey_reports.csv     Final, summary, key findings and other survey
                                       reports, from the DHS API publications endpoint.
  manifests/dhs_analytical_papers.csv  Working papers, further analysis, analytical
                                       studies, comparative reports and other analytical
                                       series, scraped from dhsprogram.com.

Usage:
  python3 scripts/build_dhs_manifest.py [--only survey|analytical]
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.error
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, write_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.dhsprogram.com/rest/dhs/publications?f=json&perpage=5000"
SITE = "https://dhsprogram.com"

# Code prefix -> (series name, URL slug used on dhsprogram.com)
ANALYTICAL_SERIES = {
    "WP": ("Working Papers", "working-papers"),
    "FA": ("Further Analysis", "further-analysis"),
    "AS": ("Analytical Studies", "analytical-studies"),
    "CR": ("Comparative Reports", "comparative-reports"),
    "MR": ("Methodological Reports", "methodological-reports"),
    "OP": ("Occasional Papers", "occasional-papers"),
    "QRS": ("Qualitative Research Studies", "qualitative-research-studies"),
    "SAR": ("Spatial Analysis Reports", "spatial-analysis-reports"),
    "AB": ("Analysis Briefs", "analysis-briefs"),
    "PB": ("Policy Briefs", "policy-briefs"),
}

# Stop probing a series after this many consecutive missing numbers.
MAX_GAP = 15


def survey_reports():
    data = json.loads(fetch(API))["Data"]
    rows = []
    for p in data:
        url = p["PublicationURL"]
        code = url.rstrip("/").split("/")[-2] if url.count("/") > 3 else ""
        rows.append({
            "source": "DHS",
            "series": p["PublicationTitle"],
            "code": code,
            "title": p["PublicationDescription"],
            "country": p["DHS_CountryCode"],
            "year": p["SurveyYear"],
            "survey_id": p["SurveyId"],
            "url": url,
            "filename": f"{p['SurveyId']}_{os.path.basename(url)}",
            "size_bytes": p.get("PublicationSize") or "",
        })
    return rows


def parse_publication_page(prefix, n):
    series, slug = ANALYTICAL_SERIES[prefix]
    code = f"{prefix}{n}"
    page = f"{SITE}/publications/publication-{code.lower()}-{slug}.cfm"
    try:
        body = fetch(page, retries=2, timeout=30).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        print(f"  could not read {page}: {e}", file=sys.stderr)
        return []
    pdfs = sorted(set(re.findall(rf'pubs/pdf/{code}/[^"\'<>]+?\.pdf', body, re.I)))
    if not pdfs:
        return []
    m = re.search(r"<title>(.*?)</title>", body, re.S)
    title = html.unescape(m.group(1)).replace("The DHS Program - ", "").strip() if m else ""
    title = re.sub(r"\s+", " ", title)
    return [{
        "source": "DHS",
        "series": series,
        "code": code,
        "title": title,
        "url": f"{SITE}/{pdf}",
        "filename": os.path.basename(pdf),
    } for pdf in pdfs]


def analytical_papers(workers=4):
    rows = []
    for prefix in ANALYTICAL_SERIES:
        n, gap, found = 1, 0, 0
        with ThreadPoolExecutor(workers) as pool:
            while gap < MAX_GAP:
                batch = list(range(n, n + workers))
                results = list(pool.map(lambda i: parse_publication_page(prefix, i), batch))
                for res in results:
                    if res:
                        rows.extend(res)
                        found += 1
                        gap = 0
                    else:
                        gap += 1
                n += workers
        print(f"  {prefix}: {found} publications", file=sys.stderr)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", choices=["survey", "analytical"])
    args = ap.parse_args()
    out = os.path.join(ROOT, "manifests")
    os.makedirs(out, exist_ok=True)

    if args.only in (None, "survey"):
        rows = survey_reports()
        write_manifest(os.path.join(out, "dhs_survey_reports.csv"), rows)
        print(f"DHS survey reports: {len(rows)}", file=sys.stderr)
    if args.only in (None, "analytical"):
        rows = analytical_papers()
        write_manifest(os.path.join(out, "dhs_analytical_papers.csv"), rows)
        print(f"DHS analytical papers: {len(rows)} files", file=sys.stderr)


if __name__ == "__main__":
    main()
