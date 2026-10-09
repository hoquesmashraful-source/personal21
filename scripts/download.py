"""Download the PDFs listed in one or more manifests.

Files go to downloads/<source>/<series>/<filename>. Files already on disk are
skipped, so the script can be re-run to resume. Failures are logged to
downloads/failed.csv.

Usage:
  python3 scripts/download.py                       # every manifest in manifests/
  python3 scripts/download.py manifests/dhs_survey_reports.csv
  python3 scripts/download.py --series "Final Report" --country BD
  python3 scripts/download.py literature/pubmed_dhs_mics_papers.csv   # open access papers
  python3 scripts/download.py --dry-run             # count files and size only
"""

import argparse
import csv
import glob
import os
import re
import sys
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, read_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PMC_OA = "https://pmc-oa-opendata.s3.amazonaws.com"


def safe(name):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name).strip(" .") or "_"


def target_path(out, row):
    return os.path.join(out, safe(row["source"]), safe(row["series"]), safe(row["filename"]))


def get_pdf(url, referer=None):
    data = fetch(url, referer=referer, timeout=300)
    if not data.startswith(b"%PDF"):
        raise ValueError("response is not a PDF")
    return data


def pmc_pdf_url(pmcid):
    """Find the latest PDF version of a PMC Open Access article on AWS."""
    listing = fetch(f"{PMC_OA}/?list-type=2&prefix={pmcid}.").decode("utf-8", "replace")
    keys = re.findall(rf"<Key>({pmcid}\.(\d+)/{pmcid}\.\d+\.pdf)</Key>", listing)
    if not keys:
        raise ValueError("no PDF in the PMC Open Access dataset")
    return f"{PMC_OA}/{max(keys, key=lambda k: int(k[1]))[0]}"


def download(row, path):
    if row["url"].startswith("pmc:"):
        data = get_pdf(pmc_pdf_url(row["url"][4:]))
    else:
        referer = "https://mics.unicef.org/" if row["source"] == "MICS" else None
        try:
            data = get_pdf(row["url"], referer)
        except (urllib.error.URLError, ValueError, OSError):
            # Older MICS links (childinfo.org) are dead; try the Internet Archive copy.
            data = get_pdf(f"https://web.archive.org/web/2020id_/{row['url']}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return len(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifests", nargs="*")
    ap.add_argument("--out", default=os.path.join(ROOT, "downloads"))
    ap.add_argument("--series", action="append", help="keep only this series (repeatable)")
    ap.add_argument("--country", action="append", help="keep only this country code or name (repeatable)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = args.manifests or sorted(glob.glob(os.path.join(ROOT, "manifests", "*.csv")))
    # Rows without a URL (e.g. papers that are not open access) cannot be fetched.
    rows = [r for p in paths for r in read_manifest(p) if r.get("url")]
    if args.series:
        rows = [r for r in rows if r["series"] in args.series]
    if args.country:
        wanted = {c.lower() for c in args.country}
        rows = [r for r in rows
                if r.get("country", "").lower() in wanted
                or wanted & {c.strip().lower() for c in r.get("countries_in_title", "").split(";")}]

    todo = [(r, target_path(args.out, r)) for r in rows]
    todo = [(r, p) for r, p in todo if not os.path.exists(p)]
    known = sum(int(r["size_bytes"]) for r, _ in todo if r.get("size_bytes", "").isdigit())
    print(f"{len(rows)} files selected, {len(todo)} still to download"
          f" (at least {known / 1e9:.2f} GB where size is known)", file=sys.stderr)
    if args.dry_run or not todo:
        return

    failed, done, total = [], 0, 0
    with ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(download, r, p): r for r, p in todo}
        for fut in as_completed(futures):
            r = futures[fut]
            done += 1
            try:
                total += fut.result()
                status = "ok"
            except (urllib.error.URLError, ValueError, OSError) as e:
                failed.append({**r, "error": str(e)})
                status = f"FAILED ({e})"
            print(f"[{done}/{len(todo)}] {status} {r['filename']}", file=sys.stderr)

    print(f"Downloaded {done - len(failed)} files ({total / 1e9:.2f} GB); {len(failed)} failed",
          file=sys.stderr)
    if failed:
        os.makedirs(args.out, exist_ok=True)
        log = os.path.join(args.out, "failed.csv")
        with open(log, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(failed[0].keys()))
            w.writeheader()
            w.writerows(failed)
        print(f"Failures listed in {log}", file=sys.stderr)


if __name__ == "__main__":
    main()
