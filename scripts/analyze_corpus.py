"""Summarise how highly cited DHS/MICS papers are written, section by section.

Reads the JSON files made by build_corpus.py and writes a Markdown report of
structure, length, statistical methods and reporting patterns. The report holds
counts and short labels only, no copied text.

Usage:
  python3 scripts/analyze_corpus.py [--corpus literature/corpus] [--out literature/corpus_analysis.md]
"""

import argparse
import collections
import glob
import json
import os
import re
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOP_JOURNALS = re.compile(r"lancet|bmj|plos medicine|jama|new england|nature medicine|"
                          r"bulletin of the world health|international journal of epidemiology", re.I)

CANON = [
    ("introduction", r"^(introduction|background)\b"),
    ("methods", r"^(materials? and methods|methods?|methodology|data and methods?|study design|subjects and methods|data)\b"),
    ("results", r"^(results?|findings)\b"),
    ("discussion", r"^discussions?\b"),
    ("conclusion", r"^(conclusions?|concluding)\b"),
    ("limitations", r"^(strengths? and limitations?|limitations?|study limitations?)\b"),
]


def canon(title):
    t = re.sub(r"^[\dIVX.\s]+", "", title.strip().lower())
    for name, pat in CANON:
        if re.match(pat, t):
            return name
    return None


def flat_text(sec):
    out = list(sec["paragraphs"])
    for s in sec["subsections"]:
        out.extend(flat_text(s))
    return out


def all_subtitles(sec):
    out = []
    for s in sec["subsections"]:
        out.append(s["title"])
        out.extend(all_subtitles(s))
    return out


def words(text):
    return len(re.findall(r"\b\w[\w'-]*\b", text))


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "n/a"


def describe(values):
    values = [v for v in values if v]
    if not values:
        return "n/a"
    q = statistics.quantiles(values, n=4) if len(values) > 1 else [values[0]] * 3
    return f"median {statistics.median(values):.0f} (IQR {q[0]:.0f} to {q[2]:.0f}; n={len(values)})"


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if s]


# Features searched for in a section's text. Each is (label, regex).
METHOD_FEATURES = [
    ("Sampling weights applied", r"\b(sampl\w* weight|survey weight|weighted|weights? (were|was) (applied|used))"),
    ("Complex survey design (cluster/strata) accounted for", r"complex (survey|sampl)|svy|primary sampling unit|\bPSU\b|stratification|clustering"),
    ("Two-stage stratified cluster sampling described", r"two[- ]stage|multi[- ]?stage|stratified (cluster )?sampl"),
    ("Response rate reported", r"response rate"),
    ("Logistic regression", r"logistic regression"),
    ("Multilevel / mixed-effects model", r"multilevel|multi-level|mixed[- ]effects?|hierarchical (model|regression)|random[- ]effects?|random intercept"),
    ("Poisson / log-binomial (prevalence ratios)", r"poisson|log[- ]binomial|prevalence ratio"),
    ("Linear regression", r"linear regression|ordinary least squares|\bOLS\b"),
    ("Survival / Cox model", r"\bcox\b|proportional hazards|survival analysis|kaplan"),
    ("Concentration index / inequality measures", r"concentration (index|curve)|slope index|relative index of inequality|equiplot"),
    ("Decomposition (e.g. Oaxaca-Blinder)", r"decomposition|oaxaca|blinder"),
    ("Propensity score / matching", r"propensity score|matching"),
    ("Spatial analysis / mapping", r"spatial|geospatial|moran|hotspot|hot spot|getis|kriging|satscan|geographic"),
    ("Trend analysis across survey rounds", r"\btrends?\b|annual (rate|change)|over time|across survey"),
    ("Wealth index / quintiles", r"wealth (index|quintile)|asset index|principal component"),
    ("Confounder selection explained", r"confound|directed acyclic|\bDAG\b|a priori|based on (the )?(literature|previous)"),
    ("Collinearity checked", r"collinearit|variance inflation|\bVIF\b"),
    ("Missing data handling described", r"missing (data|values|information)|multiple imputation|complete[- ]case"),
    ("Sensitivity analysis", r"sensitivity analys"),
    ("Interaction / effect modification tested", r"interaction|effect modification|stratified analys"),
    ("Model fit / comparison (AIC, ICC, MOR, deviance)", r"\bAIC\b|\bBIC\b|intra[- ]?class|\bICC\b|median odds ratio|\bMOR\b|deviance|log[- ]likelihood|hosmer"),
    ("Significance threshold stated", r"p\s*[<≤]\s*0?\.05|alpha|significance level|statistically significant"),
    ("Software named", r"\bstata\b|\bR\b version|R software|\bSAS\b|\bSPSS\b|R Core Team"),
    ("Outcome definition given", r"outcome (variable|measure)|dependent variable|primary outcome|was defined as|defined as"),
    ("Exposure / independent variables described", r"independent variable|explanatory variable|exposure|covariate|predictor"),
    ("Ethics: secondary data / ICF IRB approval", r"ethic|institutional review board|\bIRB\b|informed consent|ICF"),
    ("Reporting guideline cited (STROBE etc.)", r"\bSTROBE\b|\bRECORD\b|\bGATHER\b|\bCONSORT\b|\bPRISMA\b"),
    ("Data availability / public access stated", r"publicly available|available (at|from|on request)|dhsprogram\.com|measuredhs|data access"),
]

