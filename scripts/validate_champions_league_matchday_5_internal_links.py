#!/usr/bin/env python3
"""Validate the internal-link cluster for Champions League Matchday 5 coverage."""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUGS = {
    "fixtures": "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026",
    "galatasaray": "galatasaray-vs-aston-villa-champions-league-matchday-5-preview-november-24-2026",
    "madrid": "real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026",
    "sabah": "sabah-vs-barcelona-champions-league-matchday-5-preview-november-25-2026",
    "arsenal": "arsenal-vs-borussia-dortmund-champions-league-matchday-5-preview-november-24-2026",
    "city": "manchester-city-vs-napoli-champions-league-matchday-5-preview-november-24-2026",
    "inter": "inter-vs-stuttgart-champions-league-matchday-5-preview-november-25-2026",
    "club_brugge": "club-brugge-vs-liverpool-champions-league-matchday-5-preview-november-25-2026",
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

# The full schedule must expose all seven individual previews; every preview
# must lead readers back to the full schedule.
assert f'href="{SLUGS["galatasaray"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Galatasaray vs Aston Villa preview"
)
assert f'href="{SLUGS["madrid"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Real Madrid vs PSV preview"
)
assert f'href="{SLUGS["sabah"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Sabah vs Barcelona preview"
)
assert f'href="{SLUGS["arsenal"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Arsenal vs Borussia Dortmund preview"
)
assert f'href="{SLUGS["fixtures"]}.html"' in PAGES["galatasaray"], (
    "Galatasaray vs Aston Villa preview must link to the full schedule"
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

# The full schedule and all seven previews must remain in the football feed and sitemap.
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
feed_by_slug = {item.get("slug"): item for item in feed}
fixture_item = feed_by_slug.get(SLUGS["fixtures"])
assert fixture_item and fixture_item.get("date") == "November 15, 2026", "Fixture guide publication date must remain unchanged"
assert fixture_item.get("lastmod") == "2026-11-16", "Fixture feed lastmod must reflect the new internal-link update"
assert '"datePublished":"2026-11-15","dateModified":"2026-11-16"' in PAGES["fixtures"], "Fixture NewsArticle modified date is stale"
assert "Updated November 16, 2026" in PAGES["fixtures"], "Fixture guide visible update date is stale"
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



# The Galatasaray vs Aston Villa preview uses the early Matchday 5 slot and
# only verified results/points; it does not publish an unsupported table rank.
gal = PAGES["galatasaray"]
for phrase in (
    "Tuesday, November 24, 2026", "17:45 GMT", "18:45 CET",
    "20:45 local time in Istanbul", "RAMS Park",
    "12:45 p.m. US Eastern Standard Time (EST, UTC−5)",
    "9:45 a.m. US Pacific Standard Time (PST, UTC−8)", "19:45 in Sudan (UTC+2)",
    "six points", "nine points", "uefa.com", "avfc.co.uk", "nist.gov"
):
    assert phrase in gal, f"Galatasaray vs Aston Villa preview is missing verified detail or source: {phrase}"
assert "<title>Galatasaray vs Aston Villa: RAMS Park, Kick-off &amp; Preview</title>" in gal, "Galatasaray preview title is stale"
assert gal.count("<h1>") == 1, "Galatasaray preview must contain exactly one H1"
gal_description = re.search(r'<meta name="description" content="([^"]+)">', gal).group(1)
assert gal_description == "Galatasaray host Aston Villa on Nov. 24 at 18:45 CET: 12:45 p.m. EST / 9:45 a.m. PST at RAMS Park. Check verified kick-off times and recent results."
assert f'<meta property="og:description" content="{gal_description}">' in gal
assert f'<meta name="twitter:description" content="{gal_description}">' in gal
gal_schema = json.loads(re.search(r'<script type="application/ld\\+json">(.*?)</script>', gal, re.S).group(1))
assert gal_schema.get("description") == gal_description
assert gal_schema.get("datePublished") == "2026-11-16" and gal_schema.get("dateModified") == "2026-11-16"
assert "Galatasaray vs Aston Villa 12:45 PM ET" in gal_schema.get("keywords", "")
assert "Galatasaray vs Aston Villa 9:45 AM PT" in gal_schema.get("keywords", "")
gal_item = feed_by_slug.get(SLUGS["galatasaray"])
assert gal_item and gal_item.get("category") == "football", "Galatasaray preview must be in the Football feed"
assert gal_item.get("date") == "November 16, 2026" and gal_item.get("lastmod") == "2026-11-16"
assert gal_item.get("excerpt") == gal_description, "Galatasaray feed excerpt must match search metadata"
assert "Galatasaray vs Aston Villa 12:45 PM ET" in gal_item.get("tags", [])
assert "Galatasaray vs Aston Villa 9:45 AM PT" in gal_item.get("tags", [])

# The Manchester City vs Napoli preview joins the same Matchday 5 internal-link cluster.
assert f'href="{SLUGS["city"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Manchester City vs Napoli preview"
)
assert f'href="{SLUGS["inter"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Inter vs Stuttgart preview"
)
assert f'href="{SLUGS["club_brugge"]}.html"' in PAGES["fixtures"], (
    "Full schedule is missing the Club Brugge vs Liverpool preview"
)
for key in ("galatasaray", "inter", "club_brugge"):
    assert f'href="{SLUGS["fixtures"]}.html"' in PAGES[key], (
        f"{key} preview must link back to the full Matchday 5 schedule"
    )
