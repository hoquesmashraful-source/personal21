# Results

Tables and figures are in `tables-figures.md`.

## What the corpus shows

* Median 1,140 words (IQR 737 to 1,794), about 6 paragraphs.
* 74% open by describing the sample; 10% open with overall prevalence.
* 98% report percentages, 64% give 95% CIs, 37% give p values, 30% report
  adjusted odds ratios and only 5% prevalence or risk ratios.
* In a close reading of 40 exemplars, top-journal Results reported fewer p
  values (about 6 of 20 versus 11 of 20). They rarely used surprise words
  such as "as expected" or "interestingly" (1 of 20 versus 6 of 20). They
  pointed to supplementary tables more (12 of 20 versus about 4 of 20).
* Lancet Global Health papers wrote continuous prose ordered by table and
  figure; JAMA Network Open and some PLOS Medicine papers used topic
  subheadings. Follow the target journal.

## Paragraph order

Use only the steps your analysis has.

1. **Sample.** Surveys, countries, years; eligible, excluded and analysed n.
2. **Descriptive and prevalence.** Overall estimate with 95% CI, then the
   range across groups or countries.
3. **Unadjusted associations.** Crude estimates or prevalence by group.
4. **Adjusted associations.** Main exposure first, then other covariates
   that matter for the aim.
5. **Random effects.** Null-model variance, ICC and MOR, then the change
   after adding covariates.
6. **Inequalities.** Absolute (difference, SII) and relative (ratio, RII,
   concentration index) measures; groups or countries that stand out.
7. **Trends.** Change between rounds or per year; places without change.
8. **Sensitivity analyses.** One sentence each, with an appendix pointer.

If using subheadings, name them by content ("Wealth", "Trends since 2005")
rather than by method alone ("Multivariate analysis").

## How to write each estimate

* Estimate, then 95% CI, then (if used) the exact p value:
  "aOR 1.45 (95% CI 1.20 to 1.75)". Write limits with "to", never a dash.
* After the first estimate, a journal may allow bare intervals
  ("1.45, 1.20 to 1.75"); keep one format throughout.
* Two decimals for ratios, one for percentages. p<0.001 for small values,
  never p=0.000.
* Odds ratios describe odds: "higher odds of", not "times more likely",
  especially when the outcome is common.
* Add an absolute translation where it helps (percentage-point difference
  with its CI).
* Give denominators: "n (%) of N". Label weighting: weighted percentages,
  unweighted n. When the sample shrinks for a model, give the model's n.
* For pooled estimates, say how countries were combined.

## Direction and size, without interpretation

State the direction, size, comparison group and precision. Leave reasons,
mechanisms, surprise and policy to the Discussion. Use neutral verbs:
"was associated with", "was higher among", "did not differ". No causal verbs
(led to, reduced, improved) for cross-sectional associations. Do not discuss
confounding or limitations in Results.

**Non-significant findings:** give the estimate and CI ("we found no
evidence of an association (aOR 1.06, 95% CI 0.91 to 1.24)"). Never treat
an estimate whose CI includes 1 as an effect. Do not judge differences by
whether two CIs overlap; test the difference.

## How much to repeat from tables

Write out the headline estimates that answer the aim, the range, notable
extremes and any reversal of direction. Point to the table or appendix for
the rest. Do not restate every covariate's odds ratio one per sentence.

## From statistical output to text

When the user supplies Stata, R or SPSS output:

1. Identify the model, effect measure, reference categories (Stata omits
   base levels, which are the lowest-coded categories unless set otherwise),
   number of observations and whether estimates are weighted (`svy:`).
2. Copy numbers exactly; round consistently; never compute new estimates
   the output does not contain unless the user asks, and then show how.
3. Convert "0.000" p values to p<0.001.
4. Note what the text needs but the output lacks (eligible n, exclusions,
   weighted prevalence by group, n per model) as placeholders.
5. Check that each point estimate lies inside its own CI and that text
   numbers match the table.

## Sentence frames

1. "Of [N] eligible [women] in [k] surveys ([years]), we excluded [n]
   because of [reason]. The analytical sample was [n] (figure [x])."
2. "Overall, [x]% (95% CI [l] to [u]) of [population] had [outcome],
   ranging from [x]% in [lowest] to [y]% in [highest] (table [x])."
3. "[Outcome] was more common among [group] than [reference] ([x]% vs [y]%;
   difference [d] percentage points, 95% CI [l] to [u])."
4. "[Exposure] was associated with [higher or lower] odds of [outcome]
   (OR [x], 95% CI [l] to [u]). After adjustment for [covariates], the aOR
   was [x] ([l] to [u])."
5. "Each [unit] increase in [exposure] was associated with [x]% [higher or
   lower] odds of [outcome] (aOR [x], 95% CI [l] to [u])."
6. "We found no evidence of an association between [exposure] and [outcome]
   (aOR [x], 95% CI [l] to [u]) or of modification by [modifier] (p=[p])."
7. "In the null model, the ICC was [x] and the MOR was [x]. After adding
   [individual and community factors], the MOR fell to [x] (table [x])."
8. "[Indicator] was [x] percentage points higher in the richest than the
   poorest quintile (SII [x], 95% CI [l] to [u])."
9. "Between [year 1] and [year 2], [indicator] [rose or fell] from [x]% to
   [y]%, an average change of [z] percentage points per year."
10. "Estimates changed little when we [restricted the sample, added
    covariates, changed the definition] (appendix table [x])."

## Weaknesses to avoid

* p values or significance stars without estimates and CIs.
* Calling p<0.10 "significant" or "marginally significant".
* Interpretation in Results: "surprisingly", "as expected", "this shows",
  mechanisms, limitations.
* Restating whole tables in prose.
* Unlabelled weighting; text counts that do not match tables.
* Point estimates outside their own CI (a typing error reviewers catch).
* Odds ratios read as risk ratios.

## Checklist

* [ ] Opens with surveys, years, eligible, excluded and analysed n
* [ ] Follows the analysis order
* [ ] Every estimate has a 95% CI; exact p values; one format
* [ ] Weighted and unweighted numbers labelled; pooling stated
* [ ] Headline numbers only; tables and appendix carry the rest
* [ ] Null findings given with estimates
* [ ] Odds described as odds; no causal verbs; no interpretation
* [ ] Numbers match tables, figures and abstract
