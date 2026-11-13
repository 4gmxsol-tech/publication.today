#!/usr/bin/env python3
"""Regression checks for the football match-day nutrition guide."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "football-match-day-nutrition-guide"
URL = f"https://publication.today/articles/{SLUG}.html"
UPDATED = "2026-11-13"
DESCRIPTION = "Football match-day nutrition: what to eat 3–4 hours before kickoff, a light 1–2 hour snack, hydration tips and simple recovery guidance."

html = (ROOT / "articles" / f"{SLUG}.html").read_text(encoding="utf-8")
assert f'<link rel="canonical" href="{URL}">' in html
assert html.count(DESCRIPTION) >= 3, "Meta, Open Graph and Article schema descriptions must agree"
assert "Updated November 13, 2026" in html
assert "A simple pre-match timeline" in html
assert "3–4 hours before" in html and "1–2 hours before kickoff" in html
assert "There is no single fluid target that suits everyone" in html
assert "not a personal prescription" in html
assert "not individual medical advice" in html
assert 'href="https://doi.org/10.1136/bjsports-2019-101961"' in html
assert 'href="https://www.betterhealth.vic.gov.au/health/healthyliving/sporting-performance-and-food"' in html
assert 'href="football-recovery-sleep-hydration-rest-days.html"' in html
assert 'href="football-fitness-beginners-build-endurance-safely.html"' in html
hydration_section = re.search(r'<h2>Hydrate steadily</h2>(.*?)(?=<h2>)', html, re.S)
assert hydration_section and 'href="daily-water-intake-estimator.html">Daily Water Intake Estimator</a>' in hydration_section.group(1), (
    "Hydration section must link contextually to the daily water estimator"
)
estimator = (ROOT / "articles" / "daily-water-intake-estimator.html").read_text(encoding="utf-8")
assert "not a universal target or medical instruction" in estimator
assert "not suitable for people with clinician-prescribed fluid limits" in estimator

schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
assert len(schemas) == 1, "Expected one JSON-LD graph"
schema = json.loads(schemas[0])
graph = schema.get("@graph", [])
article_schema = next((item for item in graph if item.get("@type") == "Article"), None)
breadcrumb_schema = next((item for item in graph if item.get("@type") == "BreadcrumbList"), None)
assert article_schema, "Article structured data must remain present"
assert breadcrumb_schema, "BreadcrumbList structured data must be present"
assert article_schema.get("datePublished") == "2026-10-12", "Original publication date must be preserved"
assert article_schema.get("dateModified") == UPDATED
assert article_schema.get("description") == DESCRIPTION
assert breadcrumb_schema.get("@id") == URL + "#breadcrumb"
breadcrumb_items = breadcrumb_schema.get("itemListElement", [])
assert [item.get("name") for item in breadcrumb_items] == [
    "Home", "Nutrition", "What to Eat Before a Football Match"
]
assert [item.get("item") for item in breadcrumb_items] == [
    "https://publication.today/",
    "https://publication.today/section-nutrition.html",
    URL
]
visible_breadcrumb = re.search(r'<div class="breadcrumb">(.*?)</div>', html, re.S)
assert visible_breadcrumb, "Visible breadcrumb trail must be present"
assert 'href="../section-nutrition.html">Nutrition</a>' in visible_breadcrumb.group(1)
assert 'aria-current="page">What to Eat Before a Football Match</span>' in visible_breadcrumb.group(1)

feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
record = next(item for item in feed if item.get("slug") == SLUG)
assert record.get("lastmod") == UPDATED
assert record.get("excerpt") == DESCRIPTION
assert any(item.get("heading") == "A simple pre-match timeline" for item in record.get("body", []))
assert any(item.get("heading") == "Evidence and individual differences" for item in record.get("body", []))

ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
entry = next(node for node in sitemap.findall("sm:url", ns)
             if node.findtext("sm:loc", default="", namespaces=ns) == URL)
assert entry.findtext("sm:lastmod", default="", namespaces=ns) == UPDATED
print("Football nutrition guide: intent, source links, Article schema, feed, related links and sitemap lastmod all pass.")

# Static section URLs have dedicated self-canonical pages; avoid routing article navigation
# through the generic query-parameter section endpoint.
for category in ("fitness", "health", "skincare", "nutrition", "wellness", "beauty"):
    section_path = ROOT / f"section-{category}.html"
    assert section_path.is_file(), f"Static section page is missing: {section_path.name}"
    assert f'href="../section-{category}.html"' in html, (
        f"Article navigation must link directly to the canonical {category} section page"
    )
assert "../section.html?category=" not in html, (
    "Article navigation must not route through the generic query-parameter section endpoint"
)
