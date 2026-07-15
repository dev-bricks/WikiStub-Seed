"use strict";

const LANG_KEY = "mw-lang";
const LANGUAGES = ["de", "en", "es", "zh", "ja", "ru"];

function readStoredLanguage() {
  try {
    const stored = localStorage.getItem(LANG_KEY);
    return LANGUAGES.includes(stored) ? stored : "de";
  } catch (error) {
    return "de";
  }
}

function storeLanguage(value) {
  try {
    localStorage.setItem(LANG_KEY, value);
  } catch (error) {
    // Storage policies and private browsing must not break the reader.
  }
}

let wiki = null;
let index = null;
let lang = readStoredLanguage();

const catTree = document.getElementById("cat-tree");
const stubList = document.getElementById("stub-list");
const detail = document.getElementById("detail");
const searchInput = document.getElementById("search");
const langSelect = document.getElementById("lang-select");
const loadingMsg = document.getElementById("loading");

function bindActivation(element, handler) {
  element.tabIndex = 0;
  element.setAttribute("role", "button");
  element.addEventListener("click", handler);
  element.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handler(event);
    }
  });
}

function localizedText(map, selectedLang, legacy = {}) {
  const source = map && typeof map === "object" ? map : {};
  const fallback = { ...legacy, ...source };
  for (const candidate of [selectedLang, "de", "en"]) {
    if (typeof fallback[candidate] === "string" && fallback[candidate]) {
      return fallback[candidate];
    }
  }
  return Object.values(fallback).find((value) => typeof value === "string" && value) || "";
}

function definitionText(entry, selectedLang = lang) {
  return localizedText(entry.definitions, selectedLang, {
    de: typeof entry.definition_de === "string" ? entry.definition_de : "",
    en: typeof entry.definition_en === "string" ? entry.definition_en : "",
  });
}

function relevanceText(entry, selectedLang = lang) {
  const relevanceMap = entry.relevance_i18n ||
    (typeof entry.relevance === "object" ? entry.relevance : null);
  return localizedText(relevanceMap, selectedLang, {
    de: typeof entry.relevance === "string" ? entry.relevance : "",
  });
}

async function boot() {
  updateLangUI();
  try {
    const [wikiRes, indexRes] = await Promise.all([
      fetch("./data/wikistub_seed.json"),
      fetch("./data/search-index.json"),
    ]);
    if (!wikiRes.ok || !indexRes.ok) throw new Error("HTTP error");

    const wikiPayload = await wikiRes.json();
    const indexPayload = await indexRes.json();
    if (
      !wikiPayload ||
      !wikiPayload.MetaWiki ||
      typeof wikiPayload.MetaWiki !== "object" ||
      Array.isArray(wikiPayload.MetaWiki)
    ) {
      throw new Error("Invalid WikiStub payload");
    }
    if (!Array.isArray(indexPayload) || indexPayload.some((entry) =>
      !entry || typeof entry.id !== "string" || typeof entry.title !== "string"
    )) {
      throw new Error("Invalid search index");
    }
    wiki = wikiPayload.MetaWiki;
    index = indexPayload;
  } catch (error) {
    loadingMsg.textContent = "Daten konnten nicht geladen werden.";
    return;
  }
  loadingMsg.style.display = "none";
  buildTree();
  renderList(index);
  initSearch();
  routeHash();
}

function buildTree() {
  catTree.replaceChildren();
  const all = document.createElement("li");
  all.className = "cat-all active";
  all.textContent = lang === "de" ? "Alle" : "All";
  bindActivation(all, () => {
    renderList(index);
    setActive(all);
    clearHash();
  });
  catTree.appendChild(all);

  for (const cat of Object.keys(wiki)) {
    const li = document.createElement("li");
    li.className = "cat-item";
    li.dataset.cat = cat;
    li.textContent = cat.replace(/^\d+_/, "").replace(/_/g, " ");
    bindActivation(li, () => {
      renderList(index.filter((entry) => entry.cat === cat));
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
      bindActivation(subLi, (event) => {
        event.stopPropagation();
        renderList(index.filter((entry) => entry.cat === cat && entry.sub === sub));
        setActive(subLi);
        clearHash();
      });
      ul.appendChild(subLi);
    }
    li.appendChild(ul);
    catTree.appendChild(li);
  }
}

function setActive(element) {
  catTree.querySelectorAll(".active").forEach((item) => {
    item.classList.remove("active");
    item.removeAttribute("aria-current");
  });
  element.classList.add("active");
  element.setAttribute("aria-current", "true");
}

function renderList(entries) {
  stubList.replaceChildren();
  detail.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = lang === "de" ? "Keine Treffer." : "No results.";
    stubList.appendChild(empty);
    return;
  }
  for (const entry of entries) {
    const li = document.createElement("li");
    li.textContent = entry.title;
    li.dataset.id = entry.id;
    bindActivation(li, () => {
      showDetail(entry.id);
      setStubActive(li);
    });
    stubList.appendChild(li);
  }
}

