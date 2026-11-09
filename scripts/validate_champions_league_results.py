#!/usr/bin/env python3
"""Regression checks for the refreshed Champions League Matchday 4 results article."""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "champions-league-matchday-4-preview-barcelona-aston-villa-real-madrid-aek-november-2026"
ARTICLE = ROOT / "articles" / f"{SLUG}.html"
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
SITEMAP = ROOT / "sitemap.xml"
URL = f"https://publication.today/articles/{SLUG}.html"

def main():
    errors = []
    html = ARTICLE.read_text(encoding="utf-8")
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    item = next((x for x in feed if x.get("slug") == SLUG), None)
    section = SECTION.read_text(encoding="utf-8")

    for phrase in (
        "Champions League Matchday 4 Results",
        "Barcelona 3–0 Aston Villa",
        "Real Madrid 3–2 AEK Athens",
        "Lamine Yamal (7')",
        "Raphinha (52', 64')",
        "Aboubakary Koïta (12')",
        "Stavros Pilios (75')",
        "Kylian Mbappé (78')",
        "Federico Valverde (92')",
        "2026-11-09",
    ):
        if phrase not in html:
            errors.append(f"article missing required result fact: {phrase}")

    for host in ("fcbarcelona.com", "avfc.co.uk", "laliga.com", "reuters.com"):
        if host not in html:
            errors.append(f"article missing source link for {host}")

    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if len(scripts) != 1:
        errors.append("article must contain exactly one JSON-LD script")
    else:
        try:
            schema = json.loads(scripts[0])
            if schema.get("@type") != "NewsArticle" or schema.get("dateModified") != "2026-11-09":
                errors.append("NewsArticle schema type/dateModified is incorrect")
        except json.JSONDecodeError:
            errors.append("NewsArticle JSON-LD is invalid")

    if not item:
        errors.append("updated article is missing from data/articles.json")
    else:
        if "Matchday 4 Results" not in item.get("title", ""):
            errors.append("article feed title is stale")
        if "Barcelona" not in item.get("excerpt", "") or "Real Madrid" not in item.get("excerpt", ""):
            errors.append("article feed excerpt must mention both clubs")
        if item.get("date") != "November 9, 2026":
            errors.append("article feed date must be updated to November 9, 2026")

    if "Matchday 4 Results" not in section or "Read Matchday 4 results" not in section:
        errors.append("football section card still presents Matchday 4 as a preview")

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ET.parse(SITEMAP).getroot()
    entries = sitemap.findall("sm:url", ns)
    entry = next((u for u in entries if u.findtext("sm:loc", default="", namespaces=ns) == URL), None)
    if not entry or entry.findtext("sm:lastmod", default="", namespaces=ns) != "2026-11-09":
        errors.append("sitemap lastmod must be 2026-11-09 for the updated article")


    recap_slug = "champions-league-fixtures-week-barcelona-psg-real-madrid-leipzig-october-2026"
    recap_url = f"https://publication.today/articles/{recap_slug}.html"
    recap_path = ROOT / "articles" / f"{recap_slug}.html"
    if not recap_path.is_file():
        errors.append("Matchday 3 recap page is missing")
    else:
        recap_html = recap_path.read_text(encoding="utf-8")
        for phrase in (
            "Real Madrid won 2–1",
            "Kylian Mbappé scored in the 41st and 87th minutes",
            "Raphinha equalised for Barcelona in the 61st",
            "La Liga fixture, not a Champions League match",
            "laliga.com/en-ES/partidazos/el-clasico",
            "fcbarcelona.com/en/matches/138374/fc-barcelona-real-madrid-la-liga-2026-2027-0",
        ):
            if phrase not in recap_html:
                errors.append(f"Matchday 3 recap missing verified result/source: {phrase}")
        if "Barcelona are scheduled to host Real Madrid" in recap_html:
            errors.append("Matchday 3 recap still describes the completed El Clasico as upcoming")
        recap_scripts = re.findall(r'<script type="application/ld\\+json">(.*?)</script>', recap_html, re.S)
        if len(recap_scripts) != 1:
            errors.append("Matchday 3 recap must contain exactly one JSON-LD script")
        else:
            try:
                recap_schema = json.loads(recap_scripts[0])
                if recap_schema.get("@type") != "NewsArticle":
                    errors.append("Completed multi-match recap must remain a NewsArticle, not an Event")
            except json.JSONDecodeError:
                errors.append("Matchday 3 recap NewsArticle JSON-LD is invalid")
        recap_entry = next((u for u in entries if u.findtext("sm:loc", default="", namespaces=ns) == recap_url), None)
        if not recap_entry or recap_entry.findtext("sm:lastmod", default="", namespaces=ns) != "2026-11-09":
            errors.append("Matchday 3 recap sitemap lastmod must be refreshed to 2026-11-09")

    if errors:
        print("\n".join(f"FAIL: {x}" for x in errors))
        return 1
    print("PASS: Matchday 4 results article, feed card, official sources, NewsArticle schema and sitemap are consistent.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
