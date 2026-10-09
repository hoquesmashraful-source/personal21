# DHS and MICS report downloader

Scripts and manifests for downloading published reports from the
Demographic and Health Surveys (DHS) Program and UNICEF's Multiple
Indicator Cluster Surveys (MICS).

The PDFs themselves are not stored in this repository. Together they are
larger than 5 GB, which is beyond what GitHub allows. Run the downloader on
your own computer instead. It needs Python 3.8 or later and nothing else.

## What is covered

| Manifest | Source | Contents |
| --- | --- | --- |
| `manifests/dhs_survey_reports.csv` | DHS API | Final reports, summary reports, key findings, HIV fact sheets, MIS, AIS and SPA reports |
| `manifests/dhs_analytical_papers.csv` | dhsprogram.com | Working papers, further analysis, analytical studies, comparative reports, methodological reports, occasional papers, qualitative studies, spatial analysis reports, analysis briefs, policy briefs |
| `manifests/mics_reports.csv` | World Bank Microdata Library (UNICEF MICS collection) | MICS final reports, key findings and summary reports |

Each row gives the series, title, country, survey year, survey ID, source URL
and target file name.

## Download everything

```bash
python3 scripts/download.py --dry-run   # check the number of files and size first
python3 scripts/download.py             # download all manifests
```

Files are saved to `downloads/<source>/<series>/`. Re-running the command skips
files already on disk, so an interrupted run can be resumed. Failed files are
listed in `downloads/failed.csv`.

## Download a subset

```bash
# One manifest
python3 scripts/download.py manifests/dhs_analytical_papers.csv

# Only DHS final reports for Bangladesh and Nepal
python3 scripts/download.py manifests/dhs_survey_reports.csv \
    --series "Final Report" --country BD --country NP

# MICS reports for one country (MICS uses full country names)
python3 scripts/download.py manifests/mics_reports.csv --country Bangladesh
```

## Refresh the manifests

New reports are published often. To rebuild the lists:

```bash
python3 scripts/build_dhs_manifest.py
python3 scripts/build_mics_manifest.py                  # reports only
python3 scripts/build_mics_manifest.py --all-materials  # also questionnaires and manuals
```

## Research papers that used DHS or MICS data

`literature/pubmed_dhs_mics_papers.csv` lists 14,085 PubMed papers (1984 to
October 2026) that name DHS or MICS in their title or abstract.

| Tag | Papers | PubMed search (title and abstract) |
| --- | --- | --- |
| DHS | 13,132 | "Demographic and Health Survey\*", "Demographic Health Survey\*", "DHS Program\*", "National Family Health Survey\*" or "NFHS" (India's DHS) |
| MICS | 693 | "Multiple Indicator Cluster Survey\*", or "MICS" with "UNICEF" |
| DHS+MICS | 260 | Both |

Each row gives the PMID, title, first three authors, journal, year, DOI,
PMCID, a PubMed link, and countries named in the title. 9,225 papers have an
open access copy in PubMed Central. To download those PDFs (several GB):

```bash
python3 scripts/download.py literature/pubmed_dhs_mics_papers.csv --dry-run
python3 scripts/download.py literature/pubmed_dhs_mics_papers.csv
python3 scripts/download.py literature/pubmed_dhs_mics_papers.csv --country Bangladesh
```

PDFs come from the PMC Open Access dataset on AWS. Papers that are not open
access have no download link; use the DOI or PubMed link to reach them through
your library. To refresh the list, run
`python3 scripts/build_literature_manifest.py`.

Limits of this list:

* A paper is included because it names the survey in its title or abstract.
  Most such papers analyse the data, but a few only mention it. Papers that
  name the survey only in their methods section are missed.
* Country-specific survey names other than NFHS (for example "BDHS" alone) are
  only caught when the full programme name also appears.
* The `countries_in_title` column is a simple name match. It can miss
  countries or tag the wrong one (for example "Congo").
* Journals not indexed in PubMed are not covered.

## Known limits

* **MICS coverage is partial.** The MICS website (mics.unicef.org) blocks
  automated access, so the list comes from the World Bank Microdata Library.
  That catalog holds 229 MICS surveys, and 169 of them list a report PDF.
  For surveys not covered, download the reports by hand from
  <https://mics.unicef.org/surveys>.
* **Some MICS links may fail.** Most MICS reports are hosted on UNICEF's
  storage, which refused requests from the cloud server used to build this
  repository. They should work from a normal internet connection. Older links
  on childinfo.org no longer exist; the downloader then tries a copy in the
  Internet Archive.
* Journal articles that use DHS or MICS data are listed separately (see above).
* Survey datasets need a separate registration with the DHS Program and are
  not part of this repository.

## Citation counts and corpus of highly cited papers

* `scripts/add_citations.py` adds NIH iCite citation counts (`citations`,
  `rcr`) to `literature/pubmed_dhs_mics_papers.csv`. 1,046 papers have more
  than 50 citations; 595 of them are open access.
* `scripts/build_corpus.py` downloads and parses the full texts of those 595
  papers into `literature/corpus/` (not committed; rebuild locally).
* `scripts/analyze_corpus.py` writes `literature/corpus_analysis.md`, a
  section-by-section profile of how these papers are written.

## Manuscript-writing skill

`skills/public-health-manuscript/` is a Claude skill for writing, revising
and reviewing public health manuscripts, built from the corpus above. It
covers the title, abstract, introduction, methods, statistical analysis,
results, tables, figures, discussion, limitations and conclusion, and
includes `scripts/check_manuscript.py`, a draft checker:

```bash
python3 skills/public-health-manuscript/scripts/check_manuscript.py my_draft.docx
```

The packaged skill is `skills/dist/public-health-manuscript.skill`. The test
results are in `skills/public-health-manuscript-review-iteration-1.html`.

## The 100 most cited public health articles

* `scripts/build_top_cited.py` ranks public health articles (2000 to 2024) by
  NIH iCite citations. Sources are 22 core public health and epidemiology
  journals, plus public-health-indexed articles in six general medical
  journals. Clinical-care papers are screened out (`exclusions.csv`), and
  three matched controls are drawn per article from the same journal and year.
* `scripts/analyze_top_cited.py` compares the top 100 with the controls that
  have an abstract (`literature/top_cited/analysis.md`).
* `literature/top_cited/top100_classification.tsv` codes each paper by
  contribution type and by what citing authors reuse.

## High-impact writing skill

`skills/high-impact-public-health-writing/` is a second skill, built from the
top-100 analysis. It covers why papers are cited, data analysis style, figure
style with R recipes, and each section of a paper. It includes
`scripts/citability_check.py`, which scores a draft against top-100 and
typical rates. Packaged: `skills/dist/high-impact-public-health-writing.skill`.
Test results: `skills/high-impact-public-health-writing-review-iteration-1.html`.
