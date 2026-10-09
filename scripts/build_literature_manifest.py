"""Build a list of PubMed research papers that use DHS or MICS data.

A paper is included when its title or abstract names the survey programme.
Each paper is tagged DHS, MICS or DHS+MICS, and flagged when PubMed Central
holds an open access copy that scripts/download.py can fetch.

Search terms (PubMed, title and abstract):
  DHS   "Demographic and Health Survey*" OR "Demographic Health Survey*"
        OR "DHS Program*" OR "National Family Health Survey*" OR "NFHS"
        (the National Family Health Survey is India's DHS)
  MICS  "Multiple Indicator Cluster Survey*" OR ("MICS" AND UNICEF)

Usage:
  python3 scripts/build_literature_manifest.py

Set NCBI_API_KEY to raise the PubMed rate limit from 3 to 10 requests a second.
"""

import csv
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.environ.get("NCBI_API_KEY", "")
PAUSE = 0.12 if API_KEY else 0.4

QUERIES = {
    "DHS": '"Demographic and Health Survey*"[tiab] OR "Demographic Health Survey*"[tiab]'
           ' OR "DHS Program*"[tiab] OR "National Family Health Survey*"[tiab] OR "NFHS"[tiab]',
    "MICS": '"Multiple Indicator Cluster Survey*"[tiab] OR ("MICS"[tiab] AND UNICEF[tiab])',
}
OPEN_ACCESS = '"pubmed pmc open access"[filter]'
FIRST_YEAR = 1980

FIELDS = [
    "source", "series", "pmid", "title", "authors", "journal", "year",
    "doi", "pmcid", "open_access", "countries_in_title",
    "pubmed_url", "url", "filename",
]


def eutils(tool, **params):
    params["retmode"] = "json"
    if API_KEY:
        params["api_key"] = API_KEY
    time.sleep(PAUSE)
    return json.loads(fetch(f"{EUTILS}/{tool}.fcgi?{urllib.parse.urlencode(params)}"))


def search(term):
    """Return all PMIDs for a query. PubMed caps one search at 10,000 records,
    so the search is split by publication year."""
    pmids = set()
    for year in range(FIRST_YEAR, time.gmtime().tm_year + 1):
        t = f"({term}) AND {year}[dp]"
        res = eutils("esearch", db="pubmed", term=t, retmax=9999)["esearchresult"]
        if int(res["count"]) > 9999:
            raise RuntimeError(f"more than 9,999 results for {year}; split the range further")
        pmids.update(res["idlist"])
    return pmids


def summaries(pmids):
    pmids = sorted(pmids, key=int)
    for i in range(0, len(pmids), 200):
        res = eutils("esummary", db="pubmed", id=",".join(pmids[i:i + 200]))["result"]
        for uid in res.get("uids", []):
            yield res[uid]
        print(f"  summaries {min(i + 200, len(pmids))}/{len(pmids)}", file=sys.stderr)


def country_names():
    data = json.loads(fetch("https://api.dhsprogram.com/rest/dhs/countries?f=json&perpage=500"))
    names = {c["CountryName"] for c in data["Data"]}
    # MICS countries that never ran a DHS survey.
    names |= {"Argentina", "Belarus", "Bhutan", "Costa Rica", "Cuba", "Iraq",
              "Kosovo", "Lao", "Laos", "Mongolia", "Montenegro", "Serbia", "Somalia",
              "Suriname", "Thailand", "Tunisia", "Vietnam", "Viet Nam", "Zanzibar",
              "Palestine", "Belize", "Barbados", "Panama", "Guinea-Bissau"}
    return sorted(names, key=len, reverse=True)


def main():
    print("Searching PubMed...", file=sys.stderr)
    hits = {name: search(q) for name, q in QUERIES.items()}
    for name, ids in hits.items():
        print(f"  {name}: {len(ids)} papers", file=sys.stderr)
    either = " OR ".join(f"({q})" for q in QUERIES.values())
    oa = search(f"({either}) AND {OPEN_ACCESS}")
    print(f"  open access in PMC: {len(oa)}", file=sys.stderr)

    countries = country_names()
    pattern = re.compile(r"\b(" + "|".join(re.escape(c) for c in countries) + r")\b", re.I)
    canon = {c.lower(): c for c in countries}

    rows = []
    for s in summaries(hits["DHS"] | hits["MICS"]):
        pmid = s["uid"]
        ids = {a["idtype"]: a["value"] for a in s.get("articleids", [])}
        pmcid = ids.get("pmc", "")
        tags = [k for k in QUERIES if pmid in hits[k]]
        authors = [a["name"] for a in s.get("authors", []) if a.get("authtype") == "Author"]
        title = s.get("title", "")
        found = sorted({canon[m.lower()] for m in pattern.findall(title)})
        is_oa = pmid in oa and bool(pmcid)
        rows.append({
            "source": "PubMed",
            "series": "+".join(tags),
            "pmid": pmid,
            "title": title,
            "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            "journal": s.get("fulljournalname", ""),
            "year": s.get("sortpubdate", "")[:4],
            "doi": ids.get("doi", ""),
            "pmcid": pmcid,
            "open_access": "yes" if is_oa else "no",
            "countries_in_title": "; ".join(found),
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            # download.py resolves pmc: URLs to the PMC Open Access PDF on AWS.
            "url": f"pmc:{pmcid}" if is_oa else "",
            "filename": f"{s.get('sortpubdate', '')[:4]}_PMID{pmid}_{pmcid}.pdf" if is_oa else "",
        })
    rows.sort(key=lambda r: (r["year"], int(r["pmid"])), reverse=True)

    out = os.path.join(ROOT, "literature")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "pubmed_dhs_mics_papers.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} papers to {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