RESULT_FEATURES = [
    ("Adjusted odds ratio reported", r"\b(aOR|AOR|adjusted odds ratio)"),
    ("Odds ratio reported", r"\b(OR|odds ratio)\b"),
    ("Prevalence/risk ratio reported", r"\b(aPR|PR|RR|aRR|prevalence ratio|risk ratio|relative risk)\b"),
    ("Hazard ratio reported", r"\b(HR|aHR|hazard ratio)\b"),
    ("95% CI reported", r"95\s?%\s?(CI|confidence)"),
    ("p values reported", r"\bp\s?[=<>≤]\s?0?\.\d"),
    ("Sample size stated in Results", r"\b[nN]\s?=\s?\d|\d[\d,]* (women|children|men|households|respondents|participants|births|mothers)"),
    ("Percentages reported", r"\d+(\.\d+)?\s?%"),
    ("Refers to tables", r"\bTable\s?\d"),
    ("Refers to figures", r"\b(Figure|Fig\.?)\s?\d"),
]

DISCUSSION_FEATURES = [
    ("Opens by restating the main finding", None),
    ("Compares with previous studies", r"(previous|prior|earlier|other) (studies|study|research|findings)|consistent with|in line with|similar to|contrary to|in contrast"),
    ("Offers mechanisms / explanations", r"(may|might|could) (be )?(explain|due to|reflect|because)|possible explanation|one explanation|this may be"),
    ("Policy / programme implications", r"polic|programme|program|intervention|implication"),
    ("Strengths stated", r"strength"),
    ("Limitations stated", r"limitation"),
    ("Cross-sectional design limits causal inference", r"cross[- ]sectional.{0,80}(caus|tempor)|caus.{0,80}cross[- ]sectional|cannot (establish|infer|determine) caus|temporal"),
    ("Self-report / recall bias", r"self[- ]report|recall bias|reporting bias|social desirability"),
    ("Unmeasured / residual confounding", r"unmeasured|residual confounding|omitted variable|not (available|collected|captured)"),
    ("Generalisability discussed", r"generali[sz]ab|representative|external validity"),
    ("Future research recommended", r"future (research|studies|study)|further (research|studies)|more research"),
]

HEDGES = r"\b(may|might|could|suggests?|possibly|likely|appears?)\b"
CAUSAL = r"\b(caus(e|es|ed|ing)|leads? to|led to|results? in|resulted in|effect of|impact of|determin(e|es|ed))\b"

TABLE_KINDS = [
    ("Characteristics of sample", r"characteristic|background|socio-?demographic|description of|distribution of (the )?(study|sample|respondent)"),
    ("Prevalence / distribution of outcome", r"prevalence|proportion|percentage|distribution|coverage|rate"),
    ("Bivariate / unadjusted associations", r"bivariate|unadjusted|crude|chi[- ]?square|cross[- ]tab"),
    ("Multivariable / adjusted model", r"multivariable|multivariate|adjusted|regression|multilevel|model|factors associated|determinants|predictors|associated with"),
    ("Random effects / model fit", r"random effect|model fit|variance|intra[- ]?class"),
    ("Trends over time", r"trend|change|over time|between \d{4} and \d{4}"),
    ("Inequality measures", r"concentration|inequalit|equity|quintile"),
]

