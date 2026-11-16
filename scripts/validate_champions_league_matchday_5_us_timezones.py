#!/usr/bin/env python3
"""Validate US Eastern/Pacific kickoff conversions across Matchday 5 previews."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
NIST_URL = "https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst"
CASES = {
    "galatasaray-vs-aston-villa-champions-league-matchday-5-preview-november-24-2026": ("12:45 p.m.", "9:45 a.m.", "November 16, 2026"),
    "arsenal-vs-borussia-dortmund-champions-league-matchday-5-preview-november-24-2026": ("3:00 p.m.", "12:00 p.m.", "November 15, 2026"),
    "manchester-city-vs-napoli-champions-league-matchday-5-preview-november-24-2026": ("3:00 p.m.", "12:00 p.m.", "November 15, 2026"),
    "real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026": ("3:00 p.m.", "12:00 p.m.", "November 15, 2026"),
    "sabah-vs-barcelona-champions-league-matchday-5-preview-november-25-2026": ("12:45 p.m.", "9:45 a.m.", "November 15, 2026"),
    "club-brugge-vs-liverpool-champions-league-matchday-5-preview-november-25-2026": ("3:00 p.m.", "12:00 p.m.", "November 16, 2026"),
    "inter-vs-stuttgart-champions-league-matchday-5-preview-november-25-2026": ("3:00 p.m.", "12:00 p.m.", "November 16, 2026"),
}
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
feed_by_slug = {item["slug"]: item for item in feed}
sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap_entries = {
    node.findtext("sm:loc", default="", namespaces=ns): node
    for node in sitemap.findall("sm:url", ns)
}
section = (ROOT / "section-football.html").read_text(encoding="utf-8")

for slug, (est, pst, published) in CASES.items():
    path = ROOT / "articles" / f"{slug}.html"
    assert path.is_file(), f"Missing preview page: {slug}"
    html = path.read_text(encoding="utf-8")
    url = f"https://publication.today/articles/{slug}.html"
    item = feed_by_slug.get(slug)
    assert item and item.get("category") == "football", f"{slug} must remain in the Football feed"
    assert item.get("date") == published, f"{slug} publication date must remain unchanged"
    assert item.get("lastmod") == "2026-11-16", f"{slug} feed lastmod must be refreshed"
    assert "Champions League fixtures PST" in item.get("tags", []), f"{slug} missing PST search tag"
    assert "Champions League Pacific Time" in item.get("tags", []), f"{slug} missing Pacific Time search tag"
    assert any(x.get("heading") == "US Eastern and Pacific kick-off times" for x in item.get("body", [])), f"{slug} feed body missing timezone section"
    assert est in html and pst in html, f"{slug} missing expected US kick-off conversions"
    assert "US Eastern Standard Time (EST, UTC−5)" in html, f"{slug} missing explicit EST offset"
    assert "US Pacific Standard Time (PST, UTC−8)" in html, f"{slug} missing explicit PST offset"
    assert NIST_URL in html, f"{slug} missing NIST daylight-saving source"
    assert html.count(f'<link rel="canonical" href="{url}">') == 1, f"{slug} canonical must remain unique and correct"
    desc = re.search(r'<meta name="description" content="([^"]+)">', html).group(1)
    og = re.search(r'<meta property="og:description" content="([^"]+)">', html).group(1)
    twitter = re.search(r'<meta name="twitter:description" content="([^"]+)">', html).group(1)
    schema_match = re.search(r'<script type="application/ld\+json">([\s\S]*?)</script>', html)
    assert schema_match, f"{slug} missing NewsArticle JSON-LD"
    schema = json.loads(schema_match.group(1))
    assert desc == og == twitter == schema.get("description") == item.get("excerpt"), f"{slug} descriptions must match across HTML, JSON-LD and feed"
    if published == "November 15, 2026":
        assert schema.get("datePublished") == "2026-11-15", f"{slug} publication date must remain unchanged"
    else:
        assert schema.get("datePublished") == "2026-11-16", f"{slug} publication date must remain unchanged"
    assert schema.get("dateModified") == "2026-11-16", f"{slug} JSON-LD dateModified must match the update"
    assert url in sitemap_entries, f"{slug} missing from sitemap"
    lastmod = sitemap_entries[url].findtext("sm:lastmod", default="", namespaces=ns)
    assert lastmod == "2026-11-16", f"{slug} sitemap lastmod must match feed and page"
    assert f"articles/{slug}.html" in section, f"{slug} must remain linked from the Football hub"

print(f"Validated US Eastern/Pacific conversions, metadata, source links, feed dates and sitemap entries for {len(CASES)} Matchday 5 previews.")
