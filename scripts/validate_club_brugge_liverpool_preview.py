#!/usr/bin/env python3
"""Regression checks for the Club Brugge vs Liverpool Matchday 5 preview."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "club-brugge-vs-liverpool-champions-league-matchday-5-preview-november-25-2026"
URL = f"https://publication.today/articles/{SLUG}.html"
PAGE = ROOT / "articles" / f"{SLUG}.html"
html = PAGE.read_text(encoding="utf-8")
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
record = next((item for item in feed if item.get("slug") == SLUG), None)
assert record is not None, "Club Brugge vs Liverpool article is missing from the feed"
assert record.get("category") == "football", "Article must remain in the Football category"
assert record.get("date") == "November 16, 2026" and record.get("lastmod") == "2026-11-16", "Article dates are stale"
assert "Club Brugge vs Liverpool" in record.get("title", "")
assert any("3:00 p.m." in item.get("text", "") for item in record.get("body", [])), "US Eastern kick-off conversion is missing"

assert f'<link rel="canonical" href="{URL}">' in html, "Canonical URL is missing or incorrect"
assert "<title>Club Brugge vs Liverpool:" in html, "SEO title is missing"
assert "<h1>Club Brugge vs Liverpool:" in html, "Visible H1 is missing"
assert "Wednesday, November 25, 2026" in html, "Fixture date is missing"
assert "20:00 GMT" in html and "21:00 CET" in html and "3:00 p.m." in html and "22:00" in html, "Kick-off conversions are incomplete"
assert "Jan Breydel Stadium" in html and "Bruges" in html, "Venue is missing"
assert "nine points" in html and "three wins and one defeat" in html, "League-phase points context is missing"
assert "uefa.com" in html and "liverpoolfc.com" in html and "nist.gov" in html, "Official source references are incomplete"

scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
assert len(scripts) == 1, "Expected exactly one JSON-LD block"
schema = json.loads(scripts[0])
assert schema.get("@type") == "NewsArticle", "Article must use NewsArticle schema"
assert schema.get("datePublished") == "2026-11-16" and schema.get("dateModified") == "2026-11-16", "Structured dates are stale"
assert schema.get("mainEntityOfPage", {}).get("@id") == URL, "Structured canonical URL is inconsistent"
assert schema.get("articleSection") == "Football", "Structured article section is inconsistent"

section = (ROOT / "section-football.html").read_text(encoding="utf-8")
assert section.count(f"articles/{SLUG}.html") == 3, "Football section card should link to the article image, title and CTA"
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
assert URL in sitemap and "<lastmod>2026-11-16</lastmod>" in sitemap, "Sitemap entry or lastmod is missing"
assert (ROOT / "articles" / f"{SLUG}.html").is_file(), "Article target is missing"
assert "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026.html" in html, "Missing full Matchday 5 schedule link"
print("Club Brugge vs Liverpool article, Football card, structured data, official sources and sitemap are valid.")