function setStubActive(element) {
  stubList.querySelectorAll(".active").forEach((item) => {
    item.classList.remove("active");
    item.removeAttribute("aria-current");
  });
  element.classList.add("active");
  element.setAttribute("aria-current", "true");
}

function showDetail(id, updateHash = true) {
  const stableId = String(id);
  const meta = index.find((candidate) => candidate.id === stableId);
  if (!meta) return;
  const entries = wiki[meta.cat]?.[meta.sub];
  const entry = Array.isArray(entries)
    ? entries.find((candidate) => candidate.title === meta.title)
    : null;
  if (!entry) return;
  if (updateHash) {
    const hash = new URLSearchParams({ stub: meta.id, title: entry.title });
    window.location.hash = hash.toString();
  }

  const title = document.createElement("h2");
  title.textContent = entry.title;
  const breadcrumb = document.createElement("p");
  breadcrumb.className = "breadcrumb";
  breadcrumb.textContent = `${meta.cat.replace(/^\d+_/, "").replace(/_/g, " ")} › ${meta.sub.replace(/_/g, " ")}`;
  const definitionHeading = document.createElement("h3");
  definitionHeading.textContent = "Definition";
  const definition = document.createElement("p");
  definition.textContent = definitionText(entry, lang);
  const relevanceHeading = document.createElement("h3");
  relevanceHeading.textContent = lang === "de" ? "Relevanz" : "Relevance";
  const relevance = document.createElement("p");
  relevance.textContent = relevanceText(entry, lang);
  const tags = document.createElement("p");
  tags.className = "tags";
  const tagsHeading = document.createElement("strong");
  tagsHeading.textContent = "Tags: ";
  tags.appendChild(tagsHeading);
  for (const tag of Array.isArray(entry.tags) ? entry.tags : []) {
    if (typeof tag !== "string") continue;
    const badge = document.createElement("span");
    badge.className = "tag";
    badge.textContent = tag;
    tags.appendChild(badge);
    tags.append(" ");
  }
  detail.replaceChildren(
    title,
    breadcrumb,
    definitionHeading,
    definition,
    relevanceHeading,
    relevance,
    tags,
  );
}

function searchResults() {
  const query = searchInput.value.trim().toLocaleLowerCase(lang);
  if (!query) return index;
  return index.filter((entry) =>
    entry.title.toLocaleLowerCase(lang).includes(query) ||
    (Array.isArray(entry.tags) ? entry.tags : []).some((tag) =>
      typeof tag === "string" && tag.toLocaleLowerCase(lang).includes(query)
    ) ||
    definitionText(entry, lang).toLocaleLowerCase(lang).includes(query) ||
    relevanceText(entry, lang).toLocaleLowerCase(lang).includes(query)
  );
}

function initSearch() {
  searchInput.addEventListener("input", () => {
    renderList(searchResults());
    clearHash();
  });
}

function updateLangUI() {
  langSelect.value = lang;
  searchInput.placeholder = lang === "de" ? "Suche…" : "Search…";
  document.documentElement.lang = lang;
}

langSelect.addEventListener("change", () => {
  if (!LANGUAGES.includes(langSelect.value)) return;
  const selectedId = new URLSearchParams(window.location.hash.slice(1)).get("stub");
  lang = langSelect.value;
  storeLanguage(lang);
  updateLangUI();
  if (wiki) {
    buildTree();
    renderList(searchResults());
    if (selectedId) showDetail(selectedId, false);
  }
});

function routeHash() {
  const rawHash = window.location.hash.slice(1);
  if (!rawHash || !index) return;

  let entry = null;
  if (rawHash.startsWith("stub=")) {
    const params = new URLSearchParams(rawHash);
    const id = params.get("stub");
    if (/^[a-f0-9]{20}$/.test(id || "")) {
      entry = index.find((candidate) => candidate.id === id) || null;
    }
    if (!entry && params.get("title")) {
      entry = index.find((candidate) => candidate.title === params.get("title")) || null;
    }
  } else {
    try {
      const legacyTitle = decodeURIComponent(rawHash);
      entry = index.find((candidate) => candidate.title === legacyTitle) || null;
    } catch (error) {
      return;
    }
  }
  if (!entry) return;
  showDetail(entry.id, false);
  const listItem = stubList.querySelector(`[data-id="${entry.id}"]`);
  if (listItem) {
    setStubActive(listItem);
    listItem.scrollIntoView({ block: "nearest" });
  }
}

function clearHash() {
  history.replaceState(null, "", window.location.pathname + window.location.search);
}

window.addEventListener("hashchange", routeHash);

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

boot();
