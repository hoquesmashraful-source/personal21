# Methods and data analysis style

How the most cited public health papers design, run and describe their
analysis. Results writing is in `results.md`.

## Contents
1. What the evidence shows
2. Methods structure
3. Data analysis style
4. The analysis procedure
5. Adapting the style to one survey or cohort
6. Sentence frames
7. Weaknesses to avoid
8. Checklist

## 1. What the evidence shows

From the top 100 versus 163 matched controls with an abstract (same journal and year):

* Methods are long: median 2,112 words versus 1,154 (open access subset).
  The extra length buys reproducibility.
* Uncertainty intervals, bootstrap or Bayesian intervals appear in 70% of
  top full texts versus 20% of controls. This is the clearest difference.
* Code or data are shared in 42% versus 28%; supplementary material is
  attached in 38% versus 21% (all papers).
* Labelled sensitivity analyses are less common in top papers (23% versus
  40%). Top
  papers rely on propagated uncertainty and out-of-sample validation, and
  aim each sensitivity analysis at a named bias.
* Many top papers are Global Burden of Disease (GBD) or pooled multi-country
  analyses. Section 5 says what transfers to a single study.

## 2. Methods structure

A common order of subheadings:

1. **Overview:** estimand, general approach, what changed since an earlier
   round, reporting guideline (GATHER or STROBE), software and code location.
2. **Units:** population, locations, age groups, sex, years, outcome or risk
   hierarchy.
3. **Data sources:** how they were found and how many were used.
4. **Data processing:** bias corrections, crosswalks between definitions,
   splitting of aggregated ages, handling of poorly coded deaths.
5. **Modelling:** the model for each data type and its covariates.
6. **Uncertainty, validation and derived metrics** (rates, YLLs, DALYs,
   attributable burden).
7. **Role of the funding source** (Lancet journals).

Smaller studies keep the same spine in fewer words. The NHANES obesity paper
(rank 25, PMID 24570244) moves from survey design and response rates to
measurement, ethics, definitions and statistical analysis. The Wuhan
transmission paper (rank 7, PMID 31995857) uses sources of data, case
definitions, laboratory testing, statistical analysis and ethics.

**Main text versus appendix.** The main text gives a high-level description;
every step points to an exact appendix section or page. Search terms, code
lists, model specifications, correction factors and country tables go to the
appendix. A flowchart of estimation steps often appears as figure 1 or an
appendix page (rank 3, PMID 35065702).

## 3. Data analysis style

**Count the data.** Top papers say exactly how much data they used: GBD 2019
reported 86 249 sources (rank 1, PMID 33069326); NCD-RisC pooled 2416
population-based studies with 128.9 million participants (rank 32, PMID
29029897). Exclusion rules are explicit.

**Harmonise before modelling.** Self-reported BMI was corrected to measured
values (rank 9, PMID 24880830); alternative case definitions were mapped to a
reference definition (rank 1). NCD-RisC instead excluded self-reports and
explained why (rank 32). Either way, the choice is stated and justified.

**Choose the model to fit the data, and say why.**

| Data structure | Model used in top papers |
| --- | --- |
| Incidence, prevalence, remission and mortality that must agree | Bayesian meta-regression (DisMod-MR) |
| Sparse data across places, years and ages | Spatiotemporal Gaussian process regression; Bayesian hierarchical models |
| Many candidate models for one outcome | Ensemble models weighted by out-of-sample performance (CODEm) |
| Burden attributable to a risk | Comparative risk assessment against a stated counterfactual |
| Change in life expectancy | Life tables |
| One national survey | Survey-weighted estimation with design-based standard errors |
| Focused epidemiological question | Simple parametric fits (for example, delay distributions) |

The most cited methods papers show the individual-level toolkit the field
relies on: Poisson regression with robust variance for relative risks
(rank 8, PMID 15033648), MR-Egger for pleiotropy (rank 12, PMID 26050253),
discrimination plus calibration for prediction models (PMID 20010215),
marginal structural models for time-varying confounding (PMID 10955408).

**Propagate uncertainty.** GBD repeats every computation over 1000 draws and
reports the 2.5th and 97.5th percentiles. Bayesian papers add the posterior
probability that a trend is real (rank 32). Smaller attributable-fraction
studies use Monte Carlo simulation. Every derived number (attributable
fraction, projection, ratio) carries an interval.

