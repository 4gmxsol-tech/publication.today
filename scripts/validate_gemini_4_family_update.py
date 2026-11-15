#!/usr/bin/env python3
"""Regression checks for the November 2026 Gemini 4 model-family update."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "google-gemini-4-argon-ai-model-coding-benchmark-pricing"
URL = f"https://publication.today/articles/{SLUG}.html"
page = (ROOT / "articles" / f"{SLUG}.html").read_text(encoding="utf-8")
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
item = next((entry for entry in feed if entry.get("slug") == SLUG), None)
assert item is not None, "Gemini 4 Argon article missing from feed"
assert item.get("lastmod") == "2026-11-16", "Feed lastmod must match the reviewed update"
assert {"Gemini 4 Carbon", "Gemini 4 Hydrogen", "Gemini 4 model comparison"}.issubset(set(item.get("tags", [])))
assert item.get("readTime") == "9 min read"
assert "Gemini 4 Carbon" in page and "Gemini 4 Hydrogen" in page
assert "November 10, 2026" in page and "November 12" in page
assert "not available on the Free tier" in page
assert "Hydrogen is free on the Free tier" in page
assert "paid-tier API rates are $1.50 per million input tokens and $7.50 per million output tokens" in page
assert "November 30, 2026" in page and "December 1" in page
for official_url in (
    "https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-carbon-now-available/",
    "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/",
    "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/",
    "https://cloud.google.com/blog/products/ai-machine-learning/gemini-4-argon-available-on-google-cloud?hl=en",
    "https://ai.google.dev/gemini-api/docs/pricing",
):
    assert official_url in page, f"Missing official source: {official_url}"
schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
assert len(schemas) == 1, "Expected exactly one JSON-LD block"
schema = json.loads(schemas[0])
assert schema.get("@type") == "Article"
assert schema.get("datePublished") == "2026-10-15"
assert schema.get("dateModified") == "2026-11-16"
assert schema.get("mainEntityOfPage") == URL
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
entries = [node for node in sitemap.findall("sm:url", ns)
           if node.findtext("sm:loc", default="", namespaces=ns) == URL]
assert len(entries) == 1, "Article must appear exactly once in sitemap"
assert entries[0].findtext("sm:lastmod", default="", namespaces=ns) == "2026-11-16"
section = (ROOT / "section-technology.html").read_text(encoding="utf-8")
assert "Gemini 4 Argon, Carbon &amp; Hydrogen: Model Roles, Benchmarks and Pricing" in section
assert "Compare Argon, Carbon and Hydrogen workflows" in section
assert "free-tier availability" in section
assert "Verify release status and pricing against primary sources" not in section
assert f"articles/{SLUG}.html" in section
body_headings = {part.get("heading") for part in item.get("body", [])}
assert "How Gemini 4 Argon compares with Carbon and Hydrogen" in body_headings
print("Gemini 4 family article, feed, section card, official sources, schema and sitemap are consistent.")
