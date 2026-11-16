#!/usr/bin/env python3
"""Regression checks for the 2026/27 Champions League Matchday 6 fixture guide."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "champions-league-matchday-6-fixtures-kickoff-times-december-8-9-2026"
URL = "https://publication.today/articles/" + SLUG + ".html"
TITLE = "Champions League Matchday 6 Fixtures: Full Schedule & Kick-off Times"
TITLE_HTML = "Champions League Matchday 6 Fixtures: Full Schedule &amp; Kick-off Times"
DESCRIPTION = "See all 18 UEFA Champions League Matchday 6 fixtures for Dec. 8–9, 2026, with CET, US Eastern, GMT, UTC and Sudan kick-off times."
ARTICLE = ROOT / "articles" / (SLUG + ".html")
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
SITEMAP = ROOT / "sitemap.xml"

EXPECTED_FIXTURES = [
    "Viking vs Feyenoord",
    "Villarreal vs Sabah",
    "AEK Athens vs Galatasaray",
    "Roma vs Sporting CP",
    "Aston Villa vs Paris Saint-Germain",
    "Barcelona vs Manchester City",
    "Bayern München vs Slavia Praha",
    "Manchester United vs Leipzig",
    "Napoli vs Club Brugge",
    "Real Betis vs Como",
    "Slovan Bratislava vs Shakhtar Donetsk",
    "Arsenal vs Real Madrid",
    "Borussia Dortmund vs Inter",
    "LASK vs Fenerbahçe",
    "Liverpool vs Porto",
    "Lens vs Bodø/Glimt",
    "PSV Eindhoven vs Atlético de Madrid",
    "Stuttgart vs Lille",
]


def main():
    errors = []
    html = ARTICLE.read_text(encoding="utf-8")

    if html.count(f'<link rel="canonical" href="{URL}">') != 1:
        errors.append("article must declare exactly one matching canonical URL")
    if html.count(f"<title>{TITLE_HTML}</title>") != 1:
        errors.append("document title is missing or duplicated")
    if html.count(f"<h1>{TITLE_HTML}</h1>") != 1 or html.count("<h1>") != 1:
        errors.append("article must contain exactly one matching H1")
    if html.count(f'<meta name="description" content="{DESCRIPTION}">') != 1:
        errors.append("meta description is missing or inconsistent")
    for tag in ("og:title", "twitter:title"):
        if f'<meta property="{tag}" content="{TITLE_HTML}">' not in html and f'<meta name="{tag}" content="{TITLE}">' not in html:
            errors.append(f"{tag} must match the document title")
    for tag in ("og:description", "twitter:description"):
        if f'<meta property="{tag}" content="{DESCRIPTION}">' not in html and f'<meta name="{tag}" content="{DESCRIPTION}">' not in html:
            errors.append(f"{tag} must match the meta description")

    for fixture in EXPECTED_FIXTURES:
        if html.count(fixture) < 1:
            errors.append("missing official fixture: " + fixture)
    if len(EXPECTED_FIXTURES) != 18 or len(set(EXPECTED_FIXTURES)) != 18:
        errors.append("expected fixture list must contain 18 unique matches")

    tables = re.findall(r'<table class="fixture-table">(.*?)</table>', html, re.S)
    if len(tables) != 2:
        errors.append("article must contain exactly two responsive daily fixture tables")
    else:
        for index, table in enumerate(tables, start=1):
            if table.count("<tr><td>") != 9:
                errors.append(f"day {index} must contain exactly nine fixtures")

    if html.count('<div class="fixture-table-wrap">') != 2 or "min-width:760px" not in html:
        errors.append("both fixture tables must retain the responsive horizontal-scroll wrapper")
    for cell, expected in (
        ("<td>18:45 CET</td>", 4),
        ("<td>12:45 p.m. EST</td>", 4),
        ("<td>17:45 GMT / UTC</td>", 4),
        ("<td>19:45 Sudan</td>", 4),
        ("<td>21:00 CET</td>", 14),
        ("<td>3:00 p.m. EST</td>", 14),
        ("<td>20:00 GMT / UTC</td>", 14),
        ("<td>22:00 Sudan</td>", 14),
    ):
        if html.count(cell) != expected:
            errors.append(f"expected {expected} occurrences of {cell}")

    for phrase in (
        "Tuesday, December 8, 2026: Champions League fixtures",
        "Wednesday, December 9, 2026: Champions League fixtures",
        "CET is UTC+1",
        "the United Kingdom is on GMT (UTC+0)",
        "US Eastern is on Eastern Standard Time (EST, UTC−5)",
        "Sudan is UTC+2",
        "US daylight saving time ended on November 1, 2026",
        "The league phase continues with Matchday 7 on January 19–20, 2027",
    ):
        if phrase not in html:
            errors.append("missing date, schedule or timezone detail: " + phrase)

    required_links = (
        "https://www.uefa.com/uefachampionsleague/news/02a8-2174c9e9019d-f909a77bd77a-1000--2026-27-uefa-champions-league-all-the-league-phase-fix/",
        "https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst",
        "https://www.paramountplus.com/shows/uefa-champions-league/",
        'href="champions-league-tiebreaker-rules-2026-27.html"',
        'href="champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026.html"',
        'href="football-match-time-zone-converter.html"',
        'href="football-match-countdown.html"',
    )
    for link in required_links:
        if link not in html:
            errors.append("missing source or internal guide link: " + link)

    schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    if len(schemas) != 1:
        errors.append("article must contain exactly one JSON-LD block")
    else:
        try:
            schema = json.loads(schemas[0])
            if schema.get("@type") != "NewsArticle":
                errors.append("fixture guide must use NewsArticle schema")
            if schema.get("headline") != TITLE or schema.get("description") != DESCRIPTION:
                errors.append("NewsArticle headline and description must match page metadata")
            if schema.get("datePublished") != "2026-11-16" or schema.get("dateModified") != "2026-11-16":
                errors.append("NewsArticle publication and modification dates must be November 16, 2026")
            if schema.get("articleSection") != "Football":
                errors.append("articleSection must be Football")
            if schema.get("mainEntityOfPage", {}).get("@id") != URL:
                errors.append("NewsArticle mainEntityOfPage must match canonical URL")
            for phrase in ("Champions League Matchday 6 fixtures", "Champions League fixtures December 8 2026", "Champions League fixtures December 9 2026"):
                if phrase not in schema.get("keywords", ""):
                    errors.append("NewsArticle keywords are missing: " + phrase)
        except (json.JSONDecodeError, AttributeError):
            errors.append("NewsArticle JSON-LD must be valid JSON")

    feed = json.loads(FEED.read_text(encoding="utf-8"))
    slugs = [item.get("slug") for item in feed]
    if len(slugs) != len(set(slugs)):
        errors.append("article feed must not contain duplicate slugs")
    matches = [item for item in feed if item.get("slug") == SLUG]
    if len(matches) != 1:
        errors.append("Matchday 6 guide must appear exactly once in the article feed")
    else:
        item = matches[0]
        if item.get("category") != "football" or item.get("title") != TITLE:
            errors.append("article feed title/category is incorrect")
        if item.get("date") != "November 16, 2026" or item.get("lastmod") != "2026-11-16":
            errors.append("article feed publication and lastmod dates are incorrect")
        if not {"Champions League Matchday 6 fixtures", "Champions League fixtures December 8 2026", "Champions League fixtures December 9 2026", "Champions League fixtures ET"}.issubset(set(item.get("tags", []))):
            errors.append("article feed is missing primary Matchday 6 search phrases")
        body_headings = {part.get("heading") for part in item.get("body", [])}
        if not {"Tuesday, December 8 fixtures", "Wednesday, December 9 fixtures", "Kick-off times by timezone", "The four early kick-offs"}.issubset(body_headings):
            errors.append("article feed must include both fixture days and timezone sections")

    section = SECTION.read_text(encoding="utf-8")
    section_link = f'articles/{SLUG}.html'
    if section.count(f'href="{section_link}"') != 3:
        errors.append("Football section must expose image, title and CTA links to the Matchday 6 guide")
    if "Champions League Matchday 5 and 6 fixtures" not in section:
        errors.append("Football section metadata must mention both Matchday 5 and Matchday 6")
    tie_position = section.find('href="articles/champions-league-tiebreaker-rules-2026-27.html"')
    matchday6_position = section.find(f'href="{section_link}"')
    first_preview_position = section.find('href="articles/club-brugge-vs-liverpool-champions-league-matchday-5-preview-november-25-2026.html"')
    if not (0 <= tie_position < matchday6_position < first_preview_position):
        errors.append("Football hub order must keep the Matchday 6 guide after the tiebreaker guide and before individual previews")

    sitemap = ET.parse(SITEMAP).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text.strip() for node in sitemap.findall("sm:url/sm:loc", ns)]
    if urls.count(URL) != 1:
        errors.append("Matchday 6 guide must appear exactly once in sitemap")
    if len(urls) != len(set(urls)):
        errors.append("sitemap must not contain duplicate URLs")
    entry = next((node for node in sitemap.findall("sm:url", ns)
                  if node.findtext("sm:loc", default="", namespaces=ns) == URL), None)
    if entry is None or entry.findtext("sm:lastmod", default="", namespaces=ns) != "2026-11-16":
        errors.append("Matchday 6 sitemap lastmod must be 2026-11-16")
    for slug in (SLUG, "champions-league-tiebreaker-rules-2026-27",
                 "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026",
                 "football-match-time-zone-converter", "football-match-countdown"):
        if not (ROOT / "articles" / f"{slug}.html").is_file():
            errors.append("linked article/tool file is missing: " + slug)

    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: 18 official Matchday 6 fixtures, both daily tables, timezone conversions, metadata, JSON-LD, feed, Football hub order and sitemap are consistent.")


if __name__ == "__main__":
    main()
