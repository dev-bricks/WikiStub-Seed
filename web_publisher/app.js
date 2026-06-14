"use strict";

const LANG_KEY = "mw-lang";
let wiki = null;      // raw WikiStub-Seed object
let index = null;     // flat search-index array
let lang = localStorage.getItem(LANG_KEY) || "de";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const catTree    = document.getElementById("cat-tree");
const stubList   = document.getElementById("stub-list");
const detail     = document.getElementById("detail");
const searchInput = document.getElementById("search");
const langToggle  = document.getElementById("lang-toggle");
const loadingMsg  = document.getElementById("loading");

function localizedText(map, selectedLang, legacy = {}) {
  const source = map && typeof map === "object" ? map : {};
  const fallback = { ...legacy, ...source };
  for (const candidate of [selectedLang, "de", "en"]) {
    if (fallback[candidate]) return fallback[candidate];
  }
  return Object.values(fallback).find(Boolean) || "";
}

function definitionText(entry, selectedLang = lang) {
  return localizedText(entry.definitions, selectedLang, {
    de: entry.definition_de || "",
    en: entry.definition_en || "",
  });
}

function relevanceText(entry, selectedLang = lang) {
  const relevanceMap = entry.relevance_i18n || (typeof entry.relevance === "object" ? entry.relevance : null);
  return localizedText(relevanceMap, selectedLang, {
    de: typeof entry.relevance === "string" ? entry.relevance : "",
  });
}

// ── Boot ─────────────────────────────────────────────────────────────────────
async function boot() {
  updateLangUI();
  try {
    const [wikiRes, idxRes] = await Promise.all([
      fetch("./data/wikistub_seed.json"),
      fetch("./data/search-index.json"),
    ]);
    wiki  = (await wikiRes.json()).MetaWiki;
    index = await idxRes.json();
  } catch (e) {
    loadingMsg.textContent = "Daten konnten nicht geladen werden.";
    return;
  }
  loadingMsg.style.display = "none";
  buildTree();
  renderList(index);
  initSearch();
  routeHash();
}

// ── Category tree ─────────────────────────────────────────────────────────────
function buildTree() {
  catTree.innerHTML = "";
  const all = document.createElement("li");
  all.className = "cat-all active";
  all.textContent = lang === "de" ? "Alle" : "All";
  all.addEventListener("click", () => { renderList(index); setActive(all); clearHash(); });
  catTree.appendChild(all);

  for (const cat of Object.keys(wiki)) {
    const li = document.createElement("li");
    li.className = "cat-item";
    li.dataset.cat = cat;
    li.textContent = cat.replace(/^\d+_/, "").replace(/_/g, " ");
    li.addEventListener("click", () => {
      const filtered = index.filter((e) => e.cat === cat);
      renderList(filtered);
      setActive(li);
      clearHash();
    });

    const ul = document.createElement("ul");
    ul.className = "sub-list";
    for (const sub of Object.keys(wiki[cat])) {
      const subLi = document.createElement("li");
      subLi.dataset.cat = cat;
      subLi.dataset.sub = sub;
      subLi.textContent = sub.replace(/_/g, " ");
      subLi.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const filtered = index.filter((e) => e.cat === cat && e.sub === sub);
        renderList(filtered);
        setActive(subLi);
        clearHash();
      });
      ul.appendChild(subLi);
    }
    li.appendChild(ul);
    catTree.appendChild(li);
  }
}

function setActive(el) {
  catTree.querySelectorAll(".active").forEach((x) => x.classList.remove("active"));
  el.classList.add("active");
}

// ── Stub list ─────────────────────────────────────────────────────────────────
function renderList(entries) {
  stubList.innerHTML = "";
  detail.innerHTML   = "";
  if (!entries.length) {
    stubList.innerHTML = `<li class="empty">${lang === "de" ? "Keine Treffer." : "No results."}</li>`;
    return;
  }
  for (const entry of entries) {
    const li = document.createElement("li");
    li.textContent = entry.title;
    li.dataset.id  = entry.id;
    li.addEventListener("click", () => { showDetail(entry.id); setStubActive(li); });
    stubList.appendChild(li);
  }
}

function setStubActive(el) {
  stubList.querySelectorAll(".active").forEach((x) => x.classList.remove("active"));
  el.classList.add("active");
}

// ── Detail ────────────────────────────────────────────────────────────────────
function showDetail(id) {
  const meta = index[id];
  if (!meta) return;
  const entry = wiki[meta.cat]?.[meta.sub]?.find((e) => e.title === meta.title);
  if (!entry) return;
  window.location.hash = `#${encodeURIComponent(entry.title)}`;

  const def  = definitionText(entry, lang);
  const relevance = relevanceText(entry, lang);
  const defLabel = lang === "de" ? "Definition" : "Definition";
  const relLabel = lang === "de" ? "Relevanz" : "Relevance";
  const tagsLabel = lang === "de" ? "Tags" : "Tags";
  const catLabel = lang === "de" ? meta.cat.replace(/^\d+_/, "").replace(/_/g, " ") : meta.cat.replace(/^\d+_/, "").replace(/_/g, " ");

  detail.innerHTML = `
    <h2>${entry.title}</h2>
    <p class="breadcrumb">${catLabel} › ${meta.sub.replace(/_/g, " ")}</p>
    <h3>${defLabel}</h3>
    <p>${def}</p>
    <h3>${relLabel}</h3>
    <p>${relevance}</p>
    <p class="tags"><strong>${tagsLabel}:</strong> ${(entry.tags || []).map((t) => `<span class="tag">${t}</span>`).join(" ")}</p>
  `;
}

// ── Search ────────────────────────────────────────────────────────────────────
function initSearch() {
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    if (!q) { renderList(index); return; }
    const hits = index.filter((e) =>
      e.title.toLowerCase().includes(q) ||
      (e.tags || []).some((t) => t.toLowerCase().includes(q)) ||
      definitionText(e, lang).toLowerCase().includes(q) ||
      relevanceText(e, lang).toLowerCase().includes(q)
    );
    renderList(hits);
    clearHash();
  });
}

// ── Language toggle ───────────────────────────────────────────────────────────
function updateLangUI() {
  langToggle.textContent = lang === "de" ? "EN" : "DE";
  document.documentElement.lang = lang;
}

langToggle.addEventListener("click", () => {
  lang = lang === "de" ? "en" : "de";
  localStorage.setItem(LANG_KEY, lang);
  updateLangUI();
  if (wiki) { buildTree(); renderList(index); }
});

// ── Hash routing ──────────────────────────────────────────────────────────────
function routeHash() {
  const hash = decodeURIComponent(window.location.hash.slice(1));
  if (!hash || !index) return;
  const entry = index.find((e) => e.title === hash);
  if (!entry) return;
  showDetail(entry.id);
  const li = stubList.querySelector(`[data-id="${entry.id}"]`);
  if (li) { setStubActive(li); li.scrollIntoView({ block: "nearest" }); }
}

function clearHash() {
  history.replaceState(null, "", window.location.pathname + window.location.search);
}

window.addEventListener("hashchange", routeHash);

// ── Service Worker ────────────────────────────────────────────────────────────
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

boot();
