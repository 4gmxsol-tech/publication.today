(() => {
  if (window.__adsterraEditorialMounted) return;
  window.__adsterraEditorialMounted = true;
  const main = document.querySelector("main");
  if (!main || main.querySelector("[data-adsterra-slot]")) return;
  // A manually embedded unit already monetizes this article; do not stack another ad.
  if (main.querySelector('.ad-placement, [aria-label="Advertisement"] iframe, iframe[src*="adsterra"], script[src*="adsterra"], script[src*="highrevenueformat"], script[src*="bauval.org"], script[src*="bicea.org"]')) return;
  const paragraphs = [...main.querySelectorAll("article p, .article-body p, .content-section p, .article-content p, main p")]
    .filter(p => p.textContent.trim().length > 45 && !p.closest("nav, footer, header, [aria-label='Advertisement']"));
  if (!paragraphs.length) return;
  const makeSlot = (kind) => {
    const wide = kind === "banner";
    const slot = document.createElement("section");
    slot.dataset.adsterraSlot = kind;
    slot.setAttribute("aria-label", "Advertisement");
    slot.style.cssText = "box-sizing:border-box;width:100%;padding:20px 12px;margin:24px auto;text-align:center;clear:both;";
    const label = document.createElement("p");
    label.textContent = "ADVERTISEMENT";
    label.style.cssText = "font-size:11px;font-weight:600;letter-spacing:.12em;margin:0 0 10px;color:#777;";
    const frame = document.createElement("div");
    frame.style.cssText = `width:${wide ? 320 : 300}px;max-width:100%;min-height:${wide ? 50 : 250}px;margin:0 auto;display:flex;align-items:center;justify-content:center;overflow:hidden;`;
    // Isolate each ad unit's atOptions global so multiple placements cannot overwrite each other.
    const adFrame = document.createElement("iframe");
    adFrame.title = "Advertisement";
    adFrame.loading = "lazy";
    adFrame.width = wide ? "320" : "300";
    adFrame.height = wide ? "50" : "250";
    adFrame.style.cssText = "display:block;border:0;max-width:100%;margin:0 auto;";
    adFrame.setAttribute("scrolling", "no");
    const adKey = wide ? "2209ef0cfff2a4129317e1761af59d13" : "3e536f54144c351cf061de39db30858d";
    const adHost = wide ? "https://bicea.org/22/2209ef0cfff2a4129317e1761af59d13" : "https://bicea.org/22/3e536f54144c351cf061de39db30858d";
    adFrame.srcdoc = `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><script>var atOptions={key:'${adKey}',format:'iframe',height:${wide ? 50 : 250},width:${wide ? 320 : 300},params:{}};</script><script src="${adHost}"></script></body></html>`;
    frame.append(adFrame);
    slot.append(label, frame);
    return slot;
  };
  // Put the rectangle after the second substantive paragraph when possible, keeping the opening readable.
  const firstIndex = paragraphs.length >= 3 ? 1 : 0;
  paragraphs[firstIndex].insertAdjacentElement("afterend", makeSlot("rectangle"));
  // Long reads get one compact banner near the midpoint, not on short articles.
  if (paragraphs.length >= 7) {
    const midpoint = paragraphs[Math.floor(paragraphs.length * 0.6)];
    if (midpoint && midpoint !== paragraphs[firstIndex]) midpoint.insertAdjacentElement("afterend", makeSlot("banner"));
  }
})();