**Standardise and name the standard.** Counts, all-age rates and
age-standardised rates answer different questions. Top papers report all
three, explain the difference and name the standard population.

**Define counterfactuals.** Attributable burden is defined against an explicit
alternative (for example, a theoretical minimum risk exposure). The
antimicrobial resistance paper ran two counterfactuals and reported both
(rank 3). Decomposition splits change into population growth, ageing and
rate change.

**Validate.** Hold out data and report prediction error and the share of
held-out points inside the interval.

**Target sensitivity analyses at named biases**, for example excluding
self-reported data, using only explicit diagnostic codes, swapping in
trial-based relative risks, or scenarios (baseline, optimistic, pessimistic)
for projections.

**Make it reproducible.** State the guideline (GATHER for estimates, STROBE
for observational studies), software versions and where code and estimates
can be downloaded.

## 4. The analysis procedure (describe it as a numbered pipeline)

1. Define the estimand, units and outcome or risk hierarchy.
2. Find and catalogue all eligible data, with counts.
3. Harmonise: correct biases, crosswalk definitions, split aggregated ages.
4. Fit the model suited to each data type, with covariates stated.
5. Validate out of sample; report error and coverage.
6. Propagate uncertainty through every step.
7. Enforce internal consistency where needed.
8. Derive summary metrics and age-standardise.
9. Estimate attributable burden against a stated counterfactual.
10. Decompose change; compare places with levels expected for their
    development.
11. Run targeted sensitivity analyses and scenarios.
12. Report against a checklist and release code.

## 5. Adapting the style to one survey or cohort

**Transfers well**
* The Methods spine: estimand, data, definitions, processing, model,
  uncertainty, sensitivity, software.
* Design-based analysis: weights, design-based standard errors, response
  rates, share of missing data.
* Age standardisation to a named standard, beside crude estimates.
* Population counts from prevalence times population size.
* Attributable fractions from external relative risks and local prevalence,
  with Monte Carlo or bootstrap intervals.
* Modified Poisson for relative risks; discrimination and calibration for
  prediction models.
* Sensitivity analyses aimed at named biases.
* Counts beside rates, named extremes, percentage-point changes.
* Shared code and a completed STROBE checklist.

**Does not transfer**
* Borrowing strength across countries, ensemble model banks and
  covariate-only estimates for places without data.
* Claims to use "all available data" or to supersede earlier estimates.
* Calling an ordinary confidence interval an "uncertainty interval". Reserve
  that term for intervals that combine several sources by simulation.
* National counts from a non-representative sample (UK Biobank participants
  differ from the general population; PMID 28641372).

## 6. Sentence frames

1. "We estimated [measure] among [population] in [number] [units] from [start
   year] to [end year], by [age group], sex and [location level]."
2. "We used [number] data sources covering [number] participants, identified
   through [search]; appendix [section] lists every source."
3. "We converted values based on [alternative definition] to [reference
   definition] using [method], fitted to [number] studies that measured both."
4. "We modelled [outcome] with [model] and [covariates]. We held out [x]% of
   data and report prediction error and interval coverage."
5. "We repeated each step over [number] draws; 95% uncertainty intervals are
   the 2.5th and 97.5th percentiles."
6. "We age-standardised rates to [standard population] and defined
   attributable burden against a counterfactual of [level]."
7. "To test whether [named bias] explained our findings, we [changed the
   definition, excluded a subgroup or used an alternative input]."

## 7. Weaknesses to avoid

* No interval on derived quantities (attributable fractions, projections).
* Counts without rates, or crude rates compared across different age
  structures.
* Data described without numbers of sources, participants or response rates.
* No named reference group, standard population or counterfactual.
* Models never checked against held-out data.
* Sensitivity analyses promised in Methods but not reported with numbers.
* No software versions, no code, no checklist.

## 8. Checklist

* [ ] Subheadings run from scope to data, processing, model, uncertainty,
      sensitivity and reproducibility
* [ ] Estimand, units, age groups and years stated
* [ ] Sources, participants, response rates and missing data counted
* [ ] Definitions tied to a reference standard
* [ ] Model choice justified by the data structure
* [ ] Validation method and results reported (where a model predicts)
* [ ] Uncertainty method named: draws, bootstrap, design-based or Bayesian
* [ ] Standard population and counterfactual named
* [ ] Each sensitivity analysis targets a named bias
* [ ] Software versions, code location and checklist given
* [ ] Appendix pointers give section or page numbers
