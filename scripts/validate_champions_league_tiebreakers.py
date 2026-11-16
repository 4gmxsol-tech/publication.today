#!/usr/bin/env python3
"""Regression checks for the 2026/27 Champions League league-phase tiebreaker guide."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "champions-league-tiebreaker-rules-2026-27"
URL = "https://publication.today/articles/" + SLUG + ".html"
TITLE = "Champions League Tiebreaker Rules 2026/27: How Teams Are Ranked"
DESCRIPTION = "How UEFA ranks teams level on points in the 2026/27 Champions League: live Matchday 1–7 criteria, all 10 final tie-breakers, qualification places and the head-to-head rule."
ARTICLE = ROOT / "articles" / (SLUG + ".html")
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
FIXTURES = ROOT / "articles/champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026.html"
SITEMAP = ROOT / "sitemap.xml"

html = ARTICLE.read_text(encoding="utf-8")
assert html.count(f'<link rel="canonical" href="{URL}">') == 1
assert f"<title>{TITLE}</title>" in html
assert f"<h1>{TITLE}</h1>" in html
assert html.count("<h1>") == 1
assert f'<meta name="description" content="{DESCRIPTION}">' in html
assert f'<meta property="og:title" content="{TITLE}">' in html
assert f'<meta property="og:description" content="{DESCRIPTION}">' in html
assert f'<meta name="twitter:title" content="{TITLE}">' in html
assert f'<meta name="twitter:description" content="{DESCRIPTION}">' in html

schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
assert len(schemas) == 1
schema = json.loads(schemas[0])
assert schema.get("@type") == "Article"
assert schema.get("headline") == TITLE and schema.get("description") == DESCRIPTION
assert schema.get("datePublished") == "2026-11-16" and schema.get("dateModified") == "2026-11-16"
assert schema.get("articleSection") == "Football"
assert schema.get("mainEntityOfPage", {}).get("@id") == URL
for phrase in ("Champions League tiebreaker rules", "Champions League tiebreakers 2026/27", "UEFA Article 18", "Champions League head-to-head rule"):
    assert phrase in schema.get("keywords", "")

for phrase in (
    "During Matchdays 1–7",
    "goal difference, goals scored, away goals scored, wins and away wins",
    "same ranking and their abbreviated names are displayed alphabetically",
    "not a league-phase tiebreaker",
):
    assert phrase in html, f"Missing live-table rule: {phrase}"

final_criteria = [
    "Superior goal difference in the league phase.",
    "Higher number of goals scored in the league phase.",
    "Higher number of away goals scored in the league phase.",
    "Higher number of wins in the league phase.",
    "Higher number of away wins in the league phase.",
    "Higher number of points earned collectively by the club’s eight league-phase opponents.",
    "Superior combined goal difference of those opponents.",
    "Higher combined number of goals scored by those opponents.",
    "Lower disciplinary-points total",
    "Higher UEFA club coefficient.",
]
positions = [html.index(text) for text in final_criteria]
assert positions == sorted(positions), "Final Article 18 criteria must remain in UEFA order"
assert "yellow cards count one point" in html and "a red card counts three" in html
assert "Head-to-head" in html and "No." in html
assert "https://www.uefa.com/uefachampionsleague/news/0291-1bd88ae04870-e1e038c319e3-1000--champions-league-league-phase-standings-how-t/" in html
assert "Article-17-Match-system-league-phase" in html
assert "Article-18-Equality-of-points-league-phase" in html
assert "https://www.uefa.com/uefachampionsleague/standings/" in html

fixture_html = FIXTURES.read_text(encoding="utf-8")
assert f'href="{SLUG}.html"' in fixture_html, "Matchday 5 guide must link to the tiebreaker explainer"
assert "Champions League tiebreaker rules" in json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', fixture_html, re.S).group(1)).get("keywords", "")

feed = json.loads(FEED.read_text(encoding="utf-8"))
matches = [item for item in feed if item.get("slug") == SLUG]
assert len(matches) == 1
item = matches[0]
assert item.get("category") == "football" and item.get("title") == TITLE
assert item.get("date") == "November 16, 2026" and item.get("lastmod") == "2026-11-16"
assert set(("Champions League tiebreaker rules", "Champions League tiebreakers 2026/27", "UEFA Article 18", "Champions League head-to-head rule")).issubset(set(item.get("tags", [])))
body_headings = {part.get("heading") for part in item.get("body", [])}
assert {"Quick answer", "The five criteria used during Matchdays 1–7", "All ten final tiebreakers after the league phase", "Does head-to-head count?"}.issubset(body_headings)

fixture_item = next(x for x in feed if x.get("slug") == "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026")
assert "Champions League tiebreaker rules" in fixture_item.get("tags", [])
assert any("tiebreaker guide" in part.get("text", "") for part in fixture_item.get("body", []) if part.get("heading") == "Champions League standings before Matchday 5")

section = SECTION.read_text(encoding="utf-8")
assert section.count(f'href="articles/{SLUG}.html"') == 3
assert "tiebreaker rules" in section.lower()
fixture_position = section.index('href="articles/champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026.html"')
guide_position = section.index(f'href="articles/{SLUG}.html"')
preview_position = section.index('href="articles/club-brugge-vs-liverpool-champions-league-matchday-5-preview-november-25-2026.html"')
assert fixture_position < guide_position < preview_position, "The standings guide should follow the full schedule and precede individual previews"

sitemap = ET.parse(SITEMAP).getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [node.findtext("sm:loc", default="", namespaces=ns) for node in sitemap.findall("sm:url", ns)]
assert urls.count(URL) == 1
assert len(urls) == len(set(urls))
entry = next(node for node in sitemap.findall("sm:url", ns) if node.findtext("sm:loc", default="", namespaces=ns) == URL)
assert entry.findtext("sm:lastmod", default="", namespaces=ns) == "2026-11-16"
assert "https://publication.today/section-football.html" in urls

print("PASS: UEFA live and final tiebreaker rules, Article 17 qualification, metadata, feed, Football section and sitemap are consistent.")
