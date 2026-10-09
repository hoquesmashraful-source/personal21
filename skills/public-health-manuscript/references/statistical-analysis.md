# Statistical analysis: methods and procedure

Covers the "Statistical analysis" subsection: which methods fit which
question, what to report for each, and the order in which to describe the
analysis. Survey weighting code and multilevel formulas are in
`dhs-mics-essentials.md`.

## What the corpus shows (all papers versus top journals)

| Item mentioned in Methods | All | Top journals |
| --- | --- | --- |
| Sampling weights | 61% | 62% |
| Complex design (clusters, strata) | 52% | 60% |
| Logistic regression | 61% | 44% |
| Multilevel or mixed-effects model | 25% | 40% |
| Poisson or log-binomial (prevalence ratios) | 4% | 9% |
| Trend analysis across survey rounds | 22% | 43% |
| Sensitivity analysis | 8% | 24% |
| Interaction or effect modification | 12% | 19% |
| Missing data handling | 17% | 22% |
| Confounder selection explained | 29% | 30% |
| Significance threshold stated ("p<0.05") | 34% | 18% |
| Reporting guideline cited | 12% | 27% |

Stata was named in 58% of papers that named software, SPSS 17%, SAS 7%, R 5%.

The pattern: top journals choose the effect measure deliberately, justify the
adjustment set, test robustness, and lean on confidence intervals rather than
significance thresholds.

## Choosing the method

| Question | Method | Report |
| --- | --- | --- |
| How common is the outcome? | Design-based weighted prevalence | Weights, clusters, strata; linearised SEs; weighted % with unweighted n |
| Which factors are associated with a binary outcome? | Survey logistic regression | Crude and adjusted ORs with 95% CIs; full adjustment set |
| Same, but the outcome is common (above about 10%) | Modified Poisson (robust variance) or log-binomial; or marginal effects after logistic | PR or RR with 95% CI, or risk differences; reason for the choice |
| Ordered outcome | Ordinal logistic | Proportional odds test; partial model if violated |
| Do clusters or areas matter? | Multilevel (random-intercept) model | Levels; empty model; nested models; cluster variance, ICC, MOR, PCV; fit (AIC); weight handling |
| Unmeasured local confounding | Cluster or country fixed effects | Fixed-effect level; clustered SEs |
| Many surveys pooled | Pooled model with country fixed effects and rescaled weights, or survey-level estimates combined by random-effects meta-analysis | Weight rescaling rule; I² for heterogeneity |
| Equity | Absolute and relative inequality: difference, ratio, slope index (SII), relative index (RII), concentration index (Wagstaff or Erreygers for binary outcomes) | Ranking variable; design-based SEs |
| What explains inequality? | Decomposition of the concentration index, or Oaxaca-Blinder | Contributions with bootstrapped CIs |
| Change over time | Trend across rounds: annual absolute change, excess change poorest versus richest | Survey years; variance-weighted regression |
| Where is the burden? | Spatial analysis or model-based geostatistics | Linkage method; GPS displacement; model; validation |
| Through which pathway? | Mediation analysis | Diagram; method; indirect effect with bootstrap CI |
| Estimates for places or groups not surveyed | Prediction or projection | Cross-validation; AUC or error; uncertainty draws; GATHER |
| Intervention-like exposure, time to event | Matching; Cox or discrete-time survival | Matching variables; time scale; covariates |

## The analysis procedure (describe in this order)

1. Declare the survey design once for all estimates: weights, clusters,
   strata. For pooled data, rescale weights first and create unique cluster
   and strata identifiers.
2. Describe the sample: weighted percentages with unweighted counts.
3. Estimate outcome prevalence with 95% CIs, overall and by subgroup.
4. Fit unadjusted models to show crude associations (not to screen
   variables).
5. Check functional form for continuous variables (categories, splines or
   quadratic terms).
6. Fit the prespecified multivariable model. For multilevel work, start with
   the empty model and add blocks (individual, then household or community).
7. Run diagnostics briefly: collinearity, model fit, proportional odds,
   heterogeneity between countries.
8. Test effect modification where the question calls for it; account for
   multiple comparisons.
9. Report missing data per variable and how they were handled.
10. Run sensitivity analyses: alternative outcome definitions, shorter
    recall windows, extra covariates, leave-one-country-out, multiple
    imputation, weighted versus unweighted multilevel models.
11. Name the software and version, and state how uncertainty is reported
    (95% CIs; exact two-sided p values).

## Sentence frames

1. "All analyses accounted for the survey design, using sampling weights,
   primary sampling units as clusters and [region by residence] as strata.
   Standard errors were estimated by Taylor series linearisation."
2. "We pooled [n] surveys. Weights were rescaled so that each country
   contributed in proportion to its [population of women aged 15 to 49], and
   all models included country fixed effects."
3. "We estimated prevalence ratios with modified Poisson regression and
   robust variance, because [outcome] was common and odds ratios would
   overstate the relative association."
4. "Confounders were selected a priori from [framework or causal diagram].
   We did not adjust for [variables] because they may lie on the pathway
   between [exposure] and [outcome]."
5. "We fitted random-intercept logistic models with [children] at level 1
   nested in clusters at level 2. An empty model partitioned the variance
   before individual and community variables were added in turn."
6. "Random effects are summarised as cluster-level variance, the intraclass
   correlation coefficient and the median odds ratio. Models were compared
   with [AIC]."
7. "We measured absolute and relative inequality with the slope and relative
   indices of inequality, regressing [outcome] on fractional wealth rank."
8. "To assess change over time, we estimated the average annual absolute
   change in [indicator] between [first] and [last] surveys."
9. "[Variable] was missing for [x]% of [respondents]. The main analysis used
   complete cases; a sensitivity analysis used multiple imputation by
   chained equations ([m] datasets)."
10. "We did [n] sensitivity analyses: [redefining outcome], [restricting to
    births in the two years before the survey to reduce recall bias] and
    [excluding one country at a time]."
11. "We tested whether the association differed by [modifier] by adding an
    interaction term and report stratum-specific estimates."
12. "Analyses were done in [Stata 17]. We report estimates with 95% CIs and
    exact two-sided p values."

## Weaknesses to avoid

* **Ignoring the design.** No weights, or weights for descriptive tables
  only. If models are unweighted, say why and show a weighted check.
* **P-value screening and stepwise selection** (for example, entering
  variables with bivariate p<0.25 and then backward elimination). It gives
  unstable models and lets mediators into the adjustment set.
* **Misstated diagnostics.** Cite thresholds correctly. One highly cited
  paper (PMID 19619299) described large variance inflation factors as
  "acceptable fit" and reported R² for a logistic model.
* **Odds ratios read as risk ratios** for common outcomes.
* **Causal words** such as "effect" or "determinants" for cross-sectional
  associations. Write "associated with".
* **No missing-data statement**, or large exclusions without a bias check.
* **Unexplained pooling**: no statement on weight rescaling or country
  adjustment.
* **"Significant" as the only result**: always give the estimate and CI.

## Checklist (STROBE item 12 and related)

* [ ] 12a: model, effect measure and why; adjustment set and its rationale
* [ ] 12b: subgroups and interactions, with multiple-testing note
* [ ] 12c: missing data, amount and handling
* [ ] 12d: weights, clusters, strata; pooled weight rescaling
* [ ] 12e: each sensitivity analysis and its purpose
* [ ] Multilevel: levels, ICC, MOR or PCV, fit, weight handling
* [ ] Software and version; CI and p value convention
