---
name: public-health-manuscript
description: Write, revise and review public health and epidemiology manuscripts to the standard of The Lancet, BMJ, JAMA, PLOS Medicine, NEJM and Nature Medicine, section by section (title, abstract, introduction, methods, statistical analysis methods and procedure, data analysis, results, tables, figures, discussion, limitations, conclusion). Built from 579 highly cited DHS and MICS papers (more than 50 citations each). Use this skill whenever the user drafts or edits any part of a research paper, turns Stata, R or SPSS output into a Results section or table, writes a statistical analysis or methods paragraph, asks for a structured abstract, Research in context panel or Key Points, critiques a manuscript as a peer reviewer, or works with DHS, MICS, NFHS or other household survey data, even if they never say "manuscript".
---

# Public health manuscript writing

This skill helps write and improve observational public health papers,
especially secondary analyses of household surveys such as DHS and MICS. Its
guidance comes from two sources. The first is a section-by-section analysis
of 579 highly cited DHS and MICS research articles (more than 50 citations
each; 97 in top general or global health journals). The second is the
reporting standards those journals enforce: STROBE, clear effect measures
and cautious inference.

The corpus shows what highly cited papers usually do. Top journals ask for
more. Where the two differ, aim for the top-journal standard and say why.

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
* When revising text, return the revised text directly. Add explanation only
  if asked, plus the short placeholder or assumption list described below.

## Workflow

1. **Identify the task.** Drafting a section from notes or output, revising
   an existing section, reviewing a whole manuscript, or planning a paper.
   If the request is ambiguous, pick the most reasonable reading and state
   it in one line rather than asking.
2. **Gather the inputs** the section needs: research question, survey(s),
   country, years, sample, outcome and exposure definitions, analysis done,
   results, target journal. Use what the user gave; do not fill gaps with
   guesses. Read `references/dhs-mics-essentials.md` for any survey data.
3. **Read the reference file** for the section (table below) before writing.
   Each file gives the move structure, sentence frames, the top-journal
   difference and a checklist.
4. **Write** following the move order. Match length to the target journal;
   the corpus benchmarks below are a fallback when no limit is known.
5. **Check.** Save the draft to a file and run
   `python3 scripts/check_manuscript.py <file> [--section results]`.
   It flags long sentences, dashes, stock transitions, estimates without
   CIs, interpretation in Results, causal wording, Methods gaps and length.
   Fix real problems; ignore false alarms.
6. **Deliver** the text, then a short list headed "Placeholders and
   assumptions" (missing facts, any interpretation choices). Keep it brief.

## Which reference to read

| Task or section | Read |
| --- | --- |
| Title, abstract, Key Points, Research in context | `references/title-abstract.md` |
| Introduction | `references/introduction.md` |
| Methods: data source, design, sample, variables, ethics | `references/methods.md` |
| Statistical analysis methods and the analysis procedure | `references/statistical-analysis.md` |
| Results text, including turning Stata or R output into prose | `references/results.md` |
| Tables and figures, captions and footnotes | `references/tables-figures.md` |
| Discussion | `references/discussion.md` |
| Limitations and strengths | `references/limitations.md` |
| Conclusion | `references/conclusion.md` |
| Journal-specific structure and boxes | `references/journal-formats.md` |
| STROBE and other checklists | `references/reporting-checklists.md` |
| DHS or MICS design, weights, indicators, ethics, citation | `references/dhs-mics-essentials.md` |
| Peer review of a manuscript | `references/peer-review.md` |
| Full corpus statistics | `references/corpus-benchmarks.md` |

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
