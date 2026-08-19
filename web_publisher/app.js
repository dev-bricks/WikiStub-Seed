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
let currentEntryId = null;

// ---- Edit mode state --------------------------------------------------
// permissions/editModeAvailable are the ONLY source of truth for whether an
// edit control is shown; nothing here assumes a capability the last
// GET /api/permissions response didn't confirm. On a static deployment
// (no edit_server.py running) that fetch fails and every edit affordance
// stays hidden -- see loadPermissions().
let editModeAvailable = false;
let permissions = { password_set: false, authenticated: false, create: false, edit: false, delete: false };

const catTree = document.getElementById("cat-tree");
const stubList = document.getElementById("stub-list");
const detail = document.getElementById("detail");
const searchInput = document.getElementById("search");
const langSelect = document.getElementById("lang-select");
const loadingMsg = document.getElementById("loading");
const readonlyBanner = document.getElementById("readonly-banner");
const authControls = document.getElementById("auth-controls");
const authStatus = document.getElementById("auth-status");
const authOpenBtn = document.getElementById("auth-open-btn");

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

async function loadData() {
  // cache: "no-store" bypasses the browser's own HTTP cache (not the
  // service worker, which already does networkFirst() for /data/ -- see
  // sw.js) so a reload right after an edit-mode save never shows a stale
  // definition.
  const [wikiRes, indexRes] = await Promise.all([
    fetch("./data/wikistub_seed.json", { cache: "no-store" }),
    fetch("./data/search-index.json", { cache: "no-store" }),
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
}

async function loadPermissions() {
  try {
    const res = await fetch("./api/permissions", { cache: "no-store" });
    if (!res.ok) throw new Error("no edit server");
    permissions = await res.json();
    editModeAvailable = true;
  } catch (error) {
    editModeAvailable = false;
    permissions = { password_set: false, authenticated: false, create: false, edit: false, delete: false };
  }
  updateEditModeUI();
}

function updateEditModeUI() {
  readonlyBanner.classList.toggle("visible", !editModeAvailable);
  authOpenBtn.hidden = !editModeAvailable;
  document.getElementById("cat-tree-actions").hidden = !(editModeAvailable && permissions.create);
  document.getElementById("stub-panel-actions").hidden = !(editModeAvailable && permissions.create);
  if (!editModeAvailable) {
    authStatus.textContent = "";
  } else if (permissions.authenticated) {
    authStatus.textContent = "Angemeldet";
  } else if (permissions.password_set) {
    authStatus.textContent = "Nicht angemeldet";
  } else {
    authStatus.textContent = "Kein Passwort gesetzt";
  }
  if (wiki) {
    buildTree();
    if (currentEntryId) showDetail(currentEntryId, false);
  }
}

async function refreshAfterMutation() {
  await loadData();
  await loadPermissions();
  buildTree();
  renderList(searchResults());
  if (currentEntryId) showDetail(currentEntryId, false);
}

async function boot() {
  updateLangUI();
  try {
    await loadData();
  } catch (error) {
    loadingMsg.textContent = "Daten konnten nicht geladen werden.";
    return;
  }
  loadingMsg.style.display = "none";
  buildTree();
  renderList(index);
  initSearch();
  routeHash();
  await loadPermissions();
  initEditUi();
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

    const row = document.createElement("div");
    row.className = "tree-row";
    const label = document.createElement("span");
    label.textContent = cat.replace(/^\d+_/, "").replace(/_/g, " ");
    row.appendChild(label);
    if (editModeAvailable && permissions.create) {
      const addBtn = document.createElement("button");
      addBtn.type = "button";
      addBtn.className = "tree-add";
      addBtn.title = "Unterkategorie anlegen";
      addBtn.textContent = "+";
      addBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        openCategoryEditor({ category: cat });
      });
      row.appendChild(addBtn);
    }
    if (editModeAvailable && permissions.delete) {
      const delBtn = document.createElement("button");
      delBtn.type = "button";
      delBtn.className = "tree-del";
      delBtn.title = "Kategorie löschen";
      delBtn.textContent = "🗑";
      delBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        deleteCategory(cat);
      });
      row.appendChild(delBtn);
    }
    li.appendChild(row);
    bindActivation(row, () => {
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
      const subRow = document.createElement("div");
      subRow.className = "tree-row";
      const subLabel = document.createElement("span");
      subLabel.textContent = sub.replace(/_/g, " ");
      subRow.appendChild(subLabel);
      if (editModeAvailable && permissions.delete) {
        const subDelBtn = document.createElement("button");
        subDelBtn.type = "button";
        subDelBtn.className = "tree-del";
        subDelBtn.title = "Unterkategorie löschen";
        subDelBtn.textContent = "🗑";
        subDelBtn.addEventListener("click", (event) => {
          event.stopPropagation();
          deleteSubcategory(cat, sub);
        });
        subRow.appendChild(subDelBtn);
      }
      subLi.appendChild(subRow);
      bindActivation(subRow, (event) => {
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
  currentEntryId = stableId;
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
  const children = [title, breadcrumb];
  if (editModeAvailable && (permissions.edit || permissions.delete)) {
    const actionBar = document.createElement("div");
    actionBar.className = "action-bar";
    if (permissions.edit) {
      const editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.textContent = "Bearbeiten";
      editBtn.addEventListener("click", () => openEntryEditor({ mode: "edit", meta, entry }));
      actionBar.appendChild(editBtn);
    }
    if (permissions.delete) {
      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "danger";
      deleteBtn.textContent = "Löschen";
      deleteBtn.addEventListener("click", () => deleteEntry(meta, entry));
      actionBar.appendChild(deleteBtn);
    }
    children.push(actionBar);
  }
  children.push(definitionHeading, definition, relevanceHeading, relevance, tags);
  detail.replaceChildren(...children);
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

// ---- Edit mode: API calls + overlay wiring ----------------------------
// Every request here goes through apiCall(), which always sends
// Content-Type: application/json (edit_server.py rejects anything else,
// see edit_server.py's module docstring) and always includes the session
// cookie automatically via the browser (credentials default to
// "same-origin", which is exactly what a same-origin edit_server needs).

async function apiCall(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  let payload = null;
  try {
    payload = await res.json();
  } catch (error) {
    payload = null;
  }
  if (!res.ok) {
    const message = (payload && payload.error) || `Fehler (${res.status})`;
    throw new Error(message);
  }
  return payload;
}

function tagsFromInput(value) {
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

// ---- Entry editor -------------------------------------------------

const entryEditorOverlay = document.getElementById("entry-editor-overlay");
const entryEditorTitle = document.getElementById("entry-editor-title");
const entryCategoryInput = document.getElementById("entry-category");
const entrySubcategoryInput = document.getElementById("entry-subcategory");
const entryTitleInput = document.getElementById("entry-title");
const entryDefDeInput = document.getElementById("entry-def-de");
const entryDefEnInput = document.getElementById("entry-def-en");
const entryRelevanceInput = document.getElementById("entry-relevance");
const entryTagsInput = document.getElementById("entry-tags");
const entryEditorError = document.getElementById("entry-editor-error");
const entryEditorDeleteBtn = document.getElementById("entry-editor-delete-btn");

let entryEditorState = null; // { mode: "create"|"edit", meta?, entry? }

function populateEntryDatalists() {
  const catList = document.getElementById("entry-category-list");
  catList.replaceChildren(
    ...Object.keys(wiki || {}).map((cat) => {
      const opt = document.createElement("option");
      opt.value = cat;
      return opt;
    })
  );
}

function populateSubcategoryDatalist(category) {
  const subList = document.getElementById("entry-subcategory-list");
  const subs = (wiki && wiki[category]) ? Object.keys(wiki[category]) : [];
  subList.replaceChildren(
    ...subs.map((sub) => {
      const opt = document.createElement("option");
      opt.value = sub;
      return opt;
    })
  );
}

function openEntryEditor({ mode, meta, entry }) {
  entryEditorState = { mode, meta, entry };
  entryEditorError.textContent = "";
  populateEntryDatalists();
  if (mode === "edit") {
    entryEditorTitle.textContent = "Artikel bearbeiten";
    entryCategoryInput.value = meta.cat;
    entryCategoryInput.disabled = true;
    entrySubcategoryInput.value = meta.sub;
    entrySubcategoryInput.disabled = true;
    entryTitleInput.value = entry.title;
    entryDefDeInput.value = definitionText(entry, "de");
    entryDefEnInput.value = definitionText(entry, "en");
    entryRelevanceInput.value = relevanceText(entry, "de");
    entryTagsInput.value = (Array.isArray(entry.tags) ? entry.tags : []).join(", ");
    entryEditorDeleteBtn.hidden = !permissions.delete;
  } else {
    entryEditorTitle.textContent = "Neuer Artikel";
    entryCategoryInput.disabled = false;
    entrySubcategoryInput.disabled = false;
    entryCategoryInput.value = "";
    entrySubcategoryInput.value = "";
    entryTitleInput.value = "";
    entryDefDeInput.value = "";
    entryDefEnInput.value = "";
    entryRelevanceInput.value = "";
    entryTagsInput.value = "";
    entryEditorDeleteBtn.hidden = true;
  }
  populateSubcategoryDatalist(entryCategoryInput.value);
  entryEditorOverlay.classList.add("visible");
}

function closeEntryEditor() {
  entryEditorOverlay.classList.remove("visible");
  entryEditorState = null;
}

entryCategoryInput.addEventListener("input", () => populateSubcategoryDatalist(entryCategoryInput.value));

document.getElementById("entry-editor-cancel-btn").addEventListener("click", closeEntryEditor);

document.getElementById("entry-editor-save-btn").addEventListener("click", async () => {
  if (!entryEditorState) return;
  entryEditorError.textContent = "";
  const fields = {
    title: entryTitleInput.value.trim(),
    definition_de: entryDefDeInput.value,
    definition_en: entryDefEnInput.value,
    relevance: entryRelevanceInput.value,
    tags: tagsFromInput(entryTagsInput.value),
  };
  try {
    if (entryEditorState.mode === "create") {
      await apiCall("POST", "./api/entries", {
        category: entryCategoryInput.value.trim(),
        subcategory: entrySubcategoryInput.value.trim(),
        entry: fields,
      });
    } else {
      await apiCall("PUT", "./api/entries", {
        category: entryEditorState.meta.cat,
        subcategory: entryEditorState.meta.sub,
        original_title: entryEditorState.entry.title,
        entry: fields,
      });
    }
    closeEntryEditor();
    await refreshAfterMutation();
  } catch (error) {
    entryEditorError.textContent = error.message;
  }
});

entryEditorDeleteBtn.addEventListener("click", async () => {
  if (!entryEditorState || entryEditorState.mode !== "edit") return;
  if (!window.confirm(`"${entryEditorState.entry.title}" wirklich löschen?`)) return;
  try {
    await apiCall("DELETE", "./api/entries", {
      category: entryEditorState.meta.cat,
      subcategory: entryEditorState.meta.sub,
      title: entryEditorState.entry.title,
    });
    closeEntryEditor();
    currentEntryId = null;
    await refreshAfterMutation();
    detail.replaceChildren();
  } catch (error) {
    entryEditorError.textContent = error.message;
  }
});

async function deleteEntry(meta, entry) {
  if (!window.confirm(`"${entry.title}" wirklich löschen?`)) return;
  try {
    await apiCall("DELETE", "./api/entries", { category: meta.cat, subcategory: meta.sub, title: entry.title });
    currentEntryId = null;
    await refreshAfterMutation();
    detail.replaceChildren();
  } catch (error) {
    window.alert(error.message);
  }
}

// ---- Category / subcategory editor ---------------------------------

const categoryEditorOverlay = document.getElementById("category-editor-overlay");
const categoryEditorTitle = document.getElementById("category-editor-title");
const categoryEditorNameInput = document.getElementById("category-editor-name");
const categoryEditorError = document.getElementById("category-editor-error");
let categoryEditorState = null; // { category?: existing parent, or null for a new top-level category }

function openCategoryEditor({ category }) {
  categoryEditorState = { parentCategory: category || null };
  categoryEditorTitle.textContent = category ? `Neue Unterkategorie in "${category.replace(/^\d+_/, "").replace(/_/g, " ")}"` : "Neue Kategorie";
  categoryEditorNameInput.value = "";
  categoryEditorError.textContent = "";
  categoryEditorOverlay.classList.add("visible");
}

document.getElementById("category-editor-cancel-btn").addEventListener("click", () => {
  categoryEditorOverlay.classList.remove("visible");
});

document.getElementById("category-editor-save-btn").addEventListener("click", async () => {
  const name = categoryEditorNameInput.value.trim();
  if (!name) {
    categoryEditorError.textContent = "Name darf nicht leer sein.";
    return;
  }
  try {
    if (categoryEditorState.parentCategory) {
      await apiCall("POST", "./api/categories", { category: categoryEditorState.parentCategory, subcategory: name });
    } else {
      await apiCall("POST", "./api/categories", { category: name });
    }
    categoryEditorOverlay.classList.remove("visible");
    await refreshAfterMutation();
  } catch (error) {
    categoryEditorError.textContent = error.message;
  }
});

async function deleteCategory(category) {
  const label = category.replace(/^\d+_/, "").replace(/_/g, " ");
  if (!window.confirm(`Kategorie "${label}" inkl. aller Unterkategorien und Artikel löschen (in den Papierkorb)?`)) return;
  try {
    await apiCall("DELETE", "./api/categories", { category });
    currentEntryId = null;
    await refreshAfterMutation();
    detail.replaceChildren();
  } catch (error) {
    window.alert(error.message);
  }
}

async function deleteSubcategory(category, subcategory) {
  const label = subcategory.replace(/_/g, " ");
  if (!window.confirm(`Unterkategorie "${label}" inkl. aller Artikel löschen (in den Papierkorb)?`)) return;
  try {
    await apiCall("DELETE", "./api/categories", { category, subcategory });
    currentEntryId = null;
    await refreshAfterMutation();
    detail.replaceChildren();
  } catch (error) {
    window.alert(error.message);
  }
}

// ---- Auth overlay ---------------------------------------------------

const authOverlay = document.getElementById("auth-overlay");
const authLoggedOutView = document.getElementById("auth-logged-out-view");
const authLoggedInView = document.getElementById("auth-logged-in-view");
const authError = document.getElementById("auth-error");
const authError2 = document.getElementById("auth-error-2");

function openAuthOverlay() {
  authError.textContent = "";
  authError2.textContent = "";
  document.getElementById("login-password").value = "";
  document.getElementById("change-password").value = "";
  if (permissions.authenticated) {
    authLoggedOutView.hidden = true;
    authLoggedInView.hidden = false;
    document.getElementById("perm-create").checked = !!permissions.create;
    document.getElementById("perm-edit").checked = !!permissions.edit;
    document.getElementById("perm-delete").checked = !!permissions.delete;
  } else {
    authLoggedOutView.hidden = false;
    authLoggedInView.hidden = true;
  }
  authOverlay.classList.add("visible");
}

function closeAuthOverlay() {
  authOverlay.classList.remove("visible");
}

function initEditUi() {
  authOpenBtn.addEventListener("click", openAuthOverlay);
  document.getElementById("auth-cancel-btn").addEventListener("click", closeAuthOverlay);
  document.getElementById("auth-close-btn").addEventListener("click", closeAuthOverlay);

  document.getElementById("new-entry-btn").addEventListener("click", () => openEntryEditor({ mode: "create" }));
  document.getElementById("new-category-btn").addEventListener("click", () => openCategoryEditor({ category: null }));

  document.getElementById("login-btn").addEventListener("click", async () => {
    authError.textContent = "";
    try {
      await apiCall("POST", "./api/auth/login", { password: document.getElementById("login-password").value });
      await loadPermissions();
      openAuthOverlay();
    } catch (error) {
      authError.textContent = error.message;
    }
  });

  document.getElementById("set-password-btn").addEventListener("click", async () => {
    authError.textContent = "";
    const value = document.getElementById("login-password").value;
    if (!value) {
      authError.textContent = "Passwort darf nicht leer sein.";
      return;
    }
    try {
      await apiCall("POST", "./api/auth/set-password", { new_password: value });
      await apiCall("POST", "./api/auth/login", { password: value });
      await loadPermissions();
      openAuthOverlay();
    } catch (error) {
      authError.textContent = error.message;
    }
  });

  document.getElementById("logout-btn").addEventListener("click", async () => {
    await apiCall("POST", "./api/auth/logout", {});
    await loadPermissions();
    closeAuthOverlay();
  });

  document.getElementById("change-password-btn").addEventListener("click", async () => {
    authError2.textContent = "";
    const value = document.getElementById("change-password").value;
    if (!value) {
      authError2.textContent = "Neues Passwort darf nicht leer sein.";
      return;
    }
    try {
      await apiCall("POST", "./api/auth/set-password", { new_password: value });
      document.getElementById("change-password").value = "";
    } catch (error) {
      authError2.textContent = error.message;
    }
  });

  document.getElementById("remove-password-btn").addEventListener("click", async () => {
    if (!window.confirm("Passwort wirklich entfernen? Danach dürfen wieder alle uneingeschränkt bearbeiten.")) return;
    try {
      await apiCall("POST", "./api/auth/remove-password", {});
      await loadPermissions();
      closeAuthOverlay();
    } catch (error) {
      authError2.textContent = error.message;
    }
  });

  document.getElementById("save-permissions-btn").addEventListener("click", async () => {
    authError2.textContent = "";
    try {
      await apiCall("POST", "./api/auth/permissions", {
        create: document.getElementById("perm-create").checked,
        edit: document.getElementById("perm-edit").checked,
        delete: document.getElementById("perm-delete").checked,
      });
      await loadPermissions();
    } catch (error) {
      authError2.textContent = error.message;
    }
  });
}

boot();
