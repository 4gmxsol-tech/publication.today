from html.parser import HTMLParser
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "articles" / "days-between-dates-calculator.html"
URL = "https://publication.today/articles/days-between-dates-calculator.html"
html = PAGE.read_text(encoding="utf-8")

class SchemaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.current = []
        self.schemas = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.capture = True
            self.current = []
    def handle_data(self, data):
        if self.capture:
            self.current.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.capture:
            self.schemas.append("".join(self.current))
            self.capture = False

parser = SchemaParser()
parser.feed(html)
assert len(parser.schemas) == 1, "Expected one JSON-LD graph"
graph = json.loads(parser.schemas[0])
assert graph.get("@context") == "https://schema.org"
nodes = graph.get("@graph", [])
article = next((node for node in nodes if node.get("@type") == "Article"), None)
crumbs = next((node for node in nodes if node.get("@type") == "BreadcrumbList"), None)
assert article is not None, "Article structured data must remain present"
assert article.get("mainEntityOfPage") == URL
assert article.get("datePublished") == "2026-11-11", "Original publication date must remain unchanged"
assert article.get("dateModified") == "2026-11-13", "Article modification date must match the update"
assert crumbs is not None, "BreadcrumbList structured data is missing"
assert crumbs.get("@id") == URL + "#breadcrumb"
items = crumbs.get("itemListElement", [])
expected = [
    (1, "Home", "https://publication.today/"),
    (2, "Technology", "https://publication.today/section-technology.html"),
    (3, "Days Between Dates Calculator", URL),
]
actual = [(item.get("position"), item.get("name"), item.get("item")) for item in items]
assert actual == expected, f"Unexpected breadcrumb sequence: {actual}"
assert '<div class="breadcrumb">' in html
assert '<a href="../index.html">Home</a>' in html
assert '<a href="../section-technology.html">Technology</a>' in html
assert '<span aria-current="page">Days Between Dates Calculator</span>' in html
sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
entry = next((node for node in sitemap.findall("sm:url", ns) if node.findtext("sm:loc", default="", namespaces=ns) == URL), None)
assert entry is not None, "Date calculator must remain in the sitemap"
assert entry.findtext("sm:lastmod", default="", namespaces=ns) == "2026-11-13", "Sitemap lastmod must match the page update"
feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
feed_item = next((item for item in feed if item.get("slug") == "days-between-dates-calculator"), None)
assert feed_item and feed_item.get("lastmod") == "2026-11-13", "Article feed lastmod must match the page update"
print("PASS: visible breadcrumb navigation and matching Article/BreadcrumbList structured data.")
