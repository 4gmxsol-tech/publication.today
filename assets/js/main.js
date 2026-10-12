(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const categories = {
    fitness: { label: "Fitness", glyph: "↗", description: "Training, strength and movement that fits your life." },
    health: { label: "Health", glyph: "✳", description: "Clear, practical perspectives on the foundations of wellbeing." },
    skincare: { label: "Skincare", glyph: "◌", description: "Understand routines, ingredients and the basics of caring for skin." },
    nutrition: { label: "Nutrition", glyph: "⌁", description: "Food knowledge and balanced ideas for everyday choices." },
    wellness: { label: "Wellness", glyph: "☼", description: "Small habits for a more grounded, intentional everyday." },
    beauty: { label: "Beauty", glyph: "✧", description: "Personal care, considered products and simple rituals." }
  };
  const state = { articles: [], filter: "all", query: "", visible: 9 };
  const safe = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const articleUrl = article => `articles/${encodeURIComponent(article.slug)}.html`;
  const card = article => {
    const category = categories[article.category] || categories.wellness;
    return `<article class="article-card"><a class="article-visual visual-${safe(article.category)}" href="${articleUrl(article)}" aria-label="Read ${safe(article.title)}"><span class="visual-glyph" aria-hidden="true">${category.glyph}</span></a><div class="article-meta"><span class="article-category">${category.label}</span><span>${safe(article.readTime || "5 min read")}</span></div><h3><a href="${articleUrl(article)}">${safe(article.title)}</a></h3><p>${safe(article.excerpt)}</p><a class="card-read" href="${articleUrl(article)}">Read story ↗</a></article>`;
  };
  const matching = () => state.articles.filter(article => {
    const categoryMatch = state.filter === "all" || article.category === state.filter;
    const text = [article.title, article.excerpt, article.category, ...(article.tags || [])].join(" ").toLowerCase();
    return categoryMatch && text.includes(state.query.toLowerCase());
  });
  const render = () => {
    const grid = $("#article-grid");
    if (!grid) return;
    const results = matching();
    const visible = results.slice(0, state.visible);
    grid.innerHTML = visible.length ? visible.map(card).join("") : '<div class="empty-state">No stories found. Try another topic or search.</div>';
    const more = $("#load-more");
    if (more) more.hidden = visible.length >= results.length;
    const count = $("#results-count");
    if (count) count.textContent = results.length ? `Showing ${visible.length} of ${results.length} stories` : "0 stories";
  };
  const init = async () => {
    const year = $("#year"); if (year) year.textContent = new Date().getFullYear();
    const date = $("#today-date"); if (date) date.textContent = new Intl.DateTimeFormat("en", { month: "long", day: "numeric", year: "numeric" }).format(new Date()).toUpperCase();
    const menu = $("#menu-toggle"), nav = $("#main-nav");
    if (menu && nav) menu.addEventListener("click", () => { const open = nav.classList.toggle("open"); menu.setAttribute("aria-expanded", String(open)); });
    const search = $("#article-search");
    if (search) {
      search.addEventListener("input", event => { state.query = event.target.value.trim(); state.visible = 9; render(); });
      document.addEventListener("keydown", event => { if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) { event.preventDefault(); search.focus(); } });
    }
    const filters = $("#filter-row");
    if (filters) filters.addEventListener("click", event => {
      const button = event.target.closest("[data-filter]"); if (!button) return;
      state.filter = button.dataset.filter; state.visible = 9;
      $$(".filter-chip", filters).forEach(chip => chip.classList.toggle("active", chip === button));
      render();
    });
    const more = $("#load-more");
    if (more) more.addEventListener("click", () => { state.visible += 9; render(); });
    try {
      const response = await fetch("data/articles.json");
      if (!response.ok) throw new Error("Unable to load the article index");
      state.articles = await response.json();
      render();
      initArticlePage();
      initSectionPage();
    } catch (error) {
      const grid = $("#article-grid");
      if (grid) grid.innerHTML = '<div class="empty-state">Stories could not be loaded. Please refresh the page.</div>';
      console.error(error);
    }
  };
  const initArticlePage = () => {
    const mount = $("#article-content"); if (!mount) return;
    const slug = new URLSearchParams(location.search).get("slug");
    const article = state.articles.find(item => item.slug === slug);
    if (!article) { mount.innerHTML = '<div class="article-page"><p class="eyebrow">STORY NOT FOUND</p><h1>We couldn’t find that story.</h1><p>It may have moved, or the link may be incorrect.</p><a class="button button-dark" href="index.html">Return home ↗</a></div>'; return; }
    const category = categories[article.category] || categories.wellness;
    document.title = `${article.title} — Publication Today`;
    const canonical = $("link[rel=canonical]"); if (canonical) canonical.href = `https://publication.today/article.html?slug=${encodeURIComponent(article.slug)}`;
    const description = $('meta[name="description"]'); if (description) description.content = article.excerpt;
    mount.innerHTML = `<div class="container"><div class="article-page"><div class="breadcrumb"><a href="index.html">Home</a> / <a href="section.html?category=${article.category}">${category.label}</a> / Story</div><p class="eyebrow">${category.label.toUpperCase()} · ${safe(article.readTime || "5 MIN READ")}</p><h1>${safe(article.title)}</h1><p class="article-lead">${safe(article.excerpt)}</p><div class="article-meta"><span>Publication Today Editorial</span><span>Updated ${safe(article.date || "October 2026")}</span></div><div class="article-visual visual-${article.category}" style="height:260px;margin:28px 0"><span class="visual-glyph">${category.glyph}</span></div><div class="article-body">${(article.body || []).map((block, index) => `<${index === 0 ? "h2" : "h2"}>${safe(block.heading)}</h2><p>${safe(block.text)}</p>`).join("")}<h2>A thoughtful next step</h2><p>Use this guide as a starting point, not a rigid rulebook. Consider your own circumstances, look for reliable sources, and seek qualified professional advice when a decision affects your health or safety.</p></div><div class="article-disclaimer">Editorial note: Publication Today provides general educational information, not individual medical advice. Health-related decisions should be discussed with an appropriately qualified professional.</div><p style="margin-top:30px"><a class="text-link" href="section.html?category=${article.category}">Explore more in ${category.label} ↗</a></p></div></div>`;
  };
  const initSectionPage = () => {
    const mount = $("#section-content"); if (!mount) return;
    const key = new URLSearchParams(location.search).get("category") || "fitness";
    const category = categories[key];
    if (!category) { mount.innerHTML = '<div class="container page-hero"><h1>Section not found</h1><a href="index.html">Return home</a></div>'; return; }
    document.title = `${category.label} — Publication Today`;
    const canonical = $('link[rel=canonical]'); if (canonical) canonical.href = `https://publication.today/section.html?category=${encodeURIComponent(key)}`;
    const description = $('meta[name="description"]'); if (description) description.content = category.description;
    const ogTitle = $('meta[property="og:title"]'); if (ogTitle) ogTitle.content = `${category.label} — Publication Today`;
    const ogDescription = $('meta[property="og:description"]'); if (ogDescription) ogDescription.content = category.description;
    const items = state.articles.filter(article => article.category === key);
    mount.innerHTML = `<div class="container"><section class="page-hero"><div class="breadcrumb"><a href="index.html">Home</a> / ${category.label}</div><p class="eyebrow">THE ${category.label.toUpperCase()} EDIT</p><h1>${category.label} <i>for real life.</i></h1><p>${category.description} Explore our guides and ideas, made to help you ask better questions and take informed next steps.</p></section><section class="section-block" style="padding-top:42px"><div class="section-heading"><div><p class="eyebrow">EXPLORE THE SECTION</p><h2>Stories to <i>start with.</i></h2></div><p class="section-intro">${items.length} stories in this section</p></div><div class="article-grid">${items.map(card).join("")}</div><p style="margin-top:40px"><a class="button button-outline" href="index.html">← Back to all topics</a></p></section></div>`;
  };
  init();
})();