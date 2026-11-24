"""Fetch openly licensed images plus provenance metadata from Wikimedia Commons.

Usage (check category names on commons.wikimedia.org first!):
    python src/fetch_commons.py --category "Category:NAME" --depth 1 --limit 150
    python src/fetch_commons.py --category "Category:A" --category "Category:B"

Writes data/metadata.csv (appended, de-duplicated) and data/images/*.jpg
(downscaled copies, width 1024). Only freely licensed files are kept
(CC / public domain); license, author, credit and source URL are stored.
"""
import argparse
import re
import time

import pandas as pd
import requests

from common import DATA, IMAGES, METADATA_CSV, year_to_epoch

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "berlin-ansichten-prototype/0.1 (research prototype; contact: add-your-email)"}
FREE = re.compile(r"(CC|Public domain|PD|GFDL)", re.I)


def api(params):
    params = {"format": "json", "formatversion": "2", **params}
    for attempt in range(3):
        r = requests.get(API, params=params, headers=HEADERS, timeout=30)
        if r.status_code in (429, 500, 502, 503, 504) and attempt < 2:
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()


def subcategories(cat):
    data = api({"action": "query", "list": "categorymembers", "cmtitle": cat,
                "cmtype": "subcat", "cmlimit": "50"})
    return [m["title"] for m in data["query"]["categorymembers"]]


def files_in_category(cat, limit):
    out, cont = [], {}
    while len(out) < limit:
        data = api({
            "action": "query", "generator": "categorymembers", "gcmtitle": cat,
            "gcmtype": "file", "gcmlimit": "50",
            "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
            "iiurlwidth": "1024", **cont,
        })
        out += data.get("query", {}).get("pages", [])
        if "continue" not in data:
            break
        cont = data["continue"]
    return out[:limit]


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def extract_year(date_str):
    m = re.search(r"\b(1[5-9]\d\d|20[0-2]\d)\b", date_str or "")
    return int(m.group(1)) if m else None


def to_row(page, cat):
    info = (page.get("imageinfo") or [{}])[0]
    if info.get("mime") not in ("image/jpeg", "image/png"):
        return None
    meta = info.get("extmetadata", {})
    lic = meta.get("LicenseShortName", {}).get("value", "")
    if not FREE.search(lic):
        return None
    date_raw = strip_html(meta.get("DateTimeOriginal", {}).get("value", ""))
    year = extract_year(date_raw)
    return {
        "file_id": page["title"].replace("File:", "").replace(" ", "_"),
        "title": page["title"],
        "source": "Wikimedia Commons",
        "category": cat,
        "page_url": info.get("descriptionurl"),
        "image_url": info.get("thumburl") or info.get("url"),
        "license": lic,
        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
        "author": strip_html(meta.get("Artist", {}).get("value", "")),
        "credit": strip_html(meta.get("Credit", {}).get("value", "")),
        "description": strip_html(meta.get("ImageDescription", {}).get("value", ""))[:500],
        "date_raw": date_raw,
        "year": year,
        "epoch": year_to_epoch(year),
        "medium": "",  # fill in during annotation: foto / gemaelde / druck / ...
        "district": "",  # fill in during annotation
    }


def download(row):
    ext = ".png" if row["image_url"].lower().endswith(".png") else ".jpg"
    path = IMAGES / (re.sub(r"[^\w.-]", "_", row["file_id"])[:120] + ext)
    if not path.exists():
        for attempt in range(3):
            r = requests.get(row["image_url"], headers=HEADERS, timeout=60)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            r.raise_for_status()
            path.write_bytes(r.content)
            time.sleep(0.5)  # be polite
            break
    return path.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", action="append", required=True)
    ap.add_argument("--depth", type=int, default=0)
    ap.add_argument("--limit", type=int, default=100, help="max files per category")
    a = ap.parse_args()

    IMAGES.mkdir(parents=True, exist_ok=True)
    cats, frontier = list(a.category), list(a.category)
    for _ in range(a.depth):
        frontier = [s for c in frontier for s in subcategories(c)]
        cats += frontier

    rows = []
    for cat in dict.fromkeys(cats):
        for page in files_in_category(cat, a.limit):
            row = to_row(page, cat)
            if row is None:
                continue
            try:
                row["local_file"] = download(row)
            except requests.RequestException as e:
                print("skip", row["file_id"], e)
                continue
            rows.append(row)
        print(f"{cat}: {len(rows)} kept so far")

    new = pd.DataFrame(rows)
    if METADATA_CSV.exists() and METADATA_CSV.stat().st_size > 0:
        try:
            old = pd.read_csv(METADATA_CSV)
        except pd.errors.EmptyDataError:
            old = None
        if old is not None:
            new = pd.concat([old, new]).drop_duplicates("file_id", keep="first")
    new.to_csv(METADATA_CSV, index=False)
    print(f"{len(new)} images in {METADATA_CSV}")
    if "epoch" in new.columns:
        print(new["epoch"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
