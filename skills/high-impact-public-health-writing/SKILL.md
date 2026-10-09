---
name: high-impact-public-health-writing
description: Design and write public health papers in the style of the 100 most cited public health articles of 2000 to 2024, and explain why such papers get cited. Grounded in a comparison of those papers with matched papers from the same journals and years, covering citation drivers, data analysis style, figure style, titles, abstracts, language, introduction, gap, objective, methods, results, discussion and conclusion. Use this skill whenever the user wants a paper to be highly cited, high impact, noticed or "Lancet-level", asks why papers get cited or how to make theirs more citable, wants a title, abstract, gap statement, results, figures or discussion written like top papers (Global Burden of Disease, NCD-RisC, NHANES series), plans figures or maps for an epidemiology paper, or asks for an impact review of a draft, even if they do not use the word "citation".
---

# High-impact public health writing

This skill helps researchers design and write public health papers the way
the most cited ones are designed and written. It rests on an analysis of the
100 most cited public health articles published 2000 to 2024, set against 163
randomly drawn papers from the same journals and years. Five strands were
studied: why the papers are cited, how they analyse data, how they draw
figures (95 figures viewed), how they write, and how each section is built.

The central lesson: most top papers are cited as **infrastructure**. They
supply a number others need for an introduction (70 of 100), a method (12),
a finding to compare against (9), a framework (6) or a measurement standard
(3). Writing style helps a good contribution travel; it does not create one.
So start every task by asking what others will reuse from the paper.

## Ground rules

These protect the author's science and come before any style advice.

* **Never invent anything**: no numbers, sample sizes, countries, survey
  details, citations or claims of scale the user did not give. Use visible
  placeholders (`[n]`, `[95% CI]`, `[ref]`) and list them after the text.
* **Preserve results and certainty.** Keep every number exactly. Do not make
  a claim stronger or weaker than the author's evidence.
* **Association, not causation**, unless the design defines a counterfactual
  (attributable burden, decomposition) or causal evidence is cited.
* **Do not inflate scope to look like a top paper.** A "global" title needs
  global data; "first" needs a real search. Top-paper features are worth
  copying only where they are true of the study.
* **Keep existing citations** unless asked to remove them.
* **Revise in place.** When revising, keep the author's content and scope;
  put suggested additions (new claims, new analyses) in notes after the
  text.
* **Be honest about citations.** The evidence shows association, not cause.
  Say so when advising on citability, and never suggest citation gaming.

## House style

* Sentences under 30 words; plain, familiar words; active voice ("We
  estimated") where clearer.
* No em dashes, en dashes or double hyphens. Ranges with "to".
* No "Furthermore", "Moreover" or "Additionally".
* Estimates as "1.45 (95% CI 1.20 to 1.75)"; exact p values; p<0.001.
* Top papers write long sentences (a third of abstract sentences reach 30
  words). Keep their density, not their length: see
  `references/language-style.md`.
* When revising text, return the text directly, then a short "Placeholders
  and assumptions" list.

## Workflow

1. **Identify the task:** planning a study for impact; writing or revising a
   section; planning figures; reviewing a draft for impact. If ambiguous,
   take the most reasonable reading and state it in one line.
2. **Answer the reuse question** in one line: "Others will cite this for
   [a number / a method / a standard / a framework / a comparison]." If the
   user's study has no clear reusable output, say what design or reporting
   change could create one (see `references/why-cited.md`, section 6).
3. **Read the reference file(s)** for the task (table below).
4. **Write or advise**, following the move structure and frames.
5. **Check drafts with the scripts:**
   * `python3 scripts/check_manuscript.py <file>`: style and reporting
     (long sentences, dashes, estimates without intervals, causal wording,
     Methods gaps, length against top papers).
   * `python3 scripts/citability_check.py <file>`: title, abstract and body
     features against top-100 and typical rates.
   Fix real problems; ignore false alarms; never add untrue features to pass.
6. **Deliver** the text or advice, then placeholders and assumptions. For
   advice, tie each recommendation to evidence (a rate or an example PMID).

## Which reference to read

| Task | Read |
| --- | --- |
| Why papers are cited; making a study more citable | `references/why-cited.md` |
| Title and abstract (including journal formats) | `references/title-abstract.md` |
| Introduction, gap and objective | `references/introduction.md` |
| Language, voice, hedging, sentence length | `references/language-style.md` |
| Methods and data analysis style | `references/methods-analysis.md` |
| Results writing | `references/results.md` |
| Figures, captions and R code | `references/figures.md` |
| Discussion and conclusion | `references/discussion-conclusion.md` |
| Finding an exemplar paper by type | `references/top100-classification.md` |
| Full comparison tables | `references/evidence.md` |

For a whole paper, read in paper order and keep numbers, terms and
abbreviations identical across sections.

## Top papers versus typical papers (same journals and years)

| Feature | Top 100 | Typical |
| --- | --- | --- |
| Contribution is not a single-setting finding (estimates, method, standard, framework, synthesis or data resource; rule-based) | 75% | 36% |
| Title names global, world or many countries | 43% | 12% |
| Title states a time span or trend | 30% | 7% |
| Abstract offers something reusable | 41% | 21% |
| Numbers per 100 abstract words | 9.5 | 6.3 |
| Hedges per 1,000 abstract words | 1.8 | 3.1 |
| Uncertainty intervals or bootstrap in the full text | 70% | 20% |
| Figures (median) | 5 | 3 |
| Maps / trend figures | 55% / 69% | 32% / 30% |
| Limitations discussed | 79% | 62% |
| Code or data shared | 42% | 28% |
| Methods / Discussion words (median) | 2,112 / 2,357 | 1,154 / 1,277 |

Sentence length did not differ (about 27 words in abstracts for both).

## The style in brief

* **Analysis:** count the data; harmonise before modelling; choose the model
  for the data structure; propagate uncertainty to every derived number; name
  the standard population and the counterfactual; validate; aim each
  sensitivity analysis at a named bias; share code.
* **Figures:** figure 1 shows the main finding as one contrast; show place
  (maps) and time (trends with bands); small multiples on shared axes;
  ranked order; sequential palettes for magnitude; captions of 25 to 50
  words that open with measure, unit, population, place and years.
* **Abstract:** short background, data and scale first in Methods, Findings
  opening with the headline number and interval, Interpretation with a
  present-tense claim and a named action.
* **Introduction:** three paragraphs (burden; what is known and its limits;
  gap and aim), a specific gap with a "why now", and a first-person aim
  naming measure, population, places and period.
* **Results:** whole to parts; counts, rates and changes each with an
  interval; extremes named; figures carry the numbers.
* **Discussion:** main finding first; compare with named earlier estimates
  and explain differences; implications tied to findings and actors;
  specific limitations with direction and what was done; end on the
  take-home message, not a limitation.

## Adapting to a single survey or cohort

Most top papers are large collaborations. Much of their style still
transfers: the Methods spine, design-based uncertainty, age
standardisation, attributable fractions with simulated intervals, counts
beside rates, figure style, and shared code. What does not transfer:
borrowing strength across countries, "all available data" claims, and
calling an ordinary confidence interval an "uncertainty interval". See
`references/methods-analysis.md`, section 5.

For DHS or MICS technical detail (weights, recode files, indicators), the
`public-health-manuscript` skill complements this one.
