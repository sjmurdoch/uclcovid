from pathlib import Path
from bs4 import BeautifulSoup, Tag
import argparse
import csv
import os
import requests
import re

INDEX = "https://www.ucl.ac.uk/staff/life-ucl/coronavirus-covid-19-daily-update-emails"
UPDATES_PATH = Path("../data/updates")

## Issue 165 was never listed on the index page; it was found separately and is
## recorded here so the manifest can describe every file in data/updates/.
EXTRA_UPDATES = [
    ("167_4_May_2022__Issue_165_.html",
     "Update: 4 May 2022 (Issue 165)",
     "https://uclnews.org.uk/UAA-7U8DQ-C86EC44060C3E0D3H748FS5952AA4803060A4F/cr.aspx"),
]

## Download content from a URL to a specified FILENAME.
## Fetch first, and only replace the target once a good response is in hand.
## Opening FILENAME for writing before the request would truncate any existing
## archived copy, and every source URL here is now years old: a dead host or an
## error page would then leave the newsletter empty or overwritten. So require a
## 2xx response, write to a temporary sibling file, and rename it over the target
## only on success -- a failed fetch leaves the existing file untouched.
def download_to_file(url: str, filename: Path) -> None:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    tmp = filename.with_name(filename.name + ".part")
    with open(tmp, "wb") as fh:
        fh.write(r.content)
    tmp.replace(filename)

## Given a <a> tag T, extract its URL
def get_url_for_update(t: Tag) -> str:
    a = t.find("a")
    if not isinstance(a, Tag): 
        raise Exception("Could not find <a>")
    url = a["href"] 
    if not isinstance(url, str):
        raise Exception("Could not find URL")
    return url

## Given a tag T and file index I, extract a suitable filename
def get_filename_for_update(i: int, t: Tag) -> str:
    filename = t.text
    filename = filename.replace("Update: ", "")
    filename = f"{i:03d}_" + re.sub(r"\W", "_", filename) + ".html"
    return filename

## Given a Response object R extract the <article> tag
def extract_article_tag(r: requests.Response) -> Tag:
    soup = BeautifulSoup(r.text, 'html.parser')
    article = soup.find("article")
    if not isinstance(article, Tag):
        raise Exception("Could not find <article>")
    return article

## Read the index and return (filename, title, url) for every update listed
def list_updates(index_url: str) -> list:
    r = requests.get(index_url)
    article = extract_article_tag(r)
    entries = []
    for i, t in enumerate(reversed(article.find_all("li"))):
        entries.append((get_filename_for_update(i, t), t.text.strip(),
                        get_url_for_update(t)))
    return entries

## Record where each stored file came from. The stored filenames encode only the
## date and issue number, so without this the provenance of data/updates/ depends
## on the UCL index page remaining online.
def write_manifest(entries: list, path: Path, updates_path: Path) -> None:
    with open(path, "w", newline='', encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["filename", "title", "source_url", "present"])
        for filename, title, url in entries:
            present = "yes" if (updates_path / filename).exists() else "no"
            w.writerow([filename, title, url, present])

def parse_args(argv=None):
    ## Settings may be given on the command line or in the environment, with the
    ## command line taking precedence.
    parser = argparse.ArgumentParser(
        description="Download UCL COVID-19 update emails and record their source URLs.")
    parser.add_argument(
        "--updates", type=Path, dest="updates_path",
        default=Path(os.environ.get("UCLCOVID_UPDATES", str(UPDATES_PATH))),
        help="directory holding the stored updates (env: UCLCOVID_UPDATES)")
    parser.add_argument(
        "--index", default=os.environ.get("UCLCOVID_INDEX", INDEX),
        help="UCL index page listing the updates (env: UCLCOVID_INDEX)")
    parser.add_argument(
        "--manifest-only", action="store_true",
        help="write the manifest from the index without re-downloading any update")
    return parser.parse_args(argv)

def main(argv=None) -> None:
    args = parse_args(argv)
    entries = list_updates(args.index) + EXTRA_UPDATES

    if not args.manifest_only:
        for filename, _title, url in entries:
            print(f"Downloading to {filename} from {url}")
            download_to_file(url, args.updates_path / filename)

    manifest = args.updates_path / "manifest.csv"
    write_manifest(entries, manifest, args.updates_path)
    missing = sum(1 for f, _t, _u in entries if not (args.updates_path / f).exists())
    print(f"Wrote {manifest} ({len(entries)} entries, {missing} not present on disk)")

if __name__ == "__main__":
    main()
