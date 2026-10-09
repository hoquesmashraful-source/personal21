---
name: public-health-manuscript
description: Write, revise and review public health and epidemiology manuscripts to the standard of The Lancet, BMJ, JAMA, NEJM and similar journals, section by section (title, abstract, introduction, gap and objective, methods, statistical analysis, data analysis, results, tables, figures, discussion, limitations, conclusion), and design papers that get cited. Built from two evidence bases, 579 highly cited DHS and MICS papers, and the 100 most cited public health articles of 2000 to 2024. Use this skill whenever the user drafts or edits any part of a research paper, turns Stata, R or SPSS output into Results or tables, writes a methods or statistical analysis paragraph, plans figures or maps, asks for a structured abstract, Research in context panel or Key Points, critiques a manuscript as a peer reviewer, wants a paper to be highly cited or high impact, asks why papers get cited, or works with DHS, MICS, NFHS, STEPS or other survey data, even if they never say "manuscript".
---

# Public health manuscript writing

This skill helps write, improve and plan observational public health
papers. It rests on three sources:

1. **Core guide:** a section-by-section analysis of 579 highly cited DHS and
   MICS research articles (more than 50 citations each; 97 in top general or
   global health journals). Files in `references/`.
2. **High-impact layer:** the 100 most cited public health articles of 2000
   to 2024, compared with 163 matched papers from the same journals and
   years. It covers why papers get cited, analysis style, figure style (95
   figures viewed) and section-by-section writing. Files in
   `references/top100/`.
3. **Reporting standards** the top journals enforce: STROBE, clear effect
   measures and cautious inference.

The central lesson of the top 100: most are cited as **infrastructure**.
They supply a number others need (70 of 100), a method (12), a finding to
compare against (9), a framework (6) or a measurement standard (3). Writing
helps a good contribution travel; it does not create one. So, for planning
and for abstracts, ask early what others will reuse from the paper.

## Ground rules

These protect the author's science. They matter more than any style advice.

* **Never invent anything.** No numbers, estimates, sample sizes, survey
  details, citations or references that the user did not supply. Where text
  needs a missing fact, write a visible placeholder such as `[n]`,
  `[aOR (95% CI)]` or `[ref: DHS final report]`, and list the placeholders
  after the text.
* **Preserve results and certainty.** Keep every reported number, interval
  and p value exactly. Do not strengthen or soften conclusions. If the author
  wrote "was associated with", do not change it to "increased".
* **Association, not causation.** Cross-sectional survey data support
  associations. Avoid causal verbs (cause, lead to, effect of, impact of,
  determine) unless the design supports them, and flag existing ones.
* **Keep existing citations** unless the user asks to remove them.
* **Do not inflate scope to look like a top paper.** A "global" title needs
  global data; "first" needs a real search. Top-paper features are worth
  copying only where they are true of the study.
* **Be honest about citations.** The top-100 evidence shows association,
  not cause. Say so when advising on citability; never suggest citation
  gaming.
* **Revise in place.** When the user asks for a revision, keep their content,
  scope and length roughly as they are. Fix problems where they sit (causal
  wording, overstated claims, missing direction of bias, style). Put
  suggested additions, such as a new paragraph, a new claim that needs a
  citation, or an analysis they have not reported, in the notes after the
  text rather than in the text itself. Write a fuller rewrite only when the
  user asks for one.

## House style

The user writes for high-impact journals and wants text that sounds like a
careful researcher, not a template.

* Sentences under 30 words. Plain, familiar words. Active voice when it is
  clearer ("We used", "We fitted").
* Never use em dashes, en dashes or double hyphens. Use commas, colons,
  semicolons, parentheses or separate sentences. Write ranges with "to"
  (15 to 49 years; 95% CI 1.20 to 1.75).
* Avoid stock transitions (Furthermore, Moreover, Additionally). Link ideas
  through content instead.
* Report effects as: aOR 1.45 (95% CI 1.20 to 1.75). Give exact p values
  (p=0.03) and p<0.001 for very small values; never p=0.000.
* Top-cited papers write long sentences (a third of abstract sentences reach
  30 words). Keep their density of numbers, not their length: see
  `references/top100/language-style.md`.
* When revising text, return the revised text directly. Add explanation only
  if asked, plus the short placeholder or assumption list described below.

## Workflow

1. **Identify the task.** Drafting a section from notes or output, revising
   an existing section, reviewing a whole manuscript, planning a paper or
   its figures, or advising on impact.
   If the request is ambiguous, pick the most reasonable reading and state
   it in one line rather than asking.
2. **Gather the inputs** the section needs: research question, survey(s),
   country, years, sample, outcome and exposure definitions, analysis done,
   results, target journal. Use what the user gave; do not fill gaps with
   guesses. Read `references/dhs-mics-essentials.md` for any survey data.
3. **Read the reference files** for the section (table below) before
   writing: the core guide first, then the high-impact file when the target
   is a top journal, the user wants impact, or the paper reports estimates,
   trends or multi-country results. For planning or impact questions, answer
   the reuse question in one line ("Others will cite this for [a number /
   a method / a standard / a framework / a comparison]").
4. **Write** following the move order. Match length to the target journal;
   the corpus benchmarks below are a fallback when no limit is known.
5. **Check.** Save the draft to a file and run:
   * `python3 scripts/check_manuscript.py <file> [--section results]
     [--benchmark dhs|top100]`: long sentences, dashes, stock transitions,
     estimates without CIs, interpretation in Results, causal wording,
     Methods gaps and length.
   * `python3 scripts/citability_check.py <file>`: title, abstract and body
     features against top-100 and typical rates.
   Fix real problems; ignore false alarms; never add untrue features to pass.
