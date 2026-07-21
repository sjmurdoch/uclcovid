from pathlib import Path
from bs4 import BeautifulSoup, Tag
import requests
import re

INDEX = "https://www.ucl.ac.uk/staff/life-ucl/coronavirus-covid-19-daily-update-emails"
UPDATES_PATH = Path("../data/updates")

## Download content from a URL to a specified FILENAME 
def download_to_file(url: str, filename: Path) -> None:
    with open(filename, "wb") as fh:
        r = requests.get(url)
        text = r.content
        fh.write(text)

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

## Download all news updates and save them
def main() -> None:
    r = requests.get(INDEX)
    article = extract_article_tag(r)
    for i, t in enumerate(reversed(article.find_all("li"))):
        filename = get_filename_for_update(i, t)
        url = get_url_for_update(t)
        print(f"Downloading to {filename} from {url}")
        download_to_file(url, UPDATES_PATH / filename)

    ## Download an extra one not present on the page
    download_to_file("https://uclnews.org.uk/UAA-7U8DQ-C86EC44060C3E0D3H748FS5952AA4803060A4F/cr.aspx",
        UPDATES_PATH / "167_4_May_2022__Issue_165_.html")

if __name__ == "__main__":
    main()
