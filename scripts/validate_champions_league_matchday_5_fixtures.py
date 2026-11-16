#!/usr/bin/env python3
"""Regression checks for the UEFA Champions League Matchday 5 fixture guide."""
from html.parser import HTMLParser
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SLUG = "champions-league-matchday-5-fixtures-kickoff-times-november-24-25-2026"
URL = "https://publication.today/articles/" + SLUG + ".html"
TITLE = "Champions League Matchday 5 Fixtures: Full Schedule & Kick-off Times"
DESCRIPTION = "See all 18 UEFA Champions League Matchday 5 fixtures for Nov. 24–25, 2026, with CET, US Eastern and Sudan times, standings and US streaming info."
ARTICLE = ROOT / "articles" / (SLUG + ".html")
FEED = ROOT / "data" / "articles.json"
SECTION = ROOT / "section-football.html"
PSV_PREVIEW = ROOT / "articles/real-madrid-vs-psv-champions-league-matchday-5-preview-november-24-2026.html"
SITEMAP = ROOT / "sitemap.xml"

FIXTURES = [
    "Bodø/Glimt vs LASK", "Galatasaray vs Aston Villa",
    "Arsenal vs Borussia Dortmund", "Como vs AEK Athens",
    "Feyenoord vs Porto", "Manchester City vs Napoli",
    "Leipzig vs Lens", "Real Madrid vs PSV Eindhoven",
    "Slovan Bratislava vs Real Betis", "Sabah vs Barcelona",
    "Slavia Praha vs Villarreal", "Atlético de Madrid vs Viking",
    "Club Brugge vs Liverpool", "Inter vs Stuttgart",
    "Shakhtar Donetsk vs Fenerbahçe", "Lille vs Bayern München",
    "Paris Saint-Germain vs Roma", "Sporting CP vs Manchester United",
]

