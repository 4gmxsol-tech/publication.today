#!/usr/bin/env python3
"""Generate the canonical XML sitemap for Publication.today.

Article page URLs come from data/articles.json. The script checks that each
listed HTML page exists and writes only canonical, same-domain URLs.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://publication.today"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ET.register_namespace("", NS)

CORE_PAGES = [
    ("", "1.0"),
    ("section-fitness.html", "0.8"),
    ("section-health.html", "0.8"),
    ("section-skincare.html", "0.8"),
    ("section-nutrition.html", "0.8"),
    ("section-wellness.html", "0.8"),
    ("section-beauty.html", "0.8"),
    ("section-football.html", "0.8"),
    ("section-technology.html", "0.8"),
    ("section.html", "0.5"),
    ("privacy.html", "0.3"),
]


def lastmod_for(item: dict) -> str:
    value = item.get("date", "")
    try:
        return datetime.strptime(value, "%B %d, %Y").date().isoformat()
    except (TypeError, ValueError):
        # Broad dates such as "October 2026" don't provide a precise modified date.
        return ""


def main() -> None:
    feed = json.loads((ROOT / "data" / "articles.json").read_text(encoding="utf-8"))
    slugs = [item.get("slug", "") for item in feed]
    if not all(slugs):
        raise SystemExit("Every article must have a non-empty slug.")
    if len(slugs) != len(set(slugs)):
        raise SystemExit("Duplicate article slugs found in data/articles.json.")

    entries: list[tuple[str, str, str]] = []
    for relative, priority in CORE_PAGES:
        target = ROOT / (relative or "index.html")
        if not target.is_file():
            raise SystemExit(f"Core page is missing: {target.relative_to(ROOT)}")
        entries.append((f"{BASE}/" if not relative else f"{BASE}/{relative}", "", priority))

    for item in feed:
        relative = pathlib.Path("articles") / f"{item['slug']}.html"
        if not (ROOT / relative).is_file():
            raise SystemExit(f"Article feed item has no static page: {relative}")
        entries.append((f"{BASE}/{relative.as_posix()}", lastmod_for(item), "0.7"))

    locs = [entry[0] for entry in entries]
    if len(locs) != len(set(locs)):
        raise SystemExit("Duplicate sitemap URLs detected.")

    urlset = ET.Element(f"{{{NS}}}urlset")
    for loc, lastmod, priority in entries:
        node = ET.SubElement(urlset, f"{{{NS}}}url")
        ET.SubElement(node, f"{{{NS}}}loc").text = loc
        if lastmod:
            ET.SubElement(node, f"{{{NS}}}lastmod").text = lastmod
        ET.SubElement(node, f"{{{NS}}}priority").text = priority

    ET.indent(urlset, space="  ")
    ET.ElementTree(urlset).write(
        ROOT / "sitemap.xml", encoding="utf-8", xml_declaration=True
    )
    print(f"Generated sitemap.xml with {len(entries)} URLs ({len(feed)} articles).")


if __name__ == "__main__":
    main()
