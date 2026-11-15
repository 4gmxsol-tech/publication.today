#!/usr/bin/env python3
"""Regression checks for the Real Madrid vs PSV Matchday 5 preview."""
from html.parser import HTMLParser
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026"
URL = "https://publication.today/articles/" + SLUG + ".html"
ARTICLE = ROOT / "articles" / (SLUG + ".html")
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
SITEMAP = ROOT / "sitemap.xml"

class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.in_title = False
        self.h1 = []
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
    parser = HeadParser()
    parser.feed(html)
    title = " ".join("".join(parser.title).split())
    description = parser.meta.get("description", "").strip()
    h1 = " ".join("".join(parser.h1).split())

    if parser.canonical != URL:
        errors.append("canonical must point to the new HTTPS article URL")
    if parser.meta.get("og:title") != title or parser.meta.get("twitter:title") != title:
        errors.append("Open Graph and Twitter titles must match the document title")
    if parser.meta.get("og:description") != description or parser.meta.get("twitter:description") != description:
        errors.append("social descriptions must match the meta description")
    if h1 != title:
        errors.append("visible H1 must match the document title")
    if html.count("<h1>") != 1:
        errors.append("article must contain exactly one H1")

    for phrase in (
        "Tuesday, November 24, 2026",
        "21:00 CET",
        "20:00 UTC",
        "22:00 in Sudan",
        "Estadio Santiago Bernabéu",
        "Matchday 5",
        "3–2 away win over AEK Athens",
        "PSV's latest league-phase result was a 1–2 home defeat to Club Brugge",
        "Confirmed starting line-ups are not available yet",
    ):
        if phrase not in html:
            errors.append("article is missing verified fact or uncertainty note: " + phrase)

    for host in ("uefa.com", "realmadrid.com", "psv.nl"):
        if host not in html:
            errors.append("article is missing official source link: " + host)

    blocks = html.split('<script type="application/ld+json">')[1:]
    if len(blocks) != 1:
        errors.append("article must contain exactly one JSON-LD script")
    else:
        try:
            schema = json.loads(blocks[0].split("</script>", 1)[0])
            if schema.get("@type") != "NewsArticle":
                errors.append("preview must use NewsArticle schema")
            if schema.get("headline") != title:
                errors.append("NewsArticle headline must match the document title")
            if schema.get("datePublished") != "2026-11-15" or schema.get("dateModified") != "2026-11-15":
                errors.append("NewsArticle publication and modification dates must be November 15")
            if schema.get("mainEntityOfPage", {}).get("@id") != URL:
                errors.append("NewsArticle mainEntityOfPage must match canonical URL")
        except json.JSONDecodeError:
            errors.append("NewsArticle JSON-LD must be valid JSON")

    feed = json.loads(FEED.read_text(encoding="utf-8"))
    matches = [item for item in feed if item.get("slug") == SLUG]
    if len(matches) != 1:
        errors.append("article must appear exactly once in data/articles.json")
    else:
        item = matches[0]
        if item.get("category") != "football" or "Real Madrid vs PSV" not in item.get("title", ""):
            errors.append("article feed category/title is incorrect")
        if item.get("date") != "November 15, 2026" or item.get("lastmod") != "2026-11-15":
            errors.append("article feed dates must be November 15, 2026")
        if not any("Champions League Matchday 5" in tag for tag in item.get("tags", [])):
            errors.append("article feed must target the Matchday 5 search phrase")

    section = SECTION.read_text(encoding="utf-8")
    section_parser = HeadParser()
    section_parser.feed(section)
    section_title = " ".join("".join(section_parser.title).split())
    section_description = section_parser.meta.get("description", "")
    section_h1 = " ".join("".join(section_parser.h1).split())
    if "Football News" not in section_title or "Match Reports" not in section_title:
        errors.append("Football section title must represent news and match reports")
    if "football match reports" not in section_description.lower() or "fixtures" not in section_description.lower():
        errors.append("Football section description must reflect match-report and fixture content")
    if "football news" not in section_h1.lower() or "match reports" not in section_h1.lower():
        errors.append("Football section H1 must reflect the expanded editorial scope")
    if "articles/" + SLUG + ".html" not in section:
        errors.append("Football section must link to the new Matchday 5 preview")

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ET.parse(SITEMAP).getroot()
    entries = sitemap.findall("sm:url", ns)
    entry = next((node for node in entries if node.findtext("sm:loc", default="", namespaces=ns) == URL), None)
    if not entry or entry.findtext("sm:lastmod", default="", namespaces=ns) != "2026-11-15":
        errors.append("sitemap must include the article with lastmod 2026-11-15")

    if errors:
        print(" | ".join("FAIL: " + item for item in errors))
        return 1
    print("PASS: Real Madrid vs PSV preview facts, sources, feed, section metadata and sitemap are consistent.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
