import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "el-clasico-preview-barcelona-vs-real-madrid-october-25-2026"
URL = f"https://publication.today/articles/{SLUG}.html"
EXPECTED_TITLE = "Barcelona 1–2 Real Madrid: Mbappé’s Late Brace Decides El Clásico"
EXPECTED_DESCRIPTION = (
    "Real Madrid beat Barcelona 2–1 at Spotify Camp Nou on October 25, 2026. "
    "Kylian Mbappé scored twice, with Raphinha replying in the second half."
)

articles = json.loads((ROOT / "data/articles.json").read_text(encoding="utf-8"))
article = next((item for item in articles if item.get("slug") == SLUG), None)
assert article is not None, "El Clásico article must remain in the article feed"
assert article.get("category") == "football", "El Clásico article must stay in the Football category"
assert article.get("title") == EXPECTED_TITLE, "Article feed title is stale"
assert article.get("excerpt") == EXPECTED_DESCRIPTION, "Article feed excerpt is stale"
assert article.get("lastmod") == "2026-11-15", "Article feed lastmod must match the verified update"
feed_text = json.dumps(article, ensure_ascii=False)
assert "19:00 UTC" not in feed_text and "21:00 Sudan time" not in feed_text, (
    "The superseded incorrect time conversion must not remain in the article feed"
)
assert "Mbappé" in feed_text and "Raphinha" in feed_text, "Feed must include the verified scorers"

page = (ROOT / "articles" / f"{SLUG}.html").read_text(encoding="utf-8")
assert f"<title>Barcelona 1-2 Real Madrid:" in page, "HTML title must target the final score"
assert f'<link rel="canonical" href="{URL}">' in page, "Canonical URL must remain stable"
assert EXPECTED_DESCRIPTION in page, "HTML description must match the feed"
for prop in ("og:type", "og:site_name", "og:title", "og:description", "og:url"):
    assert len(re.findall(rf'<meta property="{re.escape(prop)}"', page)) == 1, (
        f"Expected exactly one {prop} Open Graph tag"
    )
assert len(re.findall(r'<meta name="description"', page)) == 1, "Expected one meta description"
assert "20:00 UTC; 22:00 Sudan time" in page, "Correct UTC and Sudan times must be retained"
assert "19:00 UTC" not in page and "21:00 Sudan time" not in page, "Incorrect old time conversion remains"
assert "Read preview" not in page and "ahead of El Clásico" not in page, "Stale preview language remains"

scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
assert len(scripts) == 1, "Article must contain one JSON-LD block"
schema = json.loads(scripts[0])
assert schema.get("@type") == "NewsArticle", "Article must use NewsArticle schema"
assert schema.get("datePublished") == "2026-10-22", "Original publication date must be preserved"
assert schema.get("dateModified") == "2026-11-15", "Structured data update date is stale"
event = schema.get("about", {})
assert event.get("@type") == "SportsEvent", "Match facts must remain linked to a SportsEvent"
assert event.get("eventStatus") == "https://schema.org/EventCompleted", "Past match must not be marked as upcoming"
assert event.get("startDate") == "2026-10-25T21:00:00+01:00", "Match start time must retain the correct CET offset"

sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
entry = next(
    (node for node in sitemap.findall("sm:url", ns)
     if node.findtext("sm:loc", default="", namespaces=ns) == URL),
    None,
)
assert entry is not None, "El Clásico article must remain in sitemap.xml"
assert entry.findtext("sm:lastmod", default="", namespaces=ns) == "2026-11-15", (
    "Sitemap lastmod must match the article update"
)

section = (ROOT / "section-football.html").read_text(encoding="utf-8")
assert f"articles/{SLUG}.html" in section, "Football section must link to the article"
assert EXPECTED_TITLE in section, "Football section card title is stale"
assert "Read match report" in section, "Football section must label the link as a report"

print("El Clásico report, feed metadata, completed-event schema, Football section and sitemap are consistent.")
