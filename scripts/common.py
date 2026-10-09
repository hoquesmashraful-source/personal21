"""Shared helpers for building manifests and downloading reports (stdlib only)."""

import csv
import time
import urllib.error
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; dhs-mics-report-downloader/1.0)"

MANIFEST_FIELDS = [
    "source",       # DHS or MICS
    "series",       # e.g. Final Report, Working Papers, MICS report
    "code",         # publication code or catalog id
    "title",
    "country",
    "year",
    "survey_id",
    "url",
    "filename",
    "size_bytes",
]


def fetch(url, retries=4, timeout=120, referer=None):
    """GET a URL and return the body as bytes. Retries with backoff on errors."""
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    delay = 2
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            # A 4xx other than 429 will not succeed on retry.
            if 400 <= e.code < 500 and e.code != 429:
                raise
            if attempt == retries:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == retries:
                raise
        time.sleep(delay)
        delay *= 2


def write_manifest(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MANIFEST_FIELDS})


def read_manifest(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
