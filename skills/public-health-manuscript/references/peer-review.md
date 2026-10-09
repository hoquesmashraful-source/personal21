# Peer review of a public health manuscript

Review as a reviewer for The Lancet, BMJ or NEJM would: fair, specific and
focused on whether the conclusions follow from the data. The aim is a report
the editor can act on and the authors can use.

## Order of work

1. Read the abstract and the final paragraph of the Introduction. Write down
   the question in one sentence. Every later judgement tests the paper
   against this question.
2. Read Methods and Results against the question. Is the design able to
   answer it? Is the analysis the right one? Do the tables support the text?
3. Read the Discussion and Conclusion last. Mark every claim stronger than
   the evidence.
4. Save the text to a file and run `scripts/check_manuscript.py`. Use the
   flags as leads; confirm each one in context before raising it.

## What to look for

**Question and framing**
* Is the gap real and specific, or generic ("few studies have examined")?
* Does the aim match what was analysed?

**Design and data (DHS and MICS)**
* Survey, years, sample restrictions and exclusions with numbers at each step.
* Sampling weights, clusters and strata used in all estimates.
* Outcome and exposure definitions match standard indicators (cite the
  Guide to DHS Statistics or MICS definitions) or are justified.
* Temporal order: was the exposure measured before the outcome? Many
  survey variables (current wealth, current empowerment) are measured after
  the event studied (for example, a birth up to five years earlier).

**Analysis**
* Confounders chosen on a stated rationale (literature, causal diagram),
  not by p-value screening or stepwise selection.
* Effect measure suits the outcome: odds ratios overstate risk ratios for
  common outcomes; consider prevalence ratios or marginal effects.
* Multilevel models: purpose stated; ICC, MOR or PCV reported; handling of
  weights explained.
* Pooled analyses: country handled (fixed effects or a level), weights
  rescaled, and heterogeneity between countries examined.
* Missing data, sensitivity analyses, multiple comparisons, interactions.

**Results**
* Unadjusted and adjusted estimates with 95% CIs; weighted percentages and
  unweighted n labelled.
* Text matches tables. No interpretation in Results.
* Absolute measures given where they matter for policy.

**Discussion and conclusions**
* Main finding stated plainly and tied to the question.
* Comparison with the strongest evidence, not only similar surveys.
* Causal or policy claims that go beyond cross-sectional associations.
* Limitations specific to this study, with the likely direction of bias.
* Recommendations that follow from the findings, not from general beliefs.

**Reporting**
* STROBE items (see `reporting-checklists.md`), data availability, ethics,
  funding and competing interests.

## Report format

```
Summary
[Two to four sentences: question, data, main findings, overall judgement.]

Major issues
1. [Issue, with location (section, page or line).] [Why it matters.]
   [What the authors should do.]
2. ...

Minor issues
1. [Location.] [Issue and fix.]
...

Recommendation to the editor (if asked)
[Accept, minor revision, major revision or reject, with one reason.]
```

## Tone

* Specific and constructive: name the problem, its consequence and a fix.
* Separate what is wrong from what is a matter of taste.
* Do not ask for analyses the data cannot support.
* Credit real strengths briefly.
* Apply the house style (short sentences, no dashes, no stock transitions).
