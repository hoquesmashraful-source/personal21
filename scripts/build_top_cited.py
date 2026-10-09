"""Find the 100 most cited public health articles and a matched comparison group.

Definition (published 2000 to 2024, citation counts from NIH iCite):
  Pool A  every article in 22 core public health and epidemiology journals
          (pre-ranked with Europe PMC, top 800 kept for iCite).
  Pool B  articles in six general medical journals (Lancet, BMJ, JAMA, NEJM,
          PLOS Medicine, Nature Medicine) indexed with a public health MeSH
          heading (Global Health, Global Burden of Disease, Public Health,
          Health Status Disparities, Population Surveillance, Socioeconomic
          Factors).
Editorials, comments, letters, news and errata are excluded.

Controls: for each top article, three articles drawn at random (fixed seed)
from the same journal and publication year (and, for pool B, the same MeSH
filter). They show what a typical paper in the same venue and year looks like.

Outputs in literature/top_cited/:
  top100.csv, controls.csv          one row per article with iCite metrics
  top100_meta.json, controls_meta.json   Europe PMC metadata incl. abstracts
  corpus/<pmid>.json                parsed open access full texts (not in git)

Usage:
  python3 scripts/build_top_cited.py
"""

import csv
import json
import os
import random
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_corpus import latest_xml, parse  # noqa: E402
from common import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "literature", "top_cited")
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ICITE = "https://icite.od.nih.gov/api/pubs?pmids="
YEARS = (2000, 2024)

CORE_ISSNS = {
    "0090-0036": "Am J Public Health", "0749-3797": "Am J Prev Med",
    "1471-2458": "BMC Public Health", "0300-5771": "Int J Epidemiol",
    "0143-005X": "J Epidemiol Community Health", "0042-9686": "Bull World Health Organ",
    "0163-7525": "Annu Rev Public Health", "1101-1262": "Eur J Public Health",
    "0033-3549": "Public Health Rep", "0277-9536": "Soc Sci Med",
    "2468-2667": "Lancet Public Health", "2214-109X": "Lancet Glob Health",
    "2059-7908": "BMJ Glob Health", "0278-2715": "Health Aff (Millwood)",
    "0964-4563": "Tob Control", "0091-7435": "Prev Med",
    "1479-5868": "Int J Behav Nutr Phys Act", "0268-1080": "Health Policy Plan",
    "0002-9262": "Am J Epidemiol", "1044-3983": "Epidemiology",
    "1368-9800": "Public Health Nutr", "1741-3842": "J Public Health (Oxf)",
}
GENERAL_TA = ["Lancet", "BMJ", "JAMA", "N Engl J Med", "PLoS Med", "Nat Med"]
MESH = ('("Global Health"[mh] OR "Global Burden of Disease"[mh] OR "Public Health"[mh] OR '
        '"Health Status Disparities"[mh] OR "Population Surveillance"[mh] OR "Socioeconomic Factors"[mh])')
EXCLUDE_PT = "NOT (editorial[pt] OR comment[pt] OR letter[pt] OR news[pt] OR published erratum[pt])"


def epmc(query, page_size=1000, cursor="*", result_type="lite", sort=None):
    params = {"query": query, "format": "json", "pageSize": page_size,
              "cursorMark": cursor, "resultType": result_type}
    if sort:
        params["sort"] = sort
    return json.loads(fetch(f"{EPMC}?{urllib.parse.urlencode(params)}"))


def esearch(term, retmax=9999):
    params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": retmax}
    time.sleep(0.4)
    return json.loads(fetch(f"{EUTILS}/esearch.fcgi?{urllib.parse.urlencode(params)}"))["esearchresult"]


def icite(pmids):
    out = {}
    pmids = list(pmids)
    for i in range(0, len(pmids), 200):
        for d in json.loads(fetch(ICITE + ",".join(pmids[i:i + 200])))["data"]:
            out[str(d["pmid"])] = d
        time.sleep(0.2)
    return out


def pool_a(n=800):
    issns = " OR ".join(f'ISSN:"{i}"' for i in CORE_ISSNS)
    q = f"({issns}) AND SRC:MED AND PUB_YEAR:[{YEARS[0]} TO {YEARS[1]}]"
    pmids, cursor = [], "*"
    while len(pmids) < n:
        res = epmc(q, cursor=cursor, sort="CITED desc")
        pmids += [r["pmid"] for r in res["resultList"]["result"] if r.get("pmid")]
        cursor = res.get("nextCursorMark")
        if not cursor:
            break
    return pmids[:n]


def pool_b():
    journals = " OR ".join(f'"{t}"[ta]' for t in GENERAL_TA)
    pmids = set()
    for y in range(YEARS[0], YEARS[1] + 1):
        res = esearch(f"({journals}) AND {MESH} AND {y}[dp] {EXCLUDE_PT}")
        pmids.update(res["idlist"])
    return pmids


