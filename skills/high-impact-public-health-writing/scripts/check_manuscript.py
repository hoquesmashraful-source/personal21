#!/usr/bin/env python3
"""Check a public health manuscript draft for reporting gaps and style problems.

Reads .md, .txt or .docx. Splits the text into sections by heading, then
reports problems that reviewers at high-impact journals commonly flag:

  Style      sentences of 30+ words, em/en dashes and double hyphens,
             overused transitions (Furthermore, Moreover, Additionally)
  Reporting  effect estimates without 95% CIs, "p = 0.000", interpretation
             in Results, numbers repeated in the Conclusion, causal verbs
  Methods    survey weights, clustering, response rate, missing data,
             software, ethics, reporting guideline (STROBE)
  Length     section word counts against the 100 most cited public health papers

The checks are heuristics. Read each flag in context before changing text.

Usage:
  python3 check_manuscript.py draft.docx
  python3 check_manuscript.py draft.md --section discussion
  python3 check_manuscript.py draft.md --design cross-sectional --max-sentence 30
"""

import argparse
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

# Word counts (median, IQR) from the open access subset of the 100 most cited
# public health articles, 2000 to 2024 (abstracts from 92 articles; sections
# from about 38). Many are Global Burden of Disease papers with long Methods and
# Results, so journal word limits take priority over these figures.
BENCHMARKS = {
    "abstract": (322, 240, 472),
    "introduction": (492, 395, 782),
    "methods": (2112, 1175, 3573),
    "results": (2816, 1533, 5250),
    "discussion": (2357, 1358, 3998),
    "conclusion": (150, 63, 268),
}

HEADINGS = [
    ("abstract", r"(summary|abstract)"),
    ("introduction", r"(introduction|background)"),
    ("methods", r"(materials? and methods|methods?|methodology|data and methods?)"),
    ("results", r"(results?|findings)"),
    ("discussion", r"discussions?"),
    ("limitations", r"(strengths? and limitations?|limitations?)"),
    ("conclusion", r"(conclusions?|conclusion and recommendations?)"),
    ("references", r"(references|bibliography)"),
]

CAUSAL = r"\b(caus(e|es|ed|ing)|leads? to|led to|results? in|resulted in|effects? (of|on)|impacts? (of|on)|ha(s|d|ve) an? (\w+ )?(effect|impact)|influenc(e|es|ed)|due to|because of|contribut(e|es|ed) to|protective effect)\b"
ESTIMATE = r"\b(a?ORs?|a?RRs?|a?PRs?|a?HRs?|odds ratios?|risk ratios?|prevalence ratios?|hazard ratios?|β|coefficients?)\b[^.;]{0,15}?\d+\.\d+"
INTERPRET = r"\b(suggest(s|ing)?|indicat(e|es|ing) that|implies|may be (due|because|explained)|could be (due|because|explained)|possibly because|this (is|may be) because|highlight(s)? the need)\b"
TRANSITIONS = r"(^|(?<=[.!?]\s))(Furthermore|Moreover|Additionally|In addition|Notably|Importantly|Interestingly)\b"

METHODS_ITEMS = [
    ("Survey design (cluster/strata or two-stage sampling)", r"cluster|strat|two[- ]stage|multi[- ]?stage|primary sampling unit|\bPSU\b"),
    ("Sampling weights", r"weight"),
    ("Response rate", r"response rate"),
    ("Outcome definition", r"outcome|dependent variable|defined as"),
    ("Exposure or explanatory variables", r"exposure|independent variable|explanatory|covariate|predictor"),
    ("Confounder selection rationale", r"confound|a priori|directed acyclic|\bDAG\b|based on (the )?(literature|previous|prior)"),
    ("Missing data handling", r"missing"),
    ("Effect measure named (OR, PR, RR, HR)", r"odds ratio|prevalence ratio|risk ratio|hazard ratio|\bOR\b|\bPR\b|\bRR\b"),
    ("Sensitivity analysis", r"sensitivity analys"),
    ("Software and version", r"\bStata\b|\bR\b|\bSAS\b|\bSPSS\b"),
    ("Ethics approval or exemption", r"ethic|institutional review|\bIRB\b|consent"),
    ("Reporting guideline (STROBE or other)", r"STROBE|RECORD|GATHER|TRIPOD|CONSORT|PRISMA"),
    ("Data availability statement", r"data (availability|sharing)|publicly available|available (on|upon) (registration|request)"),
]

