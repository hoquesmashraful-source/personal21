# Methods: data source, design, sample, variables and ethics

Statistical methods and the analysis procedure are in `statistical-analysis.md`.
Survey facts (weights, files, indicators) are in `dhs-mics-essentials.md`.

## What the corpus shows

* Median length 989 words (IQR 752 to 1,296), about 8 paragraphs.
* 90% use subheadings. The most common: Statistical analysis, Data source,
  Outcome variable, Independent variables, Ethical considerations.
* Only 25% report response rates and 9% show a sample flow chart; 17% say how
  missing data were handled. These are the gaps reviewers notice most.
* Top-journal papers describe the survey design briefly (often one or two
  sentences plus a citation to the survey report) and spend their words on
  the sample, variables and analysis.

## Subheadings and order

1. **Data source and study design.** Survey programme, implementing agency,
   funder, country, years, sampling design, response rates, data access.
2. **Study population.** Eligibility, recall window, unit of analysis,
   exclusions with counts at each step.
3. **Variables.** Outcome, exposure, covariates (grouped by level), with a
   conceptual framework if one guided the choice.
4. **Statistical analysis.** See `statistical-analysis.md`.
5. **Ethics** (some papers place it first; either works if complete).
6. **Journal statements.** Lancet journals: role of the funding source.
   BMJ journals: patient and public involvement.

## Data source and design

* Name the survey, round, implementer and technical partner, then summarise
  the design in two to four sentences: strata (usually region by residence),
  clusters drawn with probability proportional to size, households selected
  systematically within clusters. Cite the final report.
* Explain why weights are used: unequal selection probabilities,
  oversampling and non-response. Name special-module weights (for example
  the domestic violence module).
* Report household and individual response rates from the final report. For
  multi-country work give the range or the lowest rate.
* Multi-country analyses: number the inclusion criteria (for example, the
  latest survey per country, fielded between [years], available by [date],
  with the outcome and exposure measured). Name excluded countries and why.
  Put the survey list with years and sample sizes in a supplementary table.
* Note frame limits, such as areas excluded for security reasons, and the
  GPS displacement when linking clusters to spatial data.

## Study population and sample flow

* Define the unit of analysis exactly: for example, women aged 15 to 49 with
  a live birth in the five years before the survey (DHS) or two years
  (MICS), most recent birth only.
* Give the count at each exclusion step with reasons. A model from the
  corpus (PMID 21283606): all rural births in the recall window, minus those
  whose mothers had moved, leaving a stated number of births in a stated
  number of clusters.
* Add a flow diagram (figure or supplement) for anything beyond one step.
* Justify age limits and recall windows on biological or measurement grounds.

## Variables

**Outcome.** Use the standard indicator definition and cite it (Guide to DHS
Statistics, MICS indicator list, WHO). Give numerator, denominator, age group
and recall period. For self-reported measures, give the survey question.
State cleaning rules (WHO flags for implausible z-scores, haemoglobin
altitude adjustment, birthweight limits). For composite outcomes, list the
components and scoring, and test an alternative definition.

**Exposure.** Name the main exposure, define it and justify its categories.
If it is a constructed index (empowerment, ECD index), cite its validation.

**Covariates.** Group them by level (child, mother, household, community).
Derive them from a stated framework (for example, the UNICEF conceptual
framework of malnutrition or Andersen's model of health service use), not
from p values. Provide a coding table with reference categories, in the text
or supplement. Define community variables as cluster aggregates and say so.

**Wealth index.** Say it is a principal component score of household assets
and housing characteristics, grouped into quintiles within each survey.
Watch for circularity: if the exposure is housing, water or sanitation, the
index already contains it. Rebuild the index without those items or show a
sensitivity analysis.

## Ethics and data availability

* Original approvals (ICF Institutional Review Board and national ethics
  committee for DHS; national bodies for MICS), informed consent, and your
  institution's decision for secondary analysis.
* Data availability: publicly available on registration from the DHS
  Program or UNICEF MICS website; analysis code available on request or in a
  repository (state which).

## Sentence frames

Write in the past tense for what was done and the present tense for what a
table or figure shows. Fill brackets only with facts the user supplied.

1. "The [survey, year] was a nationally representative household survey
   implemented by [agency] with technical assistance from [ICF or UNICEF]."
2. "It used a two-stage stratified cluster design. [n] enumeration areas were
   selected with probability proportional to size, stratified by [region]
   and residence, and [n] households were selected in each cluster."
3. "Household and individual response rates were [x]% and [y]%."
4. "Of [N] eligible [children], we excluded [n] with [reason] and [n] with
   missing [variable], leaving [n] in [n] clusters (figure [x])."
5. "We included the most recent [DHS or MICS] in each country that was
   fielded between [year] and [year] and measured [outcome] and [exposure]."
6. "Following the Guide to DHS Statistics, [outcome] was defined as
   [numerator] among [denominator]."
7. "We excluded [n] children with biologically implausible z-scores
   according to WHO flags."
8. "Covariates were chosen a priori from [framework] and grouped at the
   [child], [mother], [household] and [community] levels (table S[x])."
9. "Wealth was measured with the survey's wealth index, grouped into
   quintiles within each survey."
10. "We analysed anonymised, publicly available data with permission from
    [the DHS Program]. The surveys were approved by [ICF and national ethics
    committees], and respondents gave informed consent. [Institution]
    exempted this secondary analysis from further review."

## Weaknesses to avoid

* Copying the survey's own fieldwork procedures (interviewer training,
  questionnaire pretesting) into a secondary analysis. Cite the report.
* No response rates, no exclusion counts, no flow chart.
* Covariates picked by bivariate p values rather than a framework.
* Adjusting for water, sanitation or housing alongside a wealth index built
  from them, without comment.
* Undefined reference categories.
* Vague ethics statements ("ethical approval was obtained") without saying
  by whom.

## Checklist

* [ ] Survey, round, years, implementer, design and response rates given
* [ ] Unit of analysis and recall window exact; exclusions counted; flow chart
* [ ] Outcome defined with a citation, question wording and cleaning rules
* [ ] Exposure and categories justified
* [ ] Covariates from a framework, with levels and reference categories
* [ ] Wealth index described; circularity considered
* [ ] Ethics: original approvals, consent, own institution's decision
* [ ] Data availability and journal-specific statements
