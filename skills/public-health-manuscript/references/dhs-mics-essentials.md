# DHS and MICS essentials for manuscript writing

Technical facts that reviewers check in secondary analyses of Demographic and
Health Surveys (DHS) and Multiple Indicator Cluster Surveys (MICS). Use them to
write accurate Methods text and to spot gaps in a draft. When a detail differs
by survey round or country, say so and check the survey's final report.

## Contents
1. Survey design
2. Files, units of analysis and sample restriction
3. Weights, clusters and strata
4. Pooled multi-country or multi-round analyses
5. Common indicators and their definitions
6. Wealth index
7. Multilevel models with survey data
8. Geographic data
9. Ethics, data access and citation

## 1. Survey design

* Both programmes use nationally representative household samples drawn by
  **two-stage stratified cluster sampling**. Clusters (enumeration areas) are
  selected with probability proportional to size within strata, usually
  region by urban or rural residence. A fixed number of households is then
  selected systematically in each cluster.
* State the survey name, country, year(s) of fieldwork, implementing agency,
  sampling frame (usually the most recent census), number of clusters and
  households, and response rates for households and for individuals. These are
  in the survey's final report; cite it.
* DHS is implemented by national agencies with technical support from ICF
  (funded by USAID). MICS is implemented by national statistics offices with
  technical support from UNICEF.
* Name the questionnaire module used (for example, the domestic violence
  module, which is given to one randomly selected woman per household and has
  its own weight).

## 2. Files, units of analysis and sample restriction

DHS recode files (standard names):

| File | Unit | Typical use |
| --- | --- | --- |
| IR | Women aged 15 to 49 | Contraception, maternal care, empowerment |
| KR | Children under 5 (born in the last 5 years) | Nutrition, vaccination, childhood illness |
| BR | All births to interviewed women | Mortality, birth history |
| HR | Households | Water, sanitation, assets |
| PR | Household members | Education, anthropometry of all members |
| MR | Men aged 15 to 49 or 59 | Men's attitudes and behaviours |
| CR | Couples | Couple concordance |

MICS uses separate datasets for households (hh), household members (hl),
women (wm), men (mn), children under 5 (ch) and children aged 5 to 17 (fs).

Describe every restriction in order, with numbers removed at each step (for
example: all women 15 to 49, then women with a live birth in the 5 years
before the survey, then the most recent birth, then complete data on key
variables). Top journals expect this as a flow chart or a sentence chain.

## 3. Weights, clusters and strata

* DHS weights are stored as integers with six implied decimals: divide by
  1,000,000 (women `v005`, households `hv005`, men `mv005`). Cluster is `v001`
  or `v021` (primary sampling unit); strata are `v022` or `v023`, depending on
  the survey. Check the recode manual for the survey used.
* MICS weights include `hhweight`, `wmweight`, `mnweight`, `chweight` and
  `fsweight`; the cluster is `HH1`; check the strata variable in the dataset.
* Stata example (DHS women's file):

  ```stata
  gen wt = v005/1000000
  svyset v021 [pweight=wt], strata(v022) singleunit(centered)
  svy: proportion outcome
  svy: logistic outcome i.exposure i.age_group i.residence i.wealth
  ```

* R example: `survey::svydesign(ids = ~v021, strata = ~v022, weights = ~wt, data = df, nest = TRUE)`.
* Say in Methods that percentages are weighted and sample sizes are
  unweighted, and repeat this in table footnotes. Reviewers ask about it often.
* Domestic violence, anthropometry and biomarker subsamples have their own
  weights (for example `d005` for the DHS domestic violence module).

## 4. Pooled multi-country or multi-round analyses

* Create unique cluster and strata identifiers by combining country, survey
  round and the original codes, so clusters are not merged across surveys.
* Decide how countries contribute: equally (rescale weights within each
  survey) or in proportion to population (de-normalise weights with
  population data). State the choice and why.
* Adjust for country (fixed effects) or model country as a level. For trends,
  include survey year and test interaction terms where the question needs it.
* Report the survey list with years and sample sizes in a supplementary
  table.

## 5. Common indicators and their definitions

Cite the *Guide to DHS Statistics* (current edition) or the MICS indicator
list for every standard indicator. Typical definitions used in the corpus:

* Stunting, wasting, underweight: height-for-age, weight-for-height and
  weight-for-age z-scores below minus 2 SD of the WHO 2006 Child Growth
  Standards. State how implausible z-scores were flagged and excluded.
* Antenatal care: four or more visits (ANC4), and eight or more under the
  2016 WHO model; first visit in the first trimester; content of care.
* Skilled birth attendance, facility delivery, caesarean section.
* Full immunisation (basic vaccines by age 12 to 23 months), from card or
  mother's report; say which sources count.
* Modern contraceptive use, unmet need and demand satisfied by modern methods.
* Under-5, infant and neonatal mortality from birth histories (synthetic
  cohort life tables for rates; survival models for individual analyses).
* Intimate partner violence in the past 12 months (domestic violence module).

## 6. Wealth index

* DHS and MICS wealth indices are built from household assets and housing
  characteristics with principal component analysis, then split into
  quintiles of the household population.
* It is a relative measure within each survey, so quintiles are not
  comparable in absolute terms across countries or rounds. Say this when
  pooling, and consider survey-specific quintiles or an absolute measure.
* Some analyses use urban and rural specific indices to avoid urban bias.
* Inequality measures: concentration index (relative or Erreygers
  corrected for binary outcomes), slope index and relative index of
  inequality, and equiplots by quintile.

## 7. Multilevel models with survey data

* Use multilevel (mixed-effects) models when the question concerns cluster,
  community or district effects, not only to "handle clustering". Survey
  commands with linearised standard errors already handle clustering for
  population-averaged estimates.
* Report the null model, then models adding individual and community
  variables. Report the intraclass correlation coefficient (ICC), the median
  odds ratio (MOR) and the proportional change in variance (PCV).
  * Logistic ICC = σ²u / (σ²u + π²/3).
  * MOR = exp(√(2σ²u) × 0.6745).
* DHS does not supply level-specific weights. State how weights were handled
  (scaled weights, or unweighted models with a weighted sensitivity analysis).
* Community-level variables built by aggregating individual responses
  (for example, cluster proportion of educated women) should be defined
  clearly, including whether the index respondent was excluded.

## 8. Geographic data

* DHS GPS cluster coordinates are displaced to protect confidentiality:
  urban clusters up to 2 km, rural clusters up to 5 km (1% of rural clusters
  up to 10 km). Mention this when linking clusters to distances or
  environmental data, and describe any buffer used.
* Name the spatial methods and software (for example, global Moran's I,
  Getis-Ord Gi*, SaTScan, kriging, or model-based geostatistics).

## 9. Ethics, data access and citation

* DHS survey protocols are reviewed by the ICF Institutional Review Board and
  by an ethics body in the host country. Informed consent was obtained from
  respondents. Secondary analysis of anonymised public datasets usually needs
  no further approval; say whether your institution confirmed exemption.
* Data access: DHS data are available on registration at the DHS Program
  website (dhsprogram.com). MICS data are available on registration at
  mics.unicef.org. Acknowledge the DHS Program (or UNICEF) and the national
  implementing agency.
* Cite the survey final report, for example:
  [Implementing agency] and ICF. [Country] Demographic and Health Survey
  [year]. [City], [Country], and Rockville, Maryland, USA: [agency] and ICF;
  [publication year].
* Do not invent report details. If a detail is unknown, leave a placeholder
  such as [response rate, final report Table 1.1].
