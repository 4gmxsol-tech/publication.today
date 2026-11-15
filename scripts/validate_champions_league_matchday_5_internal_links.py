#!/usr/bin/env python3
"""Validate the internal-link cluster for Champions League Matchday 5 coverage."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUGS = {
    "fixtures": "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026",
    "madrid": "real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026",
    "sabah": "sabah-vs-barcelona-champions-league-matchday-5-preview-november-25-2026",
    "arsenal": "arsenal-vs-borussia-dortmund-champions-league-matchday-5-preview-november-24-2026",
}
PAGES = {
    key: (ROOT / "articles" / f"{slug}.html").read_text(encoding="utf-8")
    for key, slug in SLUGS.items()
}
URLS = {
    key: f"https://publication.today/articles/{slug}.html"
    for key, slug in SLUGS.items()
}

# Every page must retain one canonical URL and one valid NewsArticle schema block.
for key, html in PAGES.items():
    assert html.count(f'<link rel="canonical" href="{URLS[key]}">') == 1, (
        f"{key} page must retain exactly one correct canonical URL"
    )
    schemas = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    )
    assert len(schemas) == 1, f"{key} page must contain exactly one JSON-LD block"
    schema = json.loads(schemas[0])
    assert schema.get("@type") == "NewsArticle", f"{key} must remain a NewsArticle"
    main_page = schema.get("mainEntityOfPage", {})
    assert main_page.get("@id") == URLS[key], f"{key} schema URL must match its canonical"

# The full schedule must expose both individual match previews; each preview
# must lead readers back to the full schedule. The two previews are cross-linked.
assert f'href="{SLUGS["madrid"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Real Madrid vs PSV preview"
)
assert f'href="{SLUGS["sabah"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Sabah vs Barcelona preview"
)
assert f'href="{SLUGS["arsenal"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Arsenal vs Borussia Dortmund preview"
)
assert f'href="{SLUGS["fixtures"]}.html"' in PAGES["madrid"], (
    "Real Madrid vs PSV preview must link to the full schedule"
)
assert f'href="{SLUGS["fixtures"]}.html"' in PAGES["sabah"], (
    "Sabah vs Barcelona preview must link to the full schedule"
)
assert f'href="{SLUGS["fixtures"]}.html"' in PAGES["arsenal"], (
    "Arsenal vs Borussia Dortmund preview must link to the full schedule"
)
assert f'href="{SLUGS["madrid"]}.html"' in PAGES["arsenal"], (
    "Arsenal preview must cross-link to the Real Madrid vs PSV preview"
)
assert f'href="{SLUGS["sabah"]}.html"' in PAGES["arsenal"], (
    "Arsenal preview must cross-link to the Sabah vs Barcelona preview"
)
assert "<title>Arsenal vs Borussia Dortmund: Kick-off Time, Emirates Stadium &amp; Match Preview</title>" in PAGES["arsenal"], (
    "Arsenal preview must have its expected document title"
)
for phrase in ("20:00 GMT", "21:00 CET", "20:00 UTC", "3:00 p.m. in US Eastern Standard Time", "22:00 in Sudan", "Emirates Stadium", "uefa.com", "arsenal.com", "bvb.de", "nist.gov"):
    assert phrase in PAGES["arsenal"], f"Arsenal preview is missing verified detail or source: {phrase}"
assert PAGES["arsenal"].count("<h1>") == 1, "Arsenal preview must contain exactly one H1"
assert f'href="{SLUGS["madrid"]}.html"' in PAGES["sabah"], (
    "Sabah preview must retain its cross-link to the Madrid preview"
)

# All four pages must remain discoverable in the football feed and sitemap.
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
feed_by_slug = {item.get("slug"): item for item in feed}
sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
entries = {}
for node in sitemap.findall("sm:url", ns):
    loc = node.findtext("sm:loc", default="", namespaces=ns)
    if loc in URLS.values():
        entries[loc] = node

for key, slug in SLUGS.items():
    item = feed_by_slug.get(slug)
    assert item and item.get("category") == "football", (
        f"{slug} must remain in the football article feed"
    )
    assert URLS[key] in entries, f"{slug} must remain in the sitemap exactly once"
    if item.get("lastmod"):
        sitemap_lastmod = entries[URLS[key]].findtext(
            "sm:lastmod", default="", namespaces=ns
        )
        assert sitemap_lastmod == item["lastmod"], (
            f"{slug} feed and sitemap lastmod values must match"
        )

print("Champions League Matchday 5 previews, canonical metadata, feed and sitemap links are valid.")
