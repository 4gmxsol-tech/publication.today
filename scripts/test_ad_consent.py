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


# Verify the runtime call graph: no ad unit or engine may be activated without acceptance.
def extract_block(source, start_marker, end_marker, label):
    start = source.find(start_marker)
    if start < 0:
        errors.append(f"Consent loader is missing {label}.")
        return ""
    end = source.find(end_marker, start + len(start_marker))
    if end < 0:
        errors.append(f"Consent loader has an unterminated {label}.")
        return ""
    return source[start:end]

accept_handler = extract_block(
    consent,
    'accept.addEventListener("click", () => {',
    "\\n    });",
    "Accept handler",
)
reject_handler = extract_block(
    consent,
    'reject.addEventListener("click", () => {',
    "\\n    });",
    "Reject handler",
)
activation = extract_block(
    consent,
    "function activateAds() {",
    "\\n  }\\n\\n  function addStyles()",
    "ad activation function",
)
start_handler = extract_block(
    consent,
    "function start() {",
    "\\n  }\\n\\n  if (document.readyState",
    "startup consent gate",
)

if accept_handler and (
    "writeChoice(\\"accepted\\");" not in accept_handler
    or "activateAds();" not in accept_handler
    or accept_handler.find("writeChoice(\\"accepted\\");") > accept_handler.find("activateAds();")
):
    errors.append("Accept must persist the accepted choice before activating ads.")

if reject_handler and (
    "writeChoice(\\"rejected\\");" not in reject_handler
    or any(call in reject_handler for call in ("activateAds();", "loadAdEngine();", "renderManualSlots();"))
):
    errors.append("Reject must persist rejection and must never activate or load ads.")

if activation and (
    "renderManualSlots();" not in activation
    or "loadAdEngine();" not in activation
):
    errors.append("The single activation function must render approved slots and load the deferred engine.")

if consent.count("activateAds();") != 2:
    errors.append("Ads may be activated only from the accepted-choice startup path and the Accept button.")

if consent.count("loadAdEngine();") != 1 or consent.count("renderManualSlots();") != 1:
    errors.append("Ad engine and manual slots must only be called through the guarded activation function.")

if start_handler and (
    'if (choice === "accepted") { activateAds(); return; }' not in start_handler
    or 'if (choice === "rejected") return;' not in start_handler
):
    errors.append("Returning visitors must load ads only for an accepted choice; rejected visitors must remain ad-free.")
