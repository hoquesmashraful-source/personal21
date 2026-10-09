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
* **Not covered:** journal articles by outside researchers that use DHS or MICS
  data. These are spread across many publishers and are often behind paywalls.
  Search PubMed or the DHS Program's own publication search for those.
* Survey datasets need a separate registration with the DHS Program and are
  not part of this repository.