STANDINGS_ROWS = [
    '<tr><td>1</td><td>Paris Saint-Germain</td><td>4</td><td>4–0–0</td><td>20–5</td><td>+15</td><td>12</td></tr>',
    '<tr><td>2</td><td>Real Madrid</td><td>4</td><td>4–0–0</td><td>13–7</td><td>+6</td><td>12</td></tr>',
    '<tr><td>3</td><td>Arsenal</td><td>4</td><td>3–1–0</td><td>8–3</td><td>+5</td><td>10</td></tr>',
    '<tr><td>4</td><td>Como</td><td>4</td><td>3–0–1</td><td>19–6</td><td>+13</td><td>9</td></tr>',
    '<tr><td>5</td><td>Barcelona</td><td>4</td><td>3–0–1</td><td>14–6</td><td>+8</td><td>9</td></tr>',
    '<tr><td>6</td><td>Aston Villa</td><td>4</td><td>3–0–1</td><td>12–6</td><td>+6</td><td>9</td></tr>',
    '<tr><td>7</td><td>Manchester City</td><td>4</td><td>3–0–1</td><td>12–7</td><td>+5</td><td>9</td></tr>',
    '<tr><td>8</td><td>Liverpool</td><td>4</td><td>3–0–1</td><td>14–10</td><td>+4</td><td>9</td></tr>',
    '<tr><td>9</td><td>Club Brugge</td><td>4</td><td>3–0–1</td><td>11–7</td><td>+4</td><td>9</td></tr>',
    '<tr><td>10</td><td>Sporting CP</td><td>4</td><td>3–0–1</td><td>8–4</td><td>+4</td><td>9</td></tr>',
    '<tr><td>11</td><td>Real Betis</td><td>4</td><td>3–0–1</td><td>8–6</td><td>+2</td><td>9</td></tr>',
    '<tr><td>12</td><td>Borussia Dortmund</td><td>4</td><td>3–0–1</td><td>7–5</td><td>+2</td><td>9</td></tr>',
]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.h1 = []
        self.in_title = False
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
    parser = Parser()
    parser.feed(html)
    title = " ".join("".join(parser.title).split())
    h1 = " ".join("".join(parser.h1).split())
    description = parser.meta.get("description", "").strip()

    if title != TITLE or h1 != TITLE:
        errors.append("document title and visible H1 must match the fixture-guide title")
    if parser.canonical != URL:
        errors.append("canonical must point to the HTTPS fixture-guide URL")
    if parser.meta.get("og:title") != TITLE or parser.meta.get("twitter:title") != TITLE:
        errors.append("Open Graph and Twitter titles must match the document title")
    if parser.meta.get("og:description") != DESCRIPTION or parser.meta.get("twitter:description") != DESCRIPTION or description != DESCRIPTION:
        errors.append("social and search descriptions must match")
    if html.count("<h1>") != 1:
        errors.append("article must contain exactly one H1")

    for fixture in FIXTURES:
        if html.count(fixture) < 1:
            errors.append("missing fixture: " + fixture)
    if len(FIXTURES) != 18 or len(set(FIXTURES)) != 18:
        errors.append("fixture test list must contain 18 unique matches")

    for phrase in ("Tuesday, November 24, 2026: Champions League fixtures", "Wednesday, November 25, 2026: Champions League fixtures",
                   "18:45 CET", "12:45 p.m. ET", "17:45 UTC", "19:45 Sudan",
                   "21:00 CET", "3:00 p.m. ET", "20:00 UTC", "22:00 Sudan",
                   "CET is UTC+1", "US Eastern Time is Eastern Standard Time (EST, UTC−5)", "Sudan is UTC+2"):
        if phrase not in html:
            errors.append("missing schedule or time-zone detail: " + phrase)

    if html.count('class="fixture-table-wrap"') != 3:
        errors.append("both fixture tables and the standings table must use the responsive horizontal-scroll wrapper")
    if "min-width:760px" not in html:
        errors.append("five-column fixture tables must retain the responsive minimum width")
    if html.count("12:45 p.m. ET</td>") != 4:
        errors.append("exactly four early fixtures must convert to 12:45 p.m. ET")
    if html.count("3:00 p.m. ET</td>") != 14:
        errors.append("exactly fourteen standard fixtures must convert to 3:00 p.m. ET")
    if "<h2>Champions League standings before Matchday 5</h2>" not in html:
        errors.append("pre-Matchday 5 league-phase standings section is missing")
    for row in STANDINGS_ROWS:
        if row not in html:
            errors.append("missing or changed UEFA standings row: " + row)
    if "Nine clubs are currently level on nine points" not in html:
        errors.append("standings context must explain the nine-club tie on nine points")
    if "https://documents.uefa.com/r/Regulations-of-the-UEFA-Champions-League-2026/27/Article-17-Match-system-league-phase-Online?contentId=z80npkZwtB5MkmwVqnk6XA" not in html:
        errors.append("qualification format must link to UEFA Article 17")
    for phrase in ("positions 1–8 qualify directly for the round of 16", "positions 9–24 enter the knockout-phase play-offs", "positions 25–36 are eliminated"):
        if phrase not in html:
            errors.append("missing UEFA league-phase qualification rule: " + phrase)

    if "https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst" not in html:
        errors.append("US Eastern standard-time conversion must link to NIST")
    if 'href="https://www.paramountplus.com/shows/uefa-champions-league/"' not in html:
        errors.append("US streaming guidance must link to the official Paramount+ Champions League page")
    if "CBS confirms that Paramount+ subscribers can stream Champions League matches live" not in html:
        errors.append("US streaming guidance must describe the CBS-confirmed live-streaming option")
    if "https://cbsi.my.salesforce-sites.com/CBSi/articles/en_US/Knowledge/PD-How-do-I-find-UEFA-Champions-League-and-Europa-League-schedules-and-watch-matches-live?data=&amp;popup=false&amp;template=ottShoTemplate" not in html:
        errors.append("US streaming guidance must link to CBS's official help article")
    if 'href="football-match-time-zone-converter.html"' not in html:
        errors.append("Fixture guide must link to the football time-zone converter")
    if 'href="football-match-countdown.html"' not in html:
        errors.append("Fixture guide must link to the football match countdown")
    if "uefa.com" not in html:
        errors.append("official UEFA source link is required")
    if f'href="{SLUG}.html"' not in PSV_PREVIEW.read_text(encoding="utf-8"):
        errors.append("existing Real Madrid vs PSV preview must link to the full fixture guide")

    scripts = html.split('<script type="application/ld+json">')[1:]
    if len(scripts) != 1:
        errors.append("article must contain exactly one JSON-LD script")
    else:
        try:
            schema = json.loads(scripts[0].split("</script>", 1)[0])
            if schema.get("@type") != "NewsArticle":
                errors.append("fixture guide must use NewsArticle schema")
            if schema.get("headline") != TITLE or schema.get("description") != DESCRIPTION:
                errors.append("NewsArticle headline and description must match metadata")
            if schema.get("datePublished") != "2026-11-15" or schema.get("dateModified") != "2026-11-16":
                errors.append("NewsArticle must preserve its November 15 publication date and reflect the November 16 update")
            if schema.get("articleSection") != "Football":
                errors.append("articleSection must be Football")
            for phrase in ("Champions League standings before Matchday 5", "Champions League table 2026/27", "UEFA Champions League top eight"):
                if phrase not in schema.get("keywords", ""):
                    errors.append("NewsArticle keywords are missing standings phrase: " + phrase)
            if schema.get("mainEntityOfPage", {}).get("@id") != URL:
                errors.append("NewsArticle mainEntityOfPage must match canonical URL")
        except (json.JSONDecodeError, AttributeError):
            errors.append("NewsArticle JSON-LD must be valid and complete")

    feed = json.loads(FEED.read_text(encoding="utf-8"))
    matches = [item for item in feed if item.get("slug") == SLUG]
    if len(matches) != 1:
        errors.append("fixture guide must appear exactly once in the article feed")
    else:
        item = matches[0]
        if item.get("category") != "football" or item.get("title") != TITLE:
            errors.append("article feed title/category is incorrect")
        if item.get("date") != "November 15, 2026" or item.get("lastmod") != "2026-11-16":
            errors.append("article feed must preserve its publication date and use the November 16 lastmod")
        if "Champions League Matchday 5 fixtures" not in item.get("tags", []):
            errors.append("article feed is missing the primary search phrase")
        if not {"Champions League Matchday 5 US kickoff times", "Champions League fixtures ET", "Champions League standings before Matchday 5", "Champions League table 2026/27", "UEFA Champions League top eight", "Champions League league phase table"}.issubset(set(item.get("tags", []))):
            errors.append("article feed is missing the US Eastern or standings search phrases")
        if "US Eastern" not in item.get("excerpt", "") or "standings" not in item.get("excerpt", "").lower():
            errors.append("article feed excerpt must mention US Eastern kick-off times and the standings snapshot")
        required_tags = {
            "Champions League live stream US",
            "where to watch Champions League in US",
            "Paramount+ Champions League",
            "football match time zone converter",
            "football match countdown",
        }
        if not required_tags.issubset(set(item.get("tags", []))):
            errors.append("article feed must include US streaming and matchday-tool search terms")
        body_headings = {part.get("heading") for part in item.get("body", [])}
        if not {"Where to watch in the United States", "Matchday planning tools", "Champions League standings before Matchday 5"}.issubset(body_headings):
            errors.append("article feed must include the standings, US streaming and matchday-tools sections")

    section = SECTION.read_text(encoding="utf-8")
    if section.count(f'href="articles/{SLUG}.html"') != 3:
        errors.append("Football section must expose image, title and CTA links to the guide")
    if "US Eastern" not in section:
        errors.append("Football section card must mention US Eastern kick-off times")
    if "US streaming guidance" not in section:
        errors.append("Football section card must surface the new US streaming information")
    if "league-phase standings" not in section or "pre-matchday league table snapshot" not in section:
        errors.append("Football section metadata and featured card must surface league-phase standings")

    sitemap = ET.parse(SITEMAP).getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text.strip() for node in sitemap.findall("sm:url/sm:loc", ns)]
    if urls.count(URL) != 1:
        errors.append("fixture guide must appear exactly once in sitemap")
    sitemap_entry = next((node for node in sitemap.findall("sm:url", ns)
                          if node.findtext("sm:loc", default="", namespaces=ns) == URL), None)
    if sitemap_entry is None or sitemap_entry.findtext("sm:lastmod", default="", namespaces=ns) != "2026-11-16":
        errors.append("fixture guide sitemap lastmod must match the November 16 content update")
    if len(urls) != len(set(urls)):
        errors.append("sitemap must not contain duplicate URLs")
    if "https://publication.today/section-football.html" not in urls:
        errors.append("Football section must remain in sitemap")

    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: 18 Matchday 5 fixtures, UEFA standings snapshot, qualification rules, time conversions, article metadata, feed, Football links, and sitemap are consistent.")

if __name__ == "__main__":
    main()
