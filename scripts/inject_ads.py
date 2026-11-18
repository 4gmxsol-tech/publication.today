#!/usr/bin/env python3
"""Ensure every Publication Today article loads its consent-gated ad controller."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAG = '<script src="/assets/js/adsterra-ads.js" defer></script>'


def inject_ads(root=ROOT):
    root = Path(root)
    controller = root / "assets" / "js" / "adsterra-ads.js"
    if not controller.is_file():
        raise ValueError("Consent controller is missing: assets/js/adsterra-ads.js")

    pages = sorted(page for page in (root / "articles").glob("*.html") if page.name.lower() != "index.html")
    injected = 0
    for page in pages:
        source = page.read_text(encoding="utf-8")
        count = source.count("adsterra-ads.js")
        if count > 1:
            raise ValueError(f"Duplicate Adsterra controllers in {page.relative_to(root)}")
        if count == 0:
            position = source.lower().rfind("</body>")
            if position < 0:
                raise ValueError(f"Missing </body> in {page.relative_to(root)}")
            source = source[:position] + TAG + "\n" + source[position:]
            page.write_text(source, encoding="utf-8")
            injected += 1
        if source.count("adsterra-ads.js") != 1:
            raise ValueError(f"Controller not present exactly once in {page.relative_to(root)}")
    return injected, len(pages)


if __name__ == "__main__":
    added, total = inject_ads()
    print(f"Consent-gated Adsterra controller verified on {total} article pages; {added} newly injected.")
