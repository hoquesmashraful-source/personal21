#!/usr/bin/env python3
"""Score a draft on the features that separate the most cited public health papers.

Compares a manuscript's title, abstract and body with two reference groups:
the 100 most cited public health articles (2000 to 2024) and 300 matched
controls drawn from the same journals and years. The rates come from that
comparison. They describe association, not cause: a feature common in highly
cited papers is worth considering, not a guarantee of citations.

Reads .md, .txt or .docx. The title is the first heading or the first
non-empty line, unless --title is given. The abstract is the section headed
Abstract or Summary.

Usage:
  python3 citability_check.py draft.docx
  python3 citability_check.py draft.md --title "Trends in ... in 54 countries, 2000 to 2022"
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_manuscript import read_text, split_sections, words  # noqa: E402

# feature: (top-100 rate, control rate) in percent, from literature/top_cited/analysis.md
RATES = {
    "title_colon": (65, 44),
    "title_scope": (43, 15),
    "title_scale": (19, 3),
    "title_time": (30, 5),
    "title_question": (1, 5),
    "abs_structured": (71, 32),
    "abs_uncertainty": (44, 20),
    "abs_countries": (23, 6),
    "abs_large_n": (45, 11),
    "abs_reusable": (38, 11),
    "body_uncertainty": (70, 16),
    "body_sharing": (42, 20),
    "body_limitations": (79, 44),
    "figs_gt_tables": (84, 57),
}
SCALE = r"\b\d[\d,.]*\s+(?:[\w-]+\s+){0,4}(countries|studies|million|participants|people|surveys|cohorts|adults|children|women|men)\b"
MANY_COUNTRIES = r"\b([1-9]\d|\d{3,})\s+(?:[\w-]+\s+){0,4}(countries|nations|territories)\b"
NUMBER = r"\b\d+(?:\.\d+)?\b"
MEDIANS = {"title_words": (13.5, 10), "abs_words": (322, 257), "abs_numbers": (9.5, 6.3),
           "figures": (5, 2), "tables": (2, 1), "references": (60, 34)}


def find_title(text):
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            return s.lstrip("#").strip()
        return s
    return ""


def yes(flag):
    return "yes" if flag else "no"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--title")
    args = ap.parse_args()

    text = read_text(args.path)
    secs = split_sections(text)
    title = args.title or find_title(text)
    abstract = secs.get("abstract", "")
    body = " ".join(v for k, v in secs.items() if k not in ("abstract", "references"))

    rows = []

    def add(label, value, key, advice):
        if key in RATES:
            t, c = RATES[key]
            ref = f"{t}% / {c}%"
        else:
            t, c = MEDIANS[key]
            ref = f"median {t:g} / {c:g}"
        rows.append((label, value, ref, advice))

    t = title
    add("Title words", str(words(t)), "title_words", "Top titles are longer because they state scope, scale and period.")
    add("Title has a colon (topic: design or scale)", yes(":" in t), "title_colon", "Use 'Topic in population: design or scale'.")
    add("Title names global, regional or multi-country scope", yes(re.search(r"global|world|countries|international|nations|regional|national", t, re.I)), "title_scope", "Name the population and setting the estimate covers.")
    add("Title states scale (number of countries, studies, people)", yes(re.search(SCALE, t, re.I)), "title_scale", "If the scale is a strength, put the number in the title.")
    add("Title states a time span or trend", yes(re.search(r"trend|since|from (19|20)\d\d|(19|20)\d\d.{0,6}(to|-).{0,6}(19|20)\d\d", t, re.I)), "title_time", "Give the period for estimates and trends.")
    add("Title is a question", yes("?" in t), "title_question", "Top papers almost never use question titles.")

    if abstract:
        nw = max(words(abstract), 1)
        add("Abstract words", str(nw), "abs_words", "Journal limits come first.")
        add("Abstract is structured", yes(re.search(r"^\s*(\*\*|#+\s*)?(Background|Objective|Methods|Findings|Results|Interpretation|Conclusions?)\b", abstract, re.I | re.M)), "abs_structured", "Use the target journal's headings.")
        add("Numbers per 100 abstract words", f"{100 * len(re.findall(NUMBER, abstract)) / nw:.1f}", "abs_numbers", "Give the headline estimates, not only directions.")
        add("Abstract reports a CI or uncertainty interval", yes(re.search(r"95\s?%|\bCI\b|\bUI\b|uncertainty interval", abstract)), "abs_uncertainty", "Every headline number needs its interval.")
        add("Abstract names 10 or more countries", yes(re.search(MANY_COUNTRIES, abstract)), "abs_countries", "Only if true: state breadth explicitly.")
        add("Abstract mentions a sample of 100,000 or more", yes(re.search(r"\b\d{3},\d{3}|\b\d{3} \d{3}|\b\d+(\.\d+)? million\b", abstract)), "abs_large_n", "Only if true: state the size.")
        add("Abstract offers something reusable", yes(re.search(r"we (propose|present|developed|describe|provide)|framework|tool|estimates (for|of)|freely available|publicly available|data (are|is) available|online|code", abstract, re.I)), "abs_reusable", "Say what others can reuse: estimates, a tool, a framework, data or code.")
    else:
        rows.append(("Abstract", "not found", "", "Add a heading 'Abstract' so it can be checked."))

    figs = {int(n) for n in re.findall(r"\b(?:Figure|Fig\.?)\s?(\d+)", body)}
    tabs = {int(n) for n in re.findall(r"\bTable\s?(\d+)", body)}
    add("Figures referred to", str(max(figs) if figs else 0), "figures", "Top papers carry their main findings in figures.")
    add("Tables referred to", str(max(tabs) if tabs else 0), "tables", "Move long tables to the appendix.")
    add("More figures than tables", yes(len(figs) > len(tabs)), "figs_gt_tables", "Consider turning a results table into a figure.")
    add("Uncertainty intervals, bootstrap or Bayesian intervals in text", yes(re.search(r"uncertainty interval|\bUI\b|bootstrap|bayesian|posterior|credible interval|95\s?%\s?CI", body, re.I)), "body_uncertainty", "Report uncertainty for every estimate.")
    add("Code or data availability stated", yes(re.search(r"github|osf\.io|zenodo|code (is|are|will be) available|data (are|is|will be) (publicly )?available|publicly available|data availability|data sharing", body, re.I)), "body_sharing", "Share code and data, or say how to get them.")
    add("Limitations discussed", yes(re.search(r"limitation", body, re.I)), "body_limitations", "Name the main limitations and their likely effect.")
    refs = secs.get("references", "")
    nref = len([l for l in refs.splitlines() if re.match(r"\s*(\[?\d+[\].]|\d+\s)", l)])
    if nref:
        add("References", str(nref), "references", "Top papers cite broadly (median 60).")

    print(f"# Citability check: {args.path}\n")
    print(f"Title: {title or '(not found)'}\n")
    print("| Feature | Your draft | Top 100 / typical | Suggestion |")
    print("| --- | --- | --- | --- |")
    for r in rows:
        print("| " + " | ".join(r) + " |")
    print("\nRates compare the 100 most cited public health papers with matched papers from the "
          "same journals and years. They show association, not cause; follow them only where they "
          "fit the study honestly.")


if __name__ == "__main__":
    sys.exit(main())