FIGURE_KINDS = [
    ("Map", r"\bmap|spatial|geographic|region|district|hot ?spot|cluster"),
    ("Flow chart of sample selection", r"flow|selection|sample size|inclusion|exclusion"),
    ("Trends over time", r"trend|over time|change|\d{4}.{0,10}\d{4}"),
    ("Forest / coefficient plot", r"forest|odds ratio|coefficient|estimates"),
    ("Inequality chart (concentration curve, equiplot, by wealth)", r"concentration|inequalit|wealth|quintile|equiplot"),
    ("Conceptual framework", r"conceptual|framework|model of|pathway|theor"),
    ("Bar chart / prevalence by group", r"prevalence|percentage|proportion|distribution|coverage"),
]


def first_sentence(paras):
    for p in paras:
        s = sentences(p)
        if s:
            return s[0]
    return ""


def opening_type(sentence):
    s = sentence.lower()
    if re.search(r"^(this|our|the present|the current|in this) (study|analysis|paper)|^we (found|show|observed)|^our (findings|results|analysis)|^(the )?(main|key|principal) (finding|result)", s):
        return "Restates own main finding"
    if re.search(r"^to (our|the best of our) knowledge|^this is the first", s):
        return "Claims novelty"
    if re.search(r"^(the )?(aim|objective|purpose)", s):
        return "Restates aim"
    return "Other (context or direct claim)"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=os.path.join(ROOT, "literature", "corpus"))
    ap.add_argument("--out", default=os.path.join(ROOT, "literature", "corpus_analysis.md"))
    args = ap.parse_args()

    docs = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(args.corpus, "*.json")))]
    research = [d for d in docs if d["article_type"] == "research-article"]
    n = len(research)
    top = [d for d in research if TOP_JOURNALS.search(d["journal"])]

    L = []
    w = L.append
    w("# How highly cited DHS and MICS papers are written")
    w("")
    w(f"Corpus: {len(docs)} open access PubMed papers that name DHS or MICS in the title or abstract "
      f"and have more than 50 citations (NIH iCite, October 2026). Analyses below use the "
      f"{n} original research articles. {len(top)} of them appeared in top general or global health "
      f"journals (Lancet family, BMJ family, PLOS Medicine, JAMA, NEJM, Bulletin of the WHO, IJE).")
    w("")
    cites = [int(d["citations"]) for d in research]
    w(f"Citations: {describe(cites)}. Publication years: {min(d['year'] for d in research)} to {max(d['year'] for d in research)}.")
    w("")
    jc = collections.Counter(d["journal"] for d in research).most_common(12)
    w("Most common journals: " + "; ".join(f"{j} ({c})" for j, c in jc) + ".")
    w("")

    # ---- Titles
    w("## Titles")
    tw = [words(d["title"]) for d in research]
    w(f"* Length: {describe(tw)} words.")
    feats = [
        ("Contains a colon (two-part title)", r":"),
        ("Names the country or region", None),
        ("Names the data source (DHS, MICS, survey)", r"demographic and health|\bDHS\b|\bMICS\b|survey|NFHS"),
        ("Names the design or method (cross-sectional, multilevel, analysis)", r"cross[- ]sectional|multilevel|multi-level|analysis|trend|decomposition|spatial|pooled"),
        ("Phrased as a question", r"\?"),
        ("Uses 'evidence from'", r"evidence from"),
        ("Uses 'factors associated' / 'determinants'", r"factors associated|determinants|correlates|predictors|risk factors"),
    ]
    for label, pat in feats:
        if pat is None:
            k = sum(1 for d in research if d["countries_in_title"] or re.search(r"africa|asia|countries|low- and middle|LMIC", d["title"], re.I))
        else:
            k = sum(1 for d in research if re.search(pat, d["title"], re.I))
        w(f"* {label}: {pct(k, n)}")
    w("")

    # ---- Abstract
    w("## Abstract")
    structured = [d for d in research if len(d["abstract"]) > 1]
    w(f"* Structured abstract: {pct(len(structured), n)} of papers.")
    heads = collections.Counter(" / ".join(re.sub(r"[:.]$", "", s["title"].strip().lower()).capitalize()
                                            for s in d["abstract"] if s["title"] and "supplementary" not in s["title"].lower())
                                for d in structured)
    w("* Most common heading sets: " + "; ".join(f"{h} ({c})" for h, c in heads.most_common(6)) + ".")
    aw = [sum(words(s["text"]) for s in d["abstract"]) for d in research if d["abstract"]]
    w(f"* Total length: {describe(aw)} words.")
    part = collections.defaultdict(list)
    for d in structured:
        for s in d["abstract"]:
            t = s["title"].lower()
            key = ("Background" if re.search(r"background|introduction|objective|context", t) else
                   "Methods" if re.search(r"method", t) else
                   "Results" if re.search(r"result|finding", t) else
                   "Conclusion" if re.search(r"conclu|interpretation", t) else None)
            if key:
                part[key].append(words(s["text"]))
    for k in ("Background", "Methods", "Results", "Conclusion"):
        w(f"* {k} part: {describe(part[k])} words.")
    abs_text = {d["pmid"]: " ".join(s["text"] for s in d["abstract"]) for d in research}
    for label, pat in [
        ("Abstract gives sample size", r"\b[nN]\s?=\s?\d|\d[\d,]{2,} (women|children|men|households|respondents|participants|births|mothers|adolescents|couples|individuals)"),
        ("Abstract names survey year(s)", r"(19|20)\d\d"),
        ("Abstract reports an effect estimate (OR/RR/HR/PR/coefficient)", r"\b(a?OR|odds ratio|a?RR|risk ratio|a?PR|prevalence ratio|a?HR|hazard ratio|coefficient|β)\b"),
        ("Abstract reports 95% CI", r"95\s?%\s?(CI|confidence)|\bCI\b"),
        ("Abstract reports p values", r"\bp\s?[=<>≤]\s?0?\.\d"),
        ("Abstract reports percentages", r"\d+(\.\d+)?\s?%"),
        ("Abstract conclusion contains a policy or action word", None),
    ]:
        if pat is None:
            k = 0
            for d in structured:
                concl = " ".join(s["text"] for s in d["abstract"] if re.search(r"conclu|interpretation", s["title"], re.I))
                if re.search(r"polic|programme|program|intervention|should|need|target|priorit", concl, re.I):
                    k += 1
            w(f"* {label}: {pct(k, len(structured))} of structured abstracts")
        else:
            k = sum(1 for d in research if re.search(pat, abs_text[d['pmid']]))
            w(f"* {label}: {pct(k, n)}")
    w("")

    # ---- Body structure
    by = {}
    for d in research:
        secs = collections.defaultdict(list)
        subs = collections.defaultdict(list)
        for s in d["sections"]:
            c = canon(s["title"])
            if c is None and re.match(r"^results? and discussion", s["title"].strip().lower()):
                c = "results"
            if c:
                secs[c].extend(flat_text(s))
                subs[c].extend(all_subtitles(s))
        for s in d.get("back_sections", []):
            c = canon(s["title"])
            if c in ("conclusion", "limitations"):
                secs[c].extend(flat_text(s))
        by[d["pmid"]] = (secs, subs)

    w("## Overall structure and length")
    order = collections.Counter()
    for d in research:
        seq = []
        for s in d["sections"]:
            c = canon(s["title"])
            if c and c not in seq:
                seq.append(c)
        order[" > ".join(seq)] += 1
    w("* Most common top-level section orders: " + "; ".join(f"{o} ({c})" for o, c in order.most_common(5)) + ".")
    for c in ("introduction", "methods", "results", "discussion", "conclusion"):
        wc = [words(" ".join(by[d["pmid"]][0][c])) for d in research if by[d["pmid"]][0][c]]
        pc = [len(by[d["pmid"]][0][c]) for d in research if by[d["pmid"]][0][c]]
        w(f"* {c.capitalize()}: {describe(wc)} words; {describe(pc)} paragraphs.")
    sepconc = sum(1 for d in research if by[d["pmid"]][0]["conclusion"])
    seplim = sum(1 for d in research if by[d["pmid"]][0]["limitations"] or
                 any(re.search(r"limitation", t, re.I) for t in by[d["pmid"]][1]["discussion"]))
    w(f"* Separate Conclusion section: {pct(sepconc, n)}. Limitations under their own heading or subheading: {pct(seplim, n)}.")
    w("")

    # ---- Introduction
    w("## Introduction")
    intro_feats = [
        ("States burden with numbers (%, rates, deaths)", r"\d+(\.\d+)?\s?%|\d[\d,]* (deaths|million|per 1000|per 1,000|per 100)|million"),
        ("Cites global targets (SDG, MDG, WHO, UN targets)", r"\bSDG|sustainable development|\bMDG|millennium development|world health assembly|global (target|strategy)|universal health coverage|\bUHC\b"),
        ("Describes evidence gap ('little is known', 'few studies')", r"little (is )?known|few studies|limited (evidence|research|data|studies)|no stud|not (been )?(well )?(studied|examined|explored|understood)|gap|lack of|scarce|paucity"),
        ("Ends with explicit aim/objective", None),
        ("Uses a theory or conceptual framework", r"framework|theor|model of|andersen|mosley|chen"),
        ("Names the country context", r"ethiopia|nigeria|bangladesh|india|kenya|ghana|nepal|pakistan|uganda|tanzania|malawi|country|countries"),
    ]
    with_intro = [d for d in research if by[d["pmid"]][0]["introduction"]]
    for label, pat in intro_feats:
        if pat is None:
            k = 0
            for d in with_intro:
                last = by[d["pmid"]][0]["introduction"][-1]
                if re.search(r"\b(aim|objective|purpose|goal|we (examine|assess|investigate|estimate|explore|analy[sz]e|describe|quantif)|this (study|paper|analysis) (examine|assess|investigate|estimate|explore|analy[sz]e|describe|quantif|seeks|aims))", last, re.I):
                    k += 1
            w(f"* {label} (in the last paragraph): {pct(k, len(with_intro))}")
        else:
            k = sum(1 for d in with_intro if re.search(pat, " ".join(by[d['pmid']][0]['introduction']), re.I))
            w(f"* {label}: {pct(k, len(with_intro))}")
    w("")

    # ---- Methods
    w("## Methods")
    with_m = [d for d in research if by[d["pmid"]][0]["methods"]]
    sub = collections.Counter()
    for d in with_m:
        seen = set()
        for t in by[d["pmid"]][1]["methods"]:
            t = re.sub(r"^[\d.\s]+", "", t.strip().lower()).rstrip(":.")
            t = re.sub(r"\s+", " ", t)
            if t and t not in seen:
                seen.add(t)
                sub[t] += 1
    with_sub = sum(1 for d in with_m if by[d["pmid"]][1]["methods"])
    w(f"* Methods split into subheadings: {pct(with_sub, len(with_m))}.")
    w("* Most common Methods subheadings: " + "; ".join(f"{t} ({c})" for t, c in sub.most_common(25)) + ".")
    w("")
    w("### Methods content (share of papers whose Methods mention each item)")
    w("")
    w("| Item | All papers | Top journals |")
    w("| --- | --- | --- |")
    top_ids = {d["pmid"] for d in top}
    with_m_top = [d for d in with_m if d["pmid"] in top_ids]
    for label, pat in METHOD_FEATURES:
        rx = re.compile(pat, re.I if "\\bR\\b" not in pat else 0)
        k = sum(1 for d in with_m if rx.search(" ".join(by[d['pmid']][0]['methods'])))
        kt = sum(1 for d in with_m_top if rx.search(" ".join(by[d['pmid']][0]['methods'])))
        w(f"| {label} | {pct(k, len(with_m))} | {pct(kt, len(with_m_top))} |")
    w("")
    soft = collections.Counter()
    for d in with_m:
        t = " ".join(by[d["pmid"]][0]["methods"])
        for name, pat in [("Stata", r"\bstata\b"), ("R", r"\bR (software|version|statistical|Core|package|\d)|R Core Team"),
                          ("SAS", r"\bSAS\b"), ("SPSS", r"\bSPSS\b"), ("ArcGIS/QGIS", r"arcgis|qgis"),
                          ("SaTScan", r"satscan"), ("MLwiN", r"mlwin")]:
            if re.search(pat, t, re.I if name not in ("R", "SAS", "SPSS") else 0):
                soft[name] += 1
    w("* Software named: " + "; ".join(f"{s} {pct(c, len(with_m))}" for s, c in soft.most_common()) + ".")
    w("")

    # ---- Results
    w("## Results")
    with_r = [d for d in research if by[d["pmid"]][0]["results"]]
    w("| Item | Share of papers |")
    w("| --- | --- |")
    for label, pat in RESULT_FEATURES:
        k = sum(1 for d in with_r if re.search(pat, " ".join(by[d['pmid']][0]['results'])))
        w(f"| {label} | {pct(k, len(with_r))} |")
    rsub = collections.Counter()
    for d in with_r:
        for t in set(re.sub(r"^[\d.\s]+", "", x.strip().lower()).rstrip(":.") for x in by[d["pmid"]][1]["results"]):
            if t:
                rsub[t] += 1
    w("")
    w("* Results split into subheadings: " + pct(sum(1 for d in with_r if by[d['pmid']][1]['results']), len(with_r)) + ".")
    w("* Most common Results subheadings: " + "; ".join(f"{t} ({c})" for t, c in rsub.most_common(15)) + ".")
    first = collections.Counter()
    for d in with_r:
        s = first_sentence(by[d["pmid"]][0]["results"]).lower()
        if re.search(r"table 1|characteristic|sample|respondent|participants|women|children|total of|included", s):
            first["Describes the sample (often citing Table 1)"] += 1
        elif re.search(r"prevalence|proportion|percent|%", s):
            first["Reports overall prevalence"] += 1
        else:
            first["Other"] += 1
    w("* First Results sentence: " + "; ".join(f"{k} {pct(v, len(with_r))}" for k, v in first.most_common()) + ".")
    w("")

    # ---- Tables and figures
    w("## Tables and figures")
    nt = [len(d["tables"]) for d in research]
    nf = [len(d["figures"]) for d in research]
    w(f"* Tables per paper: median {statistics.median(nt):.0f} (IQR {statistics.quantiles(nt, n=4)[0]:.0f} to {statistics.quantiles(nt, n=4)[2]:.0f}). "
      f"Figures per paper: median {statistics.median(nf):.0f} (IQR {statistics.quantiles(nf, n=4)[0]:.0f} to {statistics.quantiles(nf, n=4)[2]:.0f}).")
    cw = [words(t["caption"]) for d in research for t in d["tables"] if t["caption"]]
    w(f"* Table caption length: {describe(cw)} words.")
    fw = [words(t["caption"]) for d in research for t in d["figures"] if t["caption"]]
    w(f"* Figure caption length: {describe(fw)} words.")
    foot = [d for d in research if d["table_footnotes"]]
    w(f"* Papers with table footnotes: {pct(len(foot), n)}. Footnotes defining abbreviations: "
      f"{pct(sum(1 for d in foot if re.search(r'abbreviation|OR,|CI,|AOR', ' '.join(d['table_footnotes']))), len(foot))}; "
      f"stating adjustment variables: {pct(sum(1 for d in foot if re.search(r'adjusted for|controlled for|model (included|adjusts)', ' '.join(d['table_footnotes']), re.I)), len(foot))}; "
      f"marking significance with symbols: {pct(sum(1 for d in foot if re.search(r'[*†‡]|p\s?<', ' '.join(d['table_footnotes']))), len(foot))}.")
    w("")
    w("Table content by position (share of papers that have that table):")
    w("")
    w("| Table | " + " | ".join(k for k, _ in TABLE_KINDS) + " |")
    w("| --- |" + " --- |" * len(TABLE_KINDS))
    for i in range(4):
        have = [d for d in research if len(d["tables"]) > i]
        row = [pct(sum(1 for d in have if re.search(p, d["tables"][i]["caption"], re.I)), len(have)) for _, p in TABLE_KINDS]
        w(f"| Table {i + 1} (n={len(have)}) | " + " | ".join(row) + " |")
    w("")
    fk = collections.Counter()
    for d in research:
        kinds = set()
        for f in d["figures"]:
            for k, p in FIGURE_KINDS:
                if re.search(p, f["caption"], re.I):
                    kinds.add(k)
                    break
        fk.update(kinds)
    with_fig = sum(1 for d in research if d["figures"])
    w("* Figure types used (share of papers with any figure; first matching type per figure): " +
      "; ".join(f"{k} {pct(v, with_fig)}" for k, v in fk.most_common()) + ".")
    w("")

    # ---- Discussion
    w("## Discussion")
    with_d = [d for d in research if by[d["pmid"]][0]["discussion"]]
    op = collections.Counter(opening_type(first_sentence(by[d["pmid"]][0]["discussion"])) for d in with_d)
    w("* Opening sentence: " + "; ".join(f"{k} {pct(v, len(with_d))}" for k, v in op.most_common()) + ".")
    w("")
    w("| Item | Share of papers |")
    w("| --- | --- |")
    for label, pat in DISCUSSION_FEATURES:
        if pat is None:
            continue
        k = 0
        for d in with_d:
            t = " ".join(by[d["pmid"]][0]["discussion"] + by[d["pmid"]][0]["limitations"])
            if re.search(pat, t, re.I):
                k += 1
        w(f"| {label} | {pct(k, len(with_d))} |")
    w("")
    hedge_rates, causal_rates = [], []
    for d in with_d:
        t = " ".join(by[d["pmid"]][0]["discussion"])
        nw = max(words(t), 1)
        hedge_rates.append(1000 * len(re.findall(HEDGES, t, re.I)) / nw)
        causal_rates.append(1000 * len(re.findall(CAUSAL, t, re.I)) / nw)
    w(f"* Hedging words (may, might, could, suggest, likely) per 1,000 Discussion words: median {statistics.median(hedge_rates):.1f}. "
      f"Causal verbs (cause, lead to, result in, effect of, impact of, determine): median {statistics.median(causal_rates):.1f}.")
    lim_pos = collections.Counter()
    for d in with_d:
        paras = by[d["pmid"]][0]["discussion"]
        idx = [i for i, p in enumerate(paras) if re.search(r"limitation", p, re.I)]
        if not idx:
            lim_pos["Not in Discussion text"] += 1
        elif idx[0] >= len(paras) - 3:
            lim_pos["Near the end (last three paragraphs)"] += 1
        else:
            lim_pos["Earlier in the Discussion"] += 1
    w("* Where limitations appear: " + "; ".join(f"{k} {pct(v, len(with_d))}" for k, v in lim_pos.most_common()) + ".")
    w("")

    # ---- Conclusion
    w("## Conclusion")
    with_c = [d for d in research if by[d["pmid"]][0]["conclusion"]]
    cw = [words(" ".join(by[d["pmid"]][0]["conclusion"])) for d in with_c]
    w(f"* Length when a separate section exists: {describe(cw)} words.")
    for label, pat in [
        ("Restates the main finding", r"(this|our|the present) (study|analysis)|we found|found that|findings|results (show|suggest|indicate)"),
        ("Gives policy or programme recommendation", r"polic|programme|program|intervention|should|need|priorit|target"),
        ("Calls for further research", r"further (research|stud)|future (research|stud)"),
        ("Uses causal language", CAUSAL),
        ("Reports numbers again", r"\d+(\.\d+)?\s?%|\bOR\b|95\s?%"),
    ]:
        k = sum(1 for d in with_c if re.search(pat, " ".join(by[d['pmid']][0]['conclusion']), re.I))
        w(f"* {label}: {pct(k, len(with_c))}")
    w("")

    # ---- Back matter
    w("## Declarations and back matter")
    back = {d["pmid"]: " ".join(" ".join(flat_text(s)) + " " + s["title"] for s in d.get("back_sections", [])) for d in research}
    full = {d["pmid"]: back[d["pmid"]] + " " + " ".join(" ".join(flat_text(s)) + " " + s["title"] for s in d["sections"]) for d in research}
    for label, pat in [
        ("Ethics statement", r"ethic|institutional review|informed consent"),
        ("Data availability statement", r"data (availability|access|sharing)|publicly available|available (from|at|on)"),
        ("Competing interests", r"competing interest|conflict of interest|declaration of interest"),
        ("Funding statement", r"\bfund"),
        ("Author contributions", r"contribution"),
        ("Acknowledges DHS Program / ICF / UNICEF for data", r"(dhs program|measure dhs|icf|macro international|unicef).{0,80}(data|access|permission|provid)|(data|access|permission|provid).{0,80}(dhs program|measure dhs|icf|macro international|unicef)"),
    ]:
        k = sum(1 for d in research if re.search(pat, full[d['pmid']], re.I))
        w(f"* {label}: {pct(k, n)}")
    nr = [d["n_references"] for d in research if d["n_references"]]
    w(f"* References: {describe(nr)}.")
    w("")

    # ---- Exemplars
    w("## Most cited papers in the corpus")
    w("")
    w("| Citations | Year | Journal | Title | PMID |")
    w("| --- | --- | --- | --- | --- |")
    for d in sorted(research, key=lambda d: -int(d["citations"]))[:30]:
        w(f"| {d['citations']} | {d['year']} | {d['journal']} | {d['title']} | {d['pmid']} |")
    w("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
