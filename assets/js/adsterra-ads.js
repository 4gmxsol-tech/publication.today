(() => {
  "use strict";
  if (window.__publicationAdConsentInitialized) return;
  window.__publicationAdConsentInitialized = true;

  const CONSENT_KEY = "publication-ad-consent-v1";
  const ENGINE_URL = "/assets/js/adsterra-ads-engine.js";
  const ALLOWED_HOSTS = ["bicea.org", "bauval.org", "highrevenueformat.com", "www.highrevenueformat.com"];

  function readChoice() {
    try { return window.localStorage.getItem(CONSENT_KEY); } catch { return null; }
  }

  function writeChoice(value) {
    try { window.localStorage.setItem(CONSENT_KEY, value); } catch {}
  }

  function renderManualSlots() {
    document.querySelectorAll("[data-adsterra-manual-slot]").forEach((placeholder) => {
      const key = (placeholder.getAttribute("data-adsterra-ad-key") || "").trim();
      const rawUrl = (placeholder.getAttribute("data-adsterra-ad-url") || "").trim();
      const width = Number(placeholder.getAttribute("data-adsterra-width") || 320);
      const height = Number(placeholder.getAttribute("data-adsterra-height") || 50);
      let url;
      try { url = new URL(rawUrl, window.location.href); } catch { return; }
      if (!/^[a-f0-9]{32}$/i.test(key) || url.protocol !== "https:" || ALLOWED_HOSTS.indexOf(url.hostname) < 0) return;
      if (!((width === 320 && height === 50) || (width === 300 && height === 250) || (width === 728 && height === 90))) return;

      const slot = document.createElement("section");
      slot.className = "ad-placement";
      slot.setAttribute("aria-label", "Advertisement");
      slot.style.cssText = "box-sizing:border-box;width:100%;padding:20px 12px;margin:24px auto;text-align:center;clear:both;";
      const label = document.createElement("span");
      label.textContent = "Advertisement";
      label.style.cssText = "display:block;font-size:11px;font-weight:600;letter-spacing:.12em;margin:0 0 10px;color:#777;";
      const frame = document.createElement("div");
      frame.style.cssText = "width:" + width + "px;max-width:100%;min-height:" + height + "px;margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;";
      const adFrame = document.createElement("iframe");
      adFrame.title = "Advertisement";
      adFrame.loading = "lazy";
      adFrame.width = String(width);
      adFrame.height = String(height);
      adFrame.style.cssText = "display:block;border:0;max-width:100%;margin:0 auto;";
      adFrame.setAttribute("scrolling", "no");
      const safeKey = key.toLowerCase();
      adFrame.srcdoc = '<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><script>var atOptions={key:\'' + safeKey + '\',format:\'iframe\',height:' + height + ',width:' + width + ',params:{}};<\/script><script src="' + url.href + '"><\/script></body></html>';
      frame.appendChild(adFrame);
      slot.append(label, frame);
      placeholder.replaceWith(slot);
    });
  }

  function loadAdEngine() {
    if (document.querySelector('script[data-adsterra-engine="true"]')) return;
    const script = document.createElement("script");
    script.src = ENGINE_URL;
    script.async = true;
    script.setAttribute("data-adsterra-engine", "true");
    document.body.appendChild(script);
  }

  function activateAds() {
    renderManualSlots();
    loadAdEngine();
  }

  function addStyles() {
    if (document.getElementById("publication-ad-consent-style")) return;
    const style = document.createElement("style");
    style.id = "publication-ad-consent-style";
    style.textContent = "#publication-ad-consent{box-sizing:border-box;position:fixed;z-index:99999;left:12px;right:12px;bottom:12px;width:min(620px,calc(100% - 24px));margin:0 auto;padding:16px;border:1px solid #596174;border-radius:14px;background:#171b28;color:#f4f6ff;box-shadow:0 8px 36px #0008;font:14px/1.5 system-ui,sans-serif}#publication-ad-consent p{margin:0 0 12px}#publication-ad-consent a{display:inline-block;margin:0 0 12px;color:#a5f36b;text-decoration:underline;text-underline-offset:3px}#publication-ad-consent .actions{display:flex;gap:10px;flex-wrap:wrap}#publication-ad-consent button{border:1px solid #7c879d;border-radius:8px;padding:9px 13px;background:transparent;color:inherit;font:inherit;cursor:pointer}#publication-ad-consent button:first-child{background:#a5f36b;color:#10150d;border-color:#a5f36b;font-weight:700}#publication-ad-consent button:focus-visible,#publication-ad-consent a:focus-visible{outline:2px solid #a5f36b;outline-offset:3px}";
    document.head.appendChild(style);
  }

  function showConsent() {
    if (document.getElementById("publication-ad-consent")) return;
    const panel = document.createElement("aside");
    panel.id = "publication-ad-consent";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", "Advertising preferences");
    const copy = document.createElement("p");
    copy.textContent = "Publication Today uses third-party advertising. Ad scripts load only if you accept; you can reject and continue reading.";
    const privacy = document.createElement("a");
    privacy.href = "/privacy.html";
    privacy.textContent = "Read the privacy notice";
    const actions = document.createElement("div");
    actions.className = "actions";
    const accept = document.createElement("button");
    accept.type = "button";
    accept.textContent = "Accept advertising";
    const reject = document.createElement("button");
    reject.type = "button";
    reject.textContent = "Reject advertising";
    accept.addEventListener("click", () => {
      writeChoice("accepted");
      panel.remove();
      activateAds();
    });
    reject.addEventListener("click", () => {
      writeChoice("rejected");
      panel.remove();
    });
    actions.append(accept, reject);
    panel.append(copy, privacy, actions);
    document.body.appendChild(panel);
  }

  function start() {
    if (/\/privacy\.html$/i.test(window.location.pathname)) return;
    addStyles();
    const choice = readChoice();
    if (choice === "accepted") { activateAds(); return; }
    if (choice === "rejected") return;
    showConsent();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();