assert f'href="{SLUGS["fixtures"]}.html"' in PAGES["city"], (
    "Manchester City vs Napoli preview must link to the full schedule"
)
assert f'href="{SLUGS["arsenal"]}.html"' in PAGES["city"], (
    "Manchester City vs Napoli preview must cross-link to the Arsenal preview"
)
for phrase in (
    "Tuesday, November 24, 2026", "20:00 GMT", "21:00 CET", "20:00 UTC",
    "3:00 p.m. US Eastern Standard Time (EST, UTC−5)", "22:00 in Sudan",
    "Etihad Stadium", "3–2 away win against Leipzig", "4–1 away defeat to Porto",
    "uefa.com", "mancity.com", "sscnapoli.it", "nist.gov"
):
    assert phrase in PAGES["city"], (
        f"Manchester City vs Napoli preview is missing verified detail or source: {phrase}"
    )
assert "<title>Manchester City vs Napoli: Kick-off Time, Etihad Stadium &amp; Match Preview</title>" in PAGES["city"], (
    "City preview title must match its intended search title"
)
assert PAGES["city"].count("<h1>") == 1, "City preview must contain exactly one H1"
city_description = re.search(r'<meta name="description" content="([^"]+)">', PAGES["city"]).group(1)
assert city_description == "Manchester City host Napoli on Nov. 24 at 21:00 CET: 3 p.m. EST / noon PST. Check the Etihad, recent form and league-phase points.", "City preview meta description is stale"
assert f'<meta property="og:description" content="{city_description}">' in PAGES["city"], "City preview Open Graph description must match"
assert f'<meta name="twitter:description" content="{city_description}">' in PAGES["city"], "City preview Twitter description must match"
city_schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', PAGES["city"], re.S).group(1))
assert city_schema.get("description") == city_description, "City NewsArticle description must match search metadata"
assert city_schema.get("datePublished") == "2026-11-15" and city_schema.get("dateModified") == "2026-11-16", "City NewsArticle dates must match the article review date"
assert "Manchester City vs Napoli standings" in city_schema.get("keywords", ""), "City NewsArticle keywords must include the league-table query"
assert "Man City vs Napoli 3 PM ET" in city_schema.get("keywords", ""), "City NewsArticle keywords must include the US kick-off query"
assert "UEFA Champions League league phase table" in city_schema.get("keywords", ""), "City NewsArticle keywords must include the standings query"
assert "<h2>League-phase points before Matchday 5</h2>" in PAGES["city"], "City preview heading must describe points rather than unverified ranks"
assert "Manchester City have 9 points from three wins and one defeat" in PAGES["city"], "City preview is missing the verified UEFA points total"
assert "Napoli have 3 points from one win and three defeats" in PAGES["city"], "City preview is missing the verified Napoli points total"
assert "Manchester City seventh" not in PAGES["city"] and "Napoli are 27th" not in PAGES["city"], "Do not publish unverified table positions"

