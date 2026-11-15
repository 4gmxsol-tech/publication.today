#!/usr/bin/env python3
"""Ensure static Publication Today article pages do not download the article feed."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_JS = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
ARTICLE_TEMPLATE = (ROOT / "article.html").read_text(encoding="utf-8")
SECTION_TEMPLATE = (ROOT / "section.html").read_text(encoding="utf-8")

guard = 'const needsArticleData = Boolean($("#article-grid") || $("#section-content") || $("#article-content"));'
start = MAIN_JS.index("const init = async")
end = MAIN_JS.index("const initArticlePage", start)
init = MAIN_JS[start:end]

assert guard in init, "article feed loading must be guarded by data-dependent page mounts"
guard_pos = init.index(guard)
if_pos = init.index("if (needsArticleData)", guard_pos)
fetch_pos = init.index('fetch("data/articles.json")')
assert guard_pos < if_pos < fetch_pos, "article feed fetch must occur inside the data-dependent guard"
assert init.count('fetch("data/articles.json")') == 1, "article feed should have one guarded fetch"
assert "initArticlePage();" in init and "initSectionPage();" in init, "dynamic content initializers must remain available"
assert 'id="article-grid"' in INDEX, "homepage must retain its article-grid mount"
assert 'id="article-content"' in ARTICLE_TEMPLATE, "dynamic article template must retain its content mount"
assert 'id="section-content"' in SECTION_TEMPLATE, "dynamic section template must retain its content mount"

print("PASS: article data is fetched only by pages with a data-driven content mount; static pages avoid the article-index request.")