BIAS_DIRECTION = r"underestimat|overestimat|bias(ed)? (towards|toward|away)|toward(s)? the null|away from the null|attenuat|inflat|conservative"


def read_text(path):
    if path.lower().endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paras = []
        for p in root.iter(f"{{{ns['w']}}}p"):
            paras.append("".join(t.text or "" for t in p.iter(f"{{{ns['w']}}}t")))
        return "\n\n".join(paras)
    with open(path, encoding="utf-8") as f:
        return f.read()


def heading_name(line):
    t = line.strip().strip("#*_ ").strip()
    t = re.sub(r"^[\dIVX]+[.)]?\s+", "", t).rstrip(":").strip().lower()
    if len(t.split()) > 6:
        return None
    for name, pat in HEADINGS:
        if re.fullmatch(pat, t):
            return name
    return None


def split_sections(text):
    sections, current = {}, "preamble"
    for line in text.splitlines():
        name = heading_name(line) if line.strip() else None
        if name:
            current = name
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")


def units(text):
    """Split text into prose units: paragraphs and single list items.
    Headings, table rows, code blocks and YAML front matter are skipped."""
    out, buf, fence = [], [], False
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), 0)
        lines = lines[end + 1:]
    for line in lines:
        s = line.strip()
        # Blockquote markers ("> ") wrap captions and quotes; judge the text inside.
        while s.startswith(">"):
            s = s[1:].strip()
        line = s
        if s.startswith("```"):
            fence = not fence
            continue
        if fence or s.startswith("|") or s.startswith("#") or not s:
            if buf:
                out.append(" ".join(buf))
                buf = []
            continue
        # A line that is entirely bold (a caption or table title) stands alone.
        if s.startswith("**") and s.endswith("**") and len(s) > 4:
            if buf:
                out.append(" ".join(buf))
                buf = []
            out.append(s.strip("*"))
            continue
        if LIST_ITEM.match(line) and buf:
            out.append(" ".join(buf))
            buf = []
        buf.append(LIST_ITEM.sub("", s, count=1) if LIST_ITEM.match(line) else s)
    if buf:
        out.append(" ".join(buf))
    return out


def sentences(text):
    result = []
    for unit in units(text):
        unit = re.sub(r"\s+", " ", unit)
        # Do not split on decimals, "et al.", "e.g.", "i.e.", "vs." or "Fig."
        protected = re.sub(r"\b(et al|e\.g|i\.e|vs|Fig|approx|no)\.", lambda m: m.group(0).replace(".", "§"), unit)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[])", protected)
        result.extend(p.replace("§", ".").strip() for p in parts if p.strip())
    return result


def words(text):
    # Numbers such as 61.3, 4,958 or 95% count as one word.
    return len(re.findall(r"\d+(?:[.,]\d+)*%?|[^\W\d_][\w'-]*", text))


def excerpt(s, n=14):
    w = s.split()
    return " ".join(w[:n]) + (" ..." if len(w) > n else "")


