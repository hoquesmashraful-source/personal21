"""Compare the 100 most cited public health articles with matched controls.

Reads literature/top_cited/ (made by build_top_cited.py) and writes
literature/top_cited/analysis.md: what kind of contribution the top papers
make, their scale, authorship, access, titles, abstracts, structure, figures
and language, each set against typical papers from the same journal and year.

Usage:
  python3 scripts/analyze_top_cited.py
"""

import collections
import csv
import glob
import html
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_corpus import canon, flat_text, FIGURE_KINDS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "literature", "top_cited")

CONTRIBUTION = [
    ("Reporting guideline, statement or consensus",
     r"\b(statement|guideline|guidance|checklist|reporting|consensus|recommendation|explanation and elaboration|STROBE|CONSORT|PRISMA|RECORD|GATHER)\b"),
    ("Cohort profile or data resource",
     r"cohort profile|data resource|profile:|study profile|database|biobank|survey design|surveillance system"),
    ("Method, measure, tool or framework",
     r"\b(method|methods|framework|index|scale|instrument|measure|measuring|measurement|validation|validity|approach|tutorial|estimator|model for|mendelian randomi[sz]ation|calculator|questionnaire|tool|primer|guide to)\b"),
    ("Global, national or multi-country estimates and trends",
     r"\b(global|worldwide|world|national|countries|trends|estimates|burden|pooled analysis|prevalence of|since 19|from 19\d\d to|19\d\d.{0,6}20\d\d|20\d\d.{0,6}20\d\d)\b"),
    ("Systematic review or meta-analysis", r"systematic review|meta-analy|meta analy|umbrella review|scoping review"),
    ("Trial or intervention evaluation", r"\b(trial|randomi[sz]ed|intervention|programme evaluation|program evaluation)\b"),
    ("Theory, concept or commentary-style analysis", r"\b(theor|concept|fundamental cause|framework for understanding|lecture|essay|perspective)\b"),
]


# A number followed, within four words, by a unit of scale ("54 low-income and
# middle-income countries", "1.2 million adults", "120 national surveys").
SCALE = r"\b\d[\d,.]*\s+(?:[\w-]+\s+){0,4}(countries|studies|million|participants|people|surveys|cohorts|adults|children|women|men)\b"
MANY_COUNTRIES = r"\b([1-9]\d|\d{3,})\s+(?:[\w-]+\s+){0,4}(countries|nations|territories)\b"