def core_meta(pmids):
    """Europe PMC core metadata (abstract, authors, affiliations, MeSH, OA) by PMID."""
    meta = {}
    pmids = list(pmids)
    for i in range(0, len(pmids), 50):
        q = " OR ".join(f"EXT_ID:{p}" for p in pmids[i:i + 50]) + " AND SRC:MED"
        res = epmc(q, page_size=100, result_type="core")
        for r in res["resultList"]["result"]:
            meta[r["pmid"]] = r
    return meta


BAD_TYPES = {"Editorial", "Comment", "Letter", "News", "Published Erratum", "Retraction of Publication"}


def is_article(m):
    types = set((m.get("pubTypeList") or {}).get("pubType", []))
    return not (types & BAD_TYPES)


def row(pmid, ic, m, pool, rank=""):
    types = (m.get("pubTypeList") or {}).get("pubType", [])
    return {
        "rank": rank, "pmid": pmid, "pool": pool,
        "citations": ic.get("citation_count", ""),
        "rcr": f"{ic['relative_citation_ratio']:.1f}" if ic.get("relative_citation_ratio") else "",
        "year": ic.get("year", m.get("pubYear", "")),
        "journal": ic.get("journal", ""),
        "title": ic.get("title", m.get("title", "")),
        "n_authors": len((m.get("authorList") or {}).get("author", [])),
        "pub_types": "; ".join(types),
        "is_research_article": ic.get("is_research_article", ""),
        "open_access": m.get("isOpenAccess", ""),
        "pmcid": m.get("pmcid", ""),
        "doi": ic.get("doi", m.get("doi", "")),
    }


def save_corpus(rows, outdir):
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for r in rows:
        path = os.path.join(outdir, f"{r['pmid']}.json")
        if not r["pmcid"] or os.path.exists(path):
            n += os.path.exists(path)
            continue
        try:
            url = latest_xml(r["pmcid"])
            if not url:
                continue
            doc = parse(fetch(url, timeout=120))
        except Exception as e:  # noqa: BLE001 - keep going on any parse failure
            print(f"  full text failed for {r['pmid']}: {e}", file=sys.stderr)
            continue
        doc.update({k: r[k] for k in ("pmid", "pmcid", "title", "journal", "year", "citations")})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
        n += 1
    return n


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Pool A (core journals)...", file=sys.stderr)
    a = pool_a()
    print(f"  {len(a)} candidates", file=sys.stderr)
    print("Pool B (general journals with public health MeSH)...", file=sys.stderr)
    b = pool_b()
    print(f"  {len(b)} candidates", file=sys.stderr)
    pool_of = {p: "A" for p in a}
    pool_of.update({p: "B" for p in b if p not in pool_of})

    ic = icite(pool_of)
    ranked = sorted(ic.values(), key=lambda d: -(d.get("citation_count") or 0))
    meta = core_meta([str(d["pmid"]) for d in ranked[:200]])
    top = []
    for d in ranked:
        p = str(d["pmid"])
        if p in meta and is_article(meta[p]):
            top.append(row(p, d, meta[p], pool_of[p], rank=len(top) + 1))
        if len(top) == 100:
            break
    write_csv(os.path.join(OUT, "top100.csv"), top)
    with open(os.path.join(OUT, "top100_meta.json"), "w", encoding="utf-8") as f:
        json.dump({r["pmid"]: meta[r["pmid"]] for r in top}, f, ensure_ascii=False)
    print(f"Top 100: citations {top[-1]['citations']} to {top[0]['citations']}", file=sys.stderr)

    rng = random.Random(2026)
    top_ids = {r["pmid"] for r in top}
    picks = []
    for r in top:
        ta = r["journal"]
        filt = MESH if r["pool"] == "B" else ""
        res = esearch(f'"{ta}"[ta] AND {r["year"]}[dp] {("AND " + filt) if filt else ""} {EXCLUDE_PT}', retmax=2000)
        cands = [p for p in res["idlist"] if p not in top_ids]
        rng.shuffle(cands)
        picks.append((r["pmid"], r["pool"], cands[:6]))
    cmeta = core_meta([p for _, _, c in picks for p in c])
    cic = icite([p for _, _, c in picks for p in c])
    controls = []
    for top_pmid, pool, cands in picks:
        k = 0
        for p in cands:
            if p in cmeta and p in cic and is_article(cmeta[p]):
                c = row(p, cic[p], cmeta[p], pool)
                c["matched_to"] = top_pmid
                controls.append(c)
                k += 1
            if k == 3:
                break
    write_csv(os.path.join(OUT, "controls.csv"), controls)
    with open(os.path.join(OUT, "controls_meta.json"), "w", encoding="utf-8") as f:
        json.dump({c["pmid"]: cmeta[c["pmid"]] for c in controls}, f, ensure_ascii=False)
    print(f"Controls: {len(controls)}", file=sys.stderr)

    nt = save_corpus(top, os.path.join(OUT, "corpus"))
    nc = save_corpus(controls, os.path.join(OUT, "corpus_controls"))
    print(f"Full texts: top {nt}, controls {nc}", file=sys.stderr)


if __name__ == "__main__":
    main()
