from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "articles" / "daily-water-intake-estimator.html"
URL = "https://publication.today/articles/daily-water-intake-estimator.html"
html = PAGE.read_text(encoding="utf-8")

expected_description = (
    "Estimate a general fluid starting point, understand the limits of a weight-based formula, "
    "and compare it with trusted hydration references."
)
assert f'<meta name="description" content="{expected_description}">' in html
assert f'<meta property="og:description" content="{expected_description}">' in html
assert f'<meta name="twitter:description" content="{expected_description}">' in html

scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
assert len(scripts) == 1, "Expected one Article JSON-LD block"
schema = json.loads(scripts[0])
assert schema.get("@type") == "Article"
assert schema.get("mainEntityOfPage") == URL
assert schema.get("datePublished") == "2026-10-27", "Original publication date must remain unchanged"
assert schema.get("dateModified") == "2026-11-14", "Article modification date must match the update"
assert "trusted hydration references" in schema.get("description", "")

assert "30 mL per kilogram" in html, "The actual weight-based formula must be explained"
assert "not a validated clinical formula" in html, "The heuristic must not be presented as validated guidance"
assert "not an official intake recommendation" in html
assert "3.7 L per day" in html and "2.7 L" in html
assert "include water from food and all beverages" in html
assert "not exact requirements or mandatory drinking-water targets" in html
assert "The CDC explains that water needs vary" in html
assert "This tool is for general education, not diagnosis or treatment" in html
assert "clinician has prescribed a fluid limit" in html
assert 'href="https://www.nationalacademies.org/read/10925/chapter/6"' in html
assert 'href="https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/index.html"' in html
assert 'rel="noopener noreferrer"' in html
assert "Illustrative estimate — not a daily target" in html

sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
entry = next(
    (node for node in sitemap.findall("sm:url", ns)
     if node.findtext("sm:loc", default="", namespaces=ns) == URL),
    None,
)
assert entry is not None, "Water estimator must remain in the sitemap"
assert entry.findtext("sm:lastmod", default="", namespaces=ns) == "2026-11-14"

feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
item = next((item for item in feed if item.get("slug") == "daily-water-intake-estimator"), None)
assert item is not None
assert item.get("lastmod") == "2026-11-14"
assert item.get("readTime") == "6 min read"
assert "official population-level hydration references" in item.get("excerpt", "")
print("PASS: hydration formula scope, authoritative sources, Article metadata, feed and sitemap are aligned.")
