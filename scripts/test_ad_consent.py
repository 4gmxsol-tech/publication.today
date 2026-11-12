#!/usr/bin/env python3
"""Guard against third-party ad scripts loading before an explicit advertising choice."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECT_AD = re.compile(
    r"<(?:script|iframe)\b[^>]*\bsrc\s*=\s*[\"']https?://(?:www\.)?(?:bicea\.org|bauval\.org|highrevenueformat\.com)/",
    re.IGNORECASE,
)
INLINE_OPTIONS = re.compile(r"\batOptions\s*=", re.IGNORECASE)

errors = []
for page in ROOT.rglob("*.html"):
    if ".git" in page.parts or "node_modules" in page.parts:
        continue
    source = page.read_text(encoding="utf-8", errors="replace")
    if DIRECT_AD.search(source) or INLINE_OPTIONS.search(source):
        errors.append(f"Direct ad code must be consent-gated, not embedded in HTML: {page.relative_to(ROOT)}")

homepage = (ROOT / "index.html").read_text(encoding="utf-8")
privacy = (ROOT / "privacy.html").read_text(encoding="utf-8")
consent = (ROOT / "assets/js/adsterra-ads.js").read_text(encoding="utf-8")
engine = ROOT / "assets/js/adsterra-ads-engine.js"

if homepage.count("data-adsterra-manual-slot=") != 2:
    errors.append("Homepage must retain both consent-managed ad placements.")
for phrase in ('data-adsterra-ad-key=', 'data-adsterra-ad-url=', 'assets/js/adsterra-ads.js'):
    if phrase not in homepage:
        errors.append(f"Homepage must retain consent-managed ad placeholder/script: missing {phrase}")

for phrase in ("Advertising and third-party services", "Accept advertising", "Reject advertising", "local storage", "change or withdraw"):
    if phrase.lower() not in privacy.lower():
        errors.append(f"Privacy notice is missing advertising disclosure or preference control: {phrase}")
if 'id="change-ad-preferences"' not in privacy or 'src="/assets/js/adsterra-ads.js"' not in privacy:
    errors.append("Privacy notice must load the consent manager and expose a preference-change control.")
if "If analytics, advertising, newsletter signup" in privacy:
    errors.append("Privacy notice must not describe already-active advertising as a future service.")

for phrase in ("localStorage.getItem(CONSENT_KEY)", 'choice === "accepted"', 'choice === "rejected"', "adsterra-ads-engine.js", "IS_PRIVACY_PAGE", "showConsent(true)", "if (!IS_PRIVACY_PAGE) activateAds()"):
    if phrase not in consent:
        errors.append(f"Consent loader is missing required gate behavior: {phrase}")

if not engine.is_file():
    errors.append("The deferred advertising engine file is missing.")

if errors:
    print("\n".join(f"FAIL: {item}" for item in errors))
    sys.exit(1)

print("PASS: direct third-party ad code is absent from HTML; ads are loaded only through the explicit consent path.")