def load(name):
    with open(os.path.join(D, f"{name}.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(os.path.join(D, f"{name}_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return rows, meta


def abstract_text(m):
    raw = m.get("abstractText") or ""
    return html.unescape(re.sub(r"<[^>]+>", " ", raw)).strip()


def structured(m):
    raw = m.get("abstractText") or ""
    return bool(re.search(r"<h4>|^(BACKGROUND|OBJECTIVE|INTRODUCTION|METHODS?)\b|\b(Background|Methods|Findings|Results|Interpretation|Conclusions?)\s*:", raw))


def words(t):
    return len(re.findall(r"\d+(?:[.,]\d+)*%?|[^\W\d_][\w'-]*", t))


def sentences(t):
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\b(et al|e\.g|i\.e|vs|Fig|no)\.", lambda m: m.group(0).replace(".", "§"), t)
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", t) if s.strip()]


def contribution(row, m):
    text = f"{row['title']} {' '.join((m.get('pubTypeList') or {}).get('pubType', []))}"
    for label, pat in CONTRIBUTION:
        if re.search(pat, text, re.I):
            return label
    return "Original research finding (single setting or question)"


def consortium(m):
    authors = (m.get("authorList") or {}).get("author", [])
    return any("collectiveName" in a for a in authors) or bool(re.search(r"collaborat|consortium|group|network|investigators", m.get("authorString", ""), re.I))


def countries_named(text):
    return len(re.findall(r"\b\d{2,3} (?:low|middle|high|countries|nations|territories|LMICs)", text))


def med(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else float("nan")


def pct(flags):
    flags = list(flags)
    return 100 * sum(flags) / len(flags) if flags else float("nan")


def fmt_row(label, t, c, kind):
    if kind == "pct":
        return f"| {label} | {t:.0f}% | {c:.0f}% |"
    return f"| {label} | {t:.0f} | {c:.0f} |"


def language(texts):
    allsent = [s for t in texts for s in sentences(t)]
    wc = [words(s) for s in allsent]
    joined = " ".join(texts)
    nw = max(words(joined), 1)
    return {
        "Mean sentence length (words)": statistics.mean(wc) if wc else float("nan"),
        "Sentences of 30+ words (%)": 100 * sum(w >= 30 for w in wc) / len(wc) if wc else float("nan"),
        "'We' or 'our' per 1,000 words": 1000 * len(re.findall(r"\b(we|our)\b", joined, re.I)) / nw,
        "Passive constructions per 1,000 words": 1000 * len(re.findall(r"\b(was|were|is|are|been|be)\s+\w+ed\b", joined, re.I)) / nw,
        "Hedges per 1,000 words": 1000 * len(re.findall(r"\b(may|might|could|suggest\w*|likely|possibl\w+|appear\w*)\b", joined, re.I)) / nw,
        # "causes of death" is a noun phrase, not a causal claim, so it is not counted.
        "Causal verbs per 1,000 words": 1000 * len(re.findall(r"\b(caused|causing|causes? (?!of\b)|leads? to|led to|results? in|resulted in|impacts? (on|of))", joined, re.I)) / nw,
        "Numbers per 1,000 words": 1000 * len(re.findall(r"\b\d+(?:\.\d+)?\b", joined)) / nw,
        "Stock transitions per 1,000 words": 1000 * len(re.findall(r"\b(Furthermore|Moreover|Additionally|In addition)\b", joined)) / nw,
    }


def fulltext(folder):
    docs = {}
    for p in glob.glob(os.path.join(D, folder, "*.json")):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        docs[d["pmid"]] = d
    return docs


def section_words(doc):
    out = collections.defaultdict(int)
    for s in doc["sections"]:
        c = canon(s["title"])
        if c:
            out[c] += words(" ".join(flat_text(s)))
    return out


def main():
    top, tmeta = load("top100")
    ctl_all, cmeta = load("controls")
    # Controls without an abstract are mostly news, obituaries and commentary,
    # not comparable articles, so they are left out of the comparison.
    ctl = [r for r in ctl_all if abstract_text(cmeta.get(r["pmid"], {}))]
    L = []
    w = L.append
    cites = [int(r["citations"]) for r in top]
    ccites = [int(r["citations"] or 0) for r in ctl]
    w("# Why the most cited public health articles are cited")
    w("")
    w(f"Top 100: the most cited public health articles published 2000 to 2024 "
      f"(NIH iCite citation counts, October 2026; definition in scripts/build_top_cited.py). "
      f"Controls: {len(ctl)} articles with an abstract, drawn at random from the same journal "
      f"and year ({len(ctl_all) - len(ctl)} items without an abstract, mostly news and commentary, "
      f"were dropped).")
    w("")
    w(f"* Citations, top 100: median {med(cites):.0f} (range {min(cites)} to {max(cites)}). "
      f"Controls: median {med(ccites):.0f}.")
    rcr = [float(r["rcr"]) for r in top if r["rcr"]]
    w(f"* Relative citation ratio, top 100: median {med(rcr):.0f} (1 = NIH median).")
    years = collections.Counter((int(r["year"]) // 5) * 5 for r in top)
    w("* Publication period: " + "; ".join(f"{y} to {y + 4}: {n}" for y, n in sorted(years.items())) + ".")
    jc = collections.Counter(r["journal"] for r in top).most_common(12)
    w("* Journals: " + "; ".join(f"{j} ({n})" for j, n in jc) + ".")
    w("")

    w("## What kind of contribution earns citations")
    w("")
    w("| Contribution type | Top 100 | Controls |")
    w("| --- | --- | --- |")
    ct = collections.Counter(contribution(r, tmeta.get(r["pmid"], {})) for r in top)
    cc = collections.Counter(contribution(r, cmeta.get(r["pmid"], {})) for r in ctl)
    for label in [c[0] for c in CONTRIBUTION] + ["Original research finding (single setting or question)"]:
        w(f"| {label} | {ct[label]}% | {100 * cc[label] / len(ctl):.0f}% |")
    w("")
    w("Classification is rule-based on title and publication type (first matching rule wins); "
      "treat it as approximate.")
    w("")

    def feats(rows, meta):
        out = collections.defaultdict(list)
        for r in rows:
            m = meta.get(r["pmid"], {})
            ab = abstract_text(m)
            t = r["title"]
            out["Open access"].append(str(r["open_access"]).upper() == "Y")
            out["Consortium or collaborative group author"].append(consortium(m))
            out["Authors"].append(int(r["n_authors"] or 0))
            out["Title words"].append(words(t))
            out["Title has a colon"].append(":" in t)
            out["Title names global, world or many countries"].append(bool(re.search(r"global|world|countries|international|nations", t, re.I)))
            out["Title states scale (number of countries, studies or people)"].append(bool(re.search(SCALE, t, re.I)))
            out["Title states time span or trend"].append(bool(re.search(r"trend|since|from (19|20)\d\d|(19|20)\d\d.{0,4}(to|-|–).{0,4}(19|20)\d\d", t, re.I)))
            out["Title is a question"].append("?" in t)
            out["Abstract words"].append(words(ab) if ab else None)
            if ab:
                out["Structured abstract (papers with an abstract)"].append(structured(m))
            out["Abstract numbers per 100 words"].append(100 * len(re.findall(r"\b\d+(?:\.\d+)?\b", ab)) / max(words(ab), 1) if ab else None)
            if ab:
                out["Abstract reports a CI or uncertainty interval"].append(bool(re.search(r"95\s?%|\bCI\b|\bUI\b|uncertainty interval", ab)))
            if ab:
                out["Abstract names many countries (10 or more)"].append(bool(re.search(MANY_COUNTRIES, ab)))
            if ab:
                out["Abstract mentions a large sample (100,000 or more)"].append(bool(re.search(r"\b\d{3},\d{3}|\b\d+(\.\d+)? million\b", ab)))
            if ab:
                out["Abstract offers something reusable (tool, framework, estimates, data)"].append(bool(re.search(r"we (propose|present|developed|describe|provide)|framework|tool|estimates (for|of)|freely available|publicly available|open access|data (are|is) available|online", ab, re.I)))
            grants = (m.get("grantsList") or {}).get("grant", [])
            out["Funded (any grant listed)"].append(bool(grants))
            out["Funders listed"].append(len(grants))
            out["Has supplementary material"].append(m.get("hasSuppl") == "Y")
        return out

    ft, fc = feats(top, tmeta), feats(ctl, cmeta)
    w("## Article features: top 100 versus controls")
    w("")
    w("| Feature | Top 100 | Controls |")
    w("| --- | --- | --- |")
    for k in ft:
        kind = "pct" if isinstance(ft[k][0], bool) else "num"
        if kind == "pct":
            w(fmt_row(k, pct(ft[k]), pct(fc[k]), "pct"))
        else:
            w(f"| {k} (median) | {med(ft[k]):.1f} | {med(fc[k]):.1f} |")
    w("")

    keep = {r["pmid"] for r in ctl}
    tdocs = fulltext("corpus")
    cdocs = {k: v for k, v in fulltext("corpus_controls").items() if k in keep}
    w("## Full-text structure (open access subset)")
    w("")
    w(f"Full texts parsed: {len(tdocs)} top articles and {len(cdocs)} controls.")
    w("")
    w("| Feature | Top 100 | Controls |")
    w("| --- | --- | --- |")

    def ftfeats(docs):
        out = collections.defaultdict(list)
        for d in docs.values():
            sw = section_words(d)
            for k in ("introduction", "methods", "results", "discussion", "conclusion"):
                if sw.get(k):
                    out[f"{k.capitalize()} words"].append(sw[k])
            out["Figures"].append(len(d["figures"]))
            out["Tables"].append(len(d["tables"]))
            out["References"].append(d["n_references"] or None)
            out["Figures outnumber tables"].append(len(d["figures"]) > len(d["tables"]))
            body = " ".join(" ".join(flat_text(s)) for s in d["sections"])
            out["Panel or box (e.g. Research in context)"].append(bool(re.search(r"research in context|panel \d|box \d|what is already known|key points", body, re.I)))
            out["Sensitivity analysis reported"].append(bool(re.search(r"sensitivity analys", body, re.I)))
            out["Uncertainty intervals or bootstrap"].append(bool(re.search(r"uncertainty interval|\bUI\b|bootstrap|bayesian|posterior|credible interval", body, re.I)))
            out["Code or data shared"].append(bool(re.search(r"github|code (is|are) available|available (at|from) http|data (are|is) available|publicly available", body, re.I)))
            out["Limitations discussed"].append(bool(re.search(r"limitation", body, re.I)))
        return out

    tf, cf = ftfeats(tdocs), ftfeats(cdocs)
    for k in tf:
        if isinstance(tf[k][0], bool):
            w(fmt_row(k, pct(tf[k]), pct(cf.get(k, [])), "pct"))
        else:
            w(f"| {k} (median) | {med(tf[k]):.0f} | {med(cf.get(k, [None])):.0f} |")
    w("")

    def fig_kinds(docs):
        cnt, n = collections.Counter(), 0
        for d in docs.values():
            if not d["figures"]:
                continue
            n += 1
            kinds = set()
            for f in d["figures"]:
                for k, p in FIGURE_KINDS:
                    if re.search(p, f["caption"], re.I):
                        kinds.add(k)
                        break
            cnt.update(kinds)
        return cnt, n

    tk, tn = fig_kinds(tdocs)
    ck, cn = fig_kinds(cdocs)
    w("Figure types (share of papers with any figure):")
    w("")
    w("| Figure type | Top 100 | Controls |")
    w("| --- | --- | --- |")
    for k, _ in FIGURE_KINDS:
        w(f"| {k} | {100 * tk[k] / max(tn, 1):.0f}% | {100 * ck[k] / max(cn, 1):.0f}% |")
    capt = [words(f["caption"]) for d in tdocs.values() for f in d["figures"] if f["caption"]]
    capc = [words(f["caption"]) for d in cdocs.values() for f in d["figures"] if f["caption"]]
    w("")
    w(f"* Figure caption length: top median {med(capt):.0f} words; controls {med(capc):.0f}.")
    w("")

    w("## Language (abstracts)")
    w("")
    w("| Measure | Top 100 | Controls |")
    w("| --- | --- | --- |")
    lt = language([abstract_text(tmeta.get(r["pmid"], {})) for r in top])
    lc = language([abstract_text(cmeta.get(r["pmid"], {})) for r in ctl])
    for k in lt:
        w(f"| {k} | {lt[k]:.1f} | {lc[k]:.1f} |")
    w("")
    w("## Language (Discussion sections, open access subset)")
    w("")
    w("| Measure | Top 100 | Controls |")
    w("| --- | --- | --- |")

    def disc(docs):
        out = []
        for d in docs.values():
            for s in d["sections"]:
                if canon(s["title"]) == "discussion":
                    out.append(" ".join(flat_text(s)))
        return out

    dt, dc = language(disc(tdocs)), language(disc(cdocs))
    for k in dt:
        w(f"| {k} | {dt[k]:.1f} | {dc[k]:.1f} |")
    w("")

    w("## The top 100")
    w("")
    w("| Rank | Citations | Year | Journal | Title | Type | PMID |")
    w("| --- | --- | --- | --- | --- | --- | --- |")
    for r in top:
        w(f"| {r['rank']} | {r['citations']} | {r['year']} | {r['journal']} | {r['title']} | "
          f"{contribution(r, tmeta.get(r['pmid'], {}))} | {r['pmid']} |")
    w("")
    with open(os.path.join(D, "analysis.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"Wrote {os.path.join(D, 'analysis.md')}")


if __name__ == "__main__":
    main()