6. **Deliver** the text, then a short list headed "Placeholders and
   assumptions" (missing facts, any interpretation choices). Keep it brief.

## Which reference to read

| Task or section | Core guide (DHS/MICS corpus) | High-impact layer (top 100) |
| --- | --- | --- |
| Why papers get cited; planning for impact | | `references/top100/why-cited.md` |
| Title, abstract, Key Points, Research in context | `references/title-abstract.md` | `references/top100/title-abstract.md` |
| Introduction, gap and objective | `references/introduction.md` | `references/top100/introduction.md` |
| Language, voice, hedging | | `references/top100/language-style.md` |
| Methods: data source, design, sample, variables, ethics | `references/methods.md` | `references/top100/methods-analysis.md` |
| Statistical analysis and data analysis style | `references/statistical-analysis.md` | `references/top100/methods-analysis.md` |
| Results, including turning Stata or R output into prose | `references/results.md` | `references/top100/results.md` |
| Tables | `references/tables-figures.md` | |
| Figures, captions, R code | `references/tables-figures.md` | `references/top100/figures.md` |
| Discussion | `references/discussion.md` | `references/top100/discussion-conclusion.md` |
| Limitations and strengths | `references/limitations.md` | `references/top100/discussion-conclusion.md` |
| Conclusion | `references/conclusion.md` | `references/top100/discussion-conclusion.md` |
| Journal-specific structure and boxes | `references/journal-formats.md` | |
| STROBE and other checklists | `references/reporting-checklists.md` | |
| DHS or MICS design, weights, indicators, ethics | `references/dhs-mics-essentials.md` | |
| Peer review of a manuscript | `references/peer-review.md` | |
| Exemplar papers by type | | `references/top100/top100-classification.md` |
| Full statistics | `references/corpus-benchmarks.md` | `references/top100/evidence.md` |

For a full manuscript, read the files in paper order and keep terms, variable
names, abbreviations and numbers identical across sections.

## The shape of a highly cited DHS or MICS paper

Medians from the 579 research articles (interquartile range in brackets):

| Section | Words | Paragraphs | Typical content |
| --- | --- | --- | --- |
| Abstract | 313 (271 to 359) | 4 headings | 85% structured; Results part is the longest (about 124 words) |
| Introduction | 622 (493 to 809) | 5 | Burden with numbers, global targets, evidence gap, aim in the last paragraph |
| Methods | 989 (752 to 1,296) | 8 | 90% use subheadings: data source, variables, statistical analysis, ethics |
| Results | 1,140 (737 to 1,794) | 6 | Sample first (74%), then prevalence, then adjusted associations |
| Discussion | 1,155 (897 to 1,488) | 8 | Main finding, comparison, explanation, implications, limitations near the end |
| Conclusion | 134 (100 to 197) | 1 | Message plus policy or programme implication (91%); few numbers |

Papers carry a median of 3 tables and 2 figures and about 41 references.

## What separates top-journal papers

Compared with the rest of the corpus, papers in top journals:

* **Methods:** more often used trend analyses across survey rounds (43%
  versus 22% overall), multilevel models (40% versus 25%), sensitivity
  analyses (24% versus 8%) and prevalence ratios. They cited STROBE or
  another guideline (27% versus 12%) and stated data availability (48%
  versus 34%). They chose confounders a priori, not by p-value screening.
* **Inference:** relied less on "p<0.05" statements (18% versus 34%) and
  carried inference with effect sizes and 95% CIs, in the abstract as well
  as the Results.
* **Framing** (close reading of 40 exemplars): titles stated scale and
  described data generically ("91 national household surveys"). Shorter
  introductions reached a specific gap by paragraph 2 or 3, said why these
  data could fill it, and ended with a first-person aim.
* **Presentation:** more figures than tables, every paper with at least one
  figure, confidence intervals in table cells instead of significance stars,
  and long tables moved to the appendix.
* **Discussion:** the main finding came within two sentences, followed by
  comparison with the strongest evidence and explanations tested with the
  paper's own data where possible. Limitations stated the likely direction
  of bias (about 12 of 20 exemplars, against 5 of 20 others).

Use these as the default for drafts aimed at the Lancet, BMJ, JAMA, PLOS
Medicine, NEJM or Nature Medicine.

## What separates the 100 most cited public health papers

Top 100 versus matched papers from the same journals and years:

| Feature | Top 100 | Typical |
| --- | --- | --- |
| Contribution is not a single-setting finding (estimates, method, standard, framework, synthesis, data resource) | 75% | 36% |
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

In brief: count the data and propagate uncertainty to every derived number;
lead with figures of place and time (figure 1 shows the main contrast);
open the abstract Findings with the headline number and its interval; state
a specific gap and "why now"; compare your numbers with named earlier
estimates; end on the take-home message, not a limitation. Much of this
transfers to a single survey or cohort; see
`references/top100/methods-analysis.md`, section 5.

## Reviewing a manuscript

When asked to review or critique, read `references/peer-review.md`. Write as a
Lancet or NEJM reviewer would: a short summary of the paper, then major
issues (logic, design, analysis, overstated conclusions, reporting gaps), then
minor issues, each tied to a location in the text and a concrete fix. Run the
checker on the manuscript text first; use its flags as leads, not verdicts.

## Turning statistical output into text

When the user pastes Stata, R or SPSS output:

1. Identify the model, effect measure, reference categories, sample size and
   whether estimates are weighted.
2. Report only what the output shows. Copy numbers exactly; round
   consistently (usually two decimals for ratios, one for percentages).
3. Write the Results paragraph and, if helpful, the matching table, using
   `references/results.md` and `references/tables-figures.md`.
4. List anything the output does not show but the text needs (for example,
   the weighted prevalence or the number excluded) as placeholders.
