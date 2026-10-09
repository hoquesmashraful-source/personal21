# Tables and figures

## What the corpus shows

* Median 3 tables (IQR 2 to 4) and 2 figures (IQR 0 to 3).
* Table 1 most often describes the sample (44%); Tables 3 and 4 most often
  hold adjusted models (48% and 50%).
* 89% of papers have table footnotes, but only 12% define abbreviations and
  21% list adjustment variables; 64% mark significance with symbols.
* Figure types: bar or dot charts by group 36%, maps 29%, trends 26%,
  inequality charts 13%, conceptual frameworks 12%, forest plots 9%, flow
  charts 9%.
* In 40 exemplars, the 20 top-journal papers had 78 figures and 56 tables;
  the other 20 had 39 figures and 74 tables. Every top-journal paper had at
  least one figure. Only 3 of 20 top-journal papers used significance stars,
  against 8 of 20 others.

The top-journal pattern: fewer, cleaner tables with confidence intervals in
the cells, at least one figure that carries the main finding, long tables
moved to the appendix, and captions and footnotes that stand alone.

## The standard table set

1. **Survey table** (multi-country): country, survey, year, sample size,
   outcome prevalence. Often in the appendix.
2. **Sample characteristics:** unweighted n and weighted % per category,
   optionally split by outcome or exposure.
3. **Outcome by characteristics:** weighted % with 95% CI and a design-based
   test of difference.
4. **Regression:** crude and adjusted columns side by side; reference
   category in its own row ("1 (ref)"); estimate with 95% CI in every cell;
   n per model. Nested models as extra columns.
5. **Random effects:** a block under the fixed effects with variance (SE),
   ICC, MOR, PCV and fit statistics (AIC).
6. **Inequality or decomposition:** SII, RII, ratios, concentration index
   and contributions.

Layout rules: one row per category, reference categories shown, consistent
decimals, CIs in cells rather than stars, no columns of p values unless the
journal expects them, and no table that only lists significant variables.

## Table captions

Name the measure, grouping, population, place, survey and years. Example:

> Table 2: Crude and adjusted odds ratios for four or more antenatal care
> visits by maternal characteristics, women with a live birth in the three
> years before the survey, Bangladesh DHS 2017 to 2018

## Table footnotes

Include what applies:

* Cell content: "Data are weighted % (95% CI); n are unweighted."
* Design handling: sampling weights, clusters and strata.
* Adjustment set for each model.
* Outcome and index definitions.
* Small-cell rule (estimates based on fewer than [25] unweighted cases
  suppressed or flagged).
* How to read an inequality index.
* Abbreviations, in alphabetical order.

## Figures: which type for which message

| Message | Figure |
| --- | --- |
| How the sample was selected | Flow chart with counts at each step |
| Why these variables | Conceptual framework |
| Prevalence by group or country | Bar or dot chart, sorted by value |
| Wealth gaps across many countries | Dot chart with one dot per quintile (equiplot) |
| Inequality in a single index | Concentration curve |
| Level against inequality or GDP | Scatter plot |
| Country estimates and a pooled value | Forest plot |
| Adjusted ratios across exposure categories | Coefficient plot on a log scale with a null line |
| Change over time | Trend lines with uncertainty bands |
| Where the burden is | Map (national, subnational or modelled) |

## Figure captions and good practice

* Captions stand alone: data source and years, what each dot, line, band
  and colour means, adjustment set, pooling method and abbreviations.
* State weighting in the caption.
* Plot ratios on a log scale and draw the null line; say which side means
  lower odds.
* Show uncertainty (CIs or uncertainty intervals).
* Credit the base map source; note GPS displacement for cluster maps.
* Avoid empty or one-line captions.

## Frames

* Table caption: "Table [n]: [Weighted prevalence, or crude and adjusted
  odds ratios] of [outcome] by [characteristics] among [population],
  [country], [survey, years]."
* Table footnote: "Data are weighted % (95% CI); n are unweighted. aORs are
  adjusted for [list]. [Abbreviations]."
* Figure caption: "Figure [n]: [Estimate] of [outcome] by [grouping],
  [setting], [survey, years]. Dots show [weighted or adjusted] estimates and
  whiskers show 95% CIs. The vertical line marks no difference.
  [Abbreviations]."

## Producing tables

When drafting a table in Markdown or Word, build it only from numbers the
user supplied. Leave cells the output does not provide as `[ ]` and say so.
For publication figures, use the `dataviz` skill if available, or give
plotting code (Stata or R) that the user can run on their data.

## Checklist

* [ ] Caption names measure, grouping, population, place, survey and years
* [ ] Cell content stated; weighted % and unweighted n labelled
* [ ] Reference category in each variable block
* [ ] Crude and adjusted side by side; n per model
* [ ] Random-effects block below fixed effects (if multilevel)
* [ ] Footnote: adjustment set, design handling, definitions, small cells,
      abbreviations
* [ ] CIs in cells rather than stars
* [ ] At least one figure carries the main finding; uncertainty shown