def check(sections, max_sentence, design):
    out = []
    add = out.append
    body = {k: v for k, v in sections.items() if k not in ("references",)}

    add("## Style")
    long = [(k, s) for k, v in body.items() for s in sentences(v) if words(s) >= max_sentence and not s.lstrip().startswith("|")]
    add(f"* Sentences with {max_sentence} or more words: {len(long)}")
    for k, s in long[:25]:
        add(f"  * [{k}] ({words(s)} words) {excerpt(s)}")
    if len(long) > 25:
        add(f"  * ... and {len(long) - 25} more")
    for label, pat in [("Em dashes (—)", "—"), ("En dashes (–)", "–"), ("Double hyphens (--)", r"(?<!-)--(?!-)")]:
        n = sum(len(re.findall(pat, v)) for v in body.values())
        if n:
            add(f"* {label}: {n}. Replace with commas, colons, semicolons, parentheses or 'to' in ranges.")
    tr = [m.group(2) for v in body.values() for m in re.finditer(TRANSITIONS, v)]
    if tr:
        counts = {t: tr.count(t) for t in sorted(set(tr))}
        add("* Formulaic transitions at sentence start: " + ", ".join(f"{t} ({c})" for t, c in counts.items()))
    add("")

    add("## Reporting")
    flags = 0
    for k in ("abstract", "results"):
        v = sections.get(k, "")
        for s in sentences(v):
            if re.search(ESTIMATE, s) and not re.search(r"95\s?%|\bCI\b|confidence interval|credible interval|\bUI\b", s):
                add(f"* [{k}] Effect estimate without a 95% CI: {excerpt(s)}")
                flags += 1
    for k, v in body.items():
        for m in re.finditer(r"\bp\s?[=<]\s?0?\.0+\b(?!\d)", v, re.I):
            add(f"* [{k}] '{m.group(0)}': report as p<0.001.")
            flags += 1
    res = sections.get("results", "")
    for s in sentences(res):
        if re.search(INTERPRET, s, re.I):
            add(f"* [results] Interpretation in Results (move to Discussion?): {excerpt(s)}")
            flags += 1
        elif re.search(r"\bsignificant(ly)?\b", s, re.I) and not re.search(r"95\s?%|\bCI\b|\bp\s?[=<>]", s, re.I):
            add(f"* [results] 'Significant' without an estimate, CI or p value: {excerpt(s)}")
            flags += 1
    if re.search(r"data not shown", " ".join(body.values()), re.I):
        add("* 'Data not shown' found. Most top journals ask for these results in the supplement.")
        flags += 1
    if res and re.search(r"\d+(\.\d+)?\s?%", res) and not re.search(r"weight", sections.get("methods", "") + res, re.I):
        add("* Percentages reported but weighting is never mentioned. State whether percentages are weighted.")
        flags += 1
    conc = sections.get("conclusion", "")
    if re.search(r"\d+(\.\d+)?\s?%|95\s?%\s?CI|\ba?(OR|RR|PR|HR)\b", conc):
        add("* Conclusion repeats numerical results. Top journals usually state the message without numbers.")
        flags += 1
    if design in ("cross-sectional", "ecological"):
        for k in ("abstract", "results", "discussion", "conclusion"):
            for s in sentences(sections.get(k, "")):
                m = re.search(CAUSAL, s, re.I)
                if m:
                    add(f"* [{k}] Causal wording '{m.group(0)}' in a {design} study: {excerpt(s)}")
                    flags += 1
    if not flags:
        add("* No reporting flags.")
    add("")

    meth = sections.get("methods", "")
    if meth:
        add("## Methods completeness")
        missing = [label for label, pat in METHODS_ITEMS
                   if not re.search(pat, meth, re.I if "\\bR\\b" not in pat else 0)]
        if missing:
            add("* Not found in Methods (check whether needed): " + "; ".join(missing) + ".")
        else:
            add("* All core items found.")
        add("")

    lim = sections.get("limitations", "") or sections.get("discussion", "")
    if lim:
        add("## Limitations")
        if not re.search(r"limitation", lim, re.I):
            add("* No limitations paragraph found.")
        elif not re.search(BIAS_DIRECTION, lim, re.I):
            add("* Limitations do not state the likely direction of bias (for example, 'likely to underestimate').")
        else:
            add("* Limitations mention direction of bias.")
        add("")

    add("## Length against the 100 most cited public health papers (median and IQR)")
    for k, (med, lo, hi) in BENCHMARKS.items():
        if k in sections:
            n = words(sections[k])
            note = "within IQR" if lo <= n <= hi else ("shorter than usual" if n < lo else "longer than usual")
            add(f"* {k.capitalize()}: {n} words ({note}; median {med}, IQR {lo} to {hi}). Journal limits take priority.")
    found = [k for k in ("abstract", "introduction", "methods", "results", "discussion", "conclusion") if k in sections]
    add(f"* Sections detected: {', '.join(found) if found else 'none (use headings such as # Methods)'}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--section", help="treat the whole file as this section (e.g. discussion)")
    ap.add_argument("--design", default="cross-sectional",
                    help="study design, used for the causal-language check (default cross-sectional)")
    ap.add_argument("--max-sentence", type=int, default=30)
    args = ap.parse_args()

    text = read_text(args.path)
    sections = {args.section.lower(): text} if args.section else split_sections(text)
    if not args.section and set(sections) == {"preamble"}:
        sections = {"text": text}
    print(f"# Manuscript check: {args.path}\n")
    print(check(sections, args.max_sentence, args.design))


if __name__ == "__main__":
    sys.exit(main())
