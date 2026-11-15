#!/usr/bin/env python3
"""Regression checks for the UEFA Champions League Matchday 5 fixture guide."""
from html.parser import HTMLParser
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026"
URL = "https://publication.today/articles/" + SLUG + ".html"
TITLE = "Champions League Matchday 5 Fixtures: Full Schedule & Kick-off Times"
DESCRIPTION = "See all 18 UEFA Champions League Matchday 5 fixtures for November 24–25, 2026, with confirmed CET kick-off times and Sudan time conversions."
ARTICLE = ROOT / "articles" / (SLUG + ".html")
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
PSV_PREVIEW = ROOT / "articles/real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026.html"
SITEMAP = ROOT / "sitemap.xml"

FIXTURES = [
    "Bodø/Glimt vs LASK", "Galatasaray vs Aston Villa",
    "Arsenal vs Borussia Dortmund", "Como vs AEK Athens",
    "Feyenoord vs Porto", "Manchester City vs Napoli",
    "Leipzig vs Lens", "Real Madrid vs PSV Eindhoven",
    "Slovan Bratislava vs Real Betis", "Sabah vs Barcelona",
    "Slavia Praha vs Villarreal", "Atlético de Madrid vs Viking",
    "Club Brugge vs Liverpool", "Inter vs Stuttgart",
    "Shakhtar Donetsk vs Fenerbahçe", "Lille vs Bayern München",
    "Paris Saint-Germain vs Roma", "Sporting CP vs Manchester United",
]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.h1 = []
        self.in_title = False
        self.in_h1 = False
        self.meta = {}
        self.canonical = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key:
                self.meta[key.lower()] = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = attrs.get("href", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.in_h1:
            self.h1.append(data)

def main():
    errors = []
    html = ARTICLE.read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(html)
    title = " ".join("".join(parser.title).split())
    h1 = " ".join("".join(parser.h1).split())
    description = parser.meta.get("description", "").strip()

    if title != TITLE or h1 != TITLE:
        errors.append("document title and visible H1 must match the fixture-guide title")
    if parser.canonical != URL:
        errors.append("canonical must point to the HTTPS fixture-guide URL")
    if parser.meta.get("og:title") != TITLE or parser.meta.get("twitter:title") != TITLE:
        errors.append("Open Graph and Twitter titles must match the document title")
    if parser.meta.get("og:description") != DESCRIPTION or parser.meta.get("twitter:description") != DESCRIPTION or description != DESCRIPTION:
        errors.append("social and search descriptions must match")
    if html.count("<h1>") != 1:
        errors.append("article must contain exactly one H1")

    for fixture in FIXTURES:
        if html.count(fixture) < 1:
            errors.append("missing fixture: " + fixture)
    if len(FIXTURES) != 18 or len(set(FIXTURES)) != 18:
        errors.append("fixture test list must contain 18 unique matches")

    for phrase in ("Tuesday, November 24, 2026", "Wednesday, November 25, 2026",
                   "18:45 CET", "17:45 UTC", "19:45 Sudan",
                   "21:00 CET", "20:00 UTC", "22:00 Sudan",
                   "CET is UTC+1", "Sudan is UTC+2"):
        if phrase not in html:
            errors.append("missing schedule or time-zone detail: " + phrase)

    if "uefa.com" not in html:
        errors.append("official UEFA source link is required")
    if f'href="{SLUG}.html"' not in PSV_PREVIEW.read_text(encoding="utf-8"):
        errors.append("existing Real Madrid vs PSV preview must link to the full fixture guide")

    scripts = html.split('<script type="application/ld+json">')[1:]
    if len(scripts) != 1:
        errors.append("article must contain exactly one JSON-LD script")
    else:
        try:
            schema = json.loads(scripts[0].split("</script>", 1)[0])
            if schema.get("@type") != "NewsArticle":
                errors.append("fixture guide must use NewsArticle schema")
            if schema.get("headline") != TITLE or schema.get("description") != DESCRIPTION:
                errors.append("NewsArticle headline and description must match metadata")
            if schema.get("datePublished") != "2026-11-15" or schema.get("dateModified") != "2026-11-15":
                errors.append("NewsArticle dates must be November 15, 2026")
            if schema.get("articleSection") != "Football":
                errors.append("articleSection must be Football")
            if schema.get("mainEntityOfPage", {}).get("@id") != URL:
                errors.append("NewsArticle mainEntityOfPage must match canonical URL")
        except (json.JSONDecodeError, AttributeError):
            errors.append("NewsArticle JSON-LD must be valid and complete")

    feed = json.loads(FEED.read_text(encoding="utf-8"))
    matches = [item for item in feed if item.get("slug") == SLUG]
    if len(matches) != 1:
        errors.append("fixture guide must appear exactly once in the article feed")
    else:
        item = matches[0]
        if item.get("category") != "football" or item.get("title") != TITLE:
            errors.append("article feed title/category is incorrect")
        if item.get("date") != "November 15, 2026" or item.get("lastmod") != "2026-11-15":
            errors.append("article feed dates are incorrect")
        if "Champions League Matchday 5 fixtures" not in item.get("tags", []):
            errors.append("article feed is missing the primary search phrase")

    section = SECTION.read_text(encoding="utf-8")
    if section.count(f'href="articles/{SLUG}.html"') != 3:
        errors.append("Football section must expose image, title and CTA links to the guide")

    sitemap = ET.parse(SITEMAP).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text.strip() for node in sitemap.findall("sm:url/sm:loc", ns)]
    if urls.count(URL) != 1:
        errors.append("fixture guide must appear exactly once in sitemap")
    if len(urls) != len(set(urls)):
        errors.append("sitemap must not contain duplicate URLs")
    if "https://publication.today/section-football.html" not in urls:
        errors.append("Football section must remain in sitemap")

    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: 18 Matchday 5 fixtures, time conversions, article metadata, feed, Football links, and sitemap are consistent.")

if __name__ == "__main__":
    main()