city_item = feed_by_slug.get(SLUGS["city"])
assert city_item and city_item.get("category") == "football", "City preview must be in the football feed"
assert city_item.get("date") == "November 15, 2026" and city_item.get("lastmod") == "2026-11-16", (
    "City preview feed dates must be November 15, 2026"
)
assert "Manchester City vs Napoli standings" in city_item.get("tags", []), (
    "City preview must include the league-table search phrase"
)
assert "Man City vs Napoli 3 PM ET" in city_item.get("tags", []), (
    "City preview must include the US kick-off search phrase"
)
assert city_item.get("excerpt") == "Manchester City host Napoli on Nov. 24 at 21:00 CET: 3 p.m. EST / noon PST. Check the Etihad, recent form and league-phase points.", "City preview excerpt must match the search description"
assert "Champions League Matchday 5" in city_item.get("tags", []), (
    "City preview must target the Matchday 5 search phrase"
)
section_html = (ROOT / "section-football.html").read_text(encoding="utf-8")
fixture_card_position = section_html.index(f'href="articles/{SLUGS["fixtures"]}.html"')
for preview_key in ("galatasaray", "club_brugge", "inter", "city", "arsenal", "madrid", "sabah"):
    preview_position = section_html.index(f'href="articles/{SLUGS[preview_key]}.html"')
    assert fixture_card_position < preview_position, (
        f"Full Matchday 5 fixtures card must appear before the {preview_key} preview"
    )
assert section_html.count(f'href="articles/{SLUGS["galatasaray"]}.html') == 3, (
    "Football section must expose the Galatasaray preview image, title and CTA links"
)
assert section_html.count(f'href="articles/{SLUGS["city"]}.html"') == 3, (
    "Football section must expose the City preview image, title and CTA links"
)
assert URLS["city"] in entries, "City preview must be present in the sitemap"
city_entry = next(node for node in sitemap.findall("sm:url", ns)
                  if node.findtext("sm:loc", default="", namespaces=ns) == URLS["city"])
assert city_entry.findtext("sm:lastmod", default="", namespaces=ns) == city_item["lastmod"], (
    "City preview feed and sitemap lastmod must match"
)

# Keep the upcoming Matchday 5 coverage together in chronological order before
# the later Matchday 6 schedule, so the section prioritizes the next fixtures.
priority_section_slugs = [
    SLUGS["fixtures"],
    "champions-league-tiebreaker-rules-2026-27",
    SLUGS["galatasaray"],
    SLUGS["arsenal"],
    SLUGS["city"],
    SLUGS["madrid"],
    SLUGS["sabah"],
    SLUGS["club_brugge"],
    SLUGS["inter"],
    "champions-league-matchday-6-fixtures-kickoff-times-december-8-9-2026",
]
section_card_positions = [
    section_html.index(
        f'<article class="article-card"><a class="article-visual visual-football" href="articles/{slug}.html"'
    )
    for slug in priority_section_slugs
]
assert section_card_positions == sorted(section_card_positions), (
    "Football hub must show the full Matchday 5 schedule, its seven dated previews, "
    "then evergreen tiebreaker guidance and the later Matchday 6 schedule"
)
assert len(re.findall(r'<article class="article-card">', section_html)) == 20, (
    "Reordering must preserve all 19 Football section cards"
)

# Keep each Matchday 5 card snippet aligned with its article-feed excerpt.
# This prevents the Football hub from showing stale kick-off information after
# the individual preview metadata has been updated.
section_cards = re.findall(r'<article class="article-card">.*?</article>', section_html, re.S)
for preview_key in ("galatasaray", "arsenal", "city", "madrid", "sabah", "club_brugge", "inter"):
    slug = SLUGS[preview_key]
    item = feed_by_slug.get(slug)
    assert item and item.get("excerpt"), f"{preview_key} preview must have a feed excerpt"
    card = next(
        (candidate for candidate in section_cards if f'href="articles/{slug}.html"' in candidate),
        None,
    )
    assert card is not None, f"{preview_key} preview card is missing from the Football hub"
    card_excerpt = re.search(r"<p>(.*?)</p>", card, re.S)
    assert card_excerpt, f"{preview_key} preview card must have a descriptive excerpt"
    assert card_excerpt.group(1) == item["excerpt"], (
        f"{preview_key} Football card excerpt must match the article feed"
    )
    assert "EST" in card_excerpt.group(1) and "PST" in card_excerpt.group(1), (
        f"{preview_key} Football card must expose both US Eastern and Pacific kick-off times"
    )

print("Champions League Matchday 5 previews, canonical metadata, feed, sitemap, and Football hub order are valid.")
