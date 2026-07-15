/**
 * Statische Tests für den WikiStub-Seed PWA web_publisher.
 * Laufen ohne Browser/Emulator via: node --test web_publisher/tests/publisher.test.mjs
 */
import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dir = path.dirname(fileURLToPath(import.meta.url));
const PUB   = path.resolve(__dir, "..");
const ROOT  = path.resolve(PUB, "..");

// ── Hilfsfunktionen ──────────────────────────────────────────────────────────
function readJson(rel) {
  return JSON.parse(readFileSync(path.join(PUB, rel), "utf-8"));
}
function fileExists(rel) {
  return existsSync(path.join(PUB, rel));
}
function readText(rel) {
  return readFileSync(path.join(PUB, rel), "utf-8");
}

// ── 1: wikistub_seed.json Schema ───────────────────────────────────────────────────
describe("data/wikistub_seed.json", () => {
  it("existiert in data/", () => {
    assert.ok(fileExists("data/wikistub_seed.json"), "data/wikistub_seed.json fehlt — _build.py ausführen");
  });

  it("hat MetaWiki-Root mit ≥1 Kategorien", () => {
    const data = readJson("data/wikistub_seed.json");
    assert.ok(data.MetaWiki, "MetaWiki-Key fehlt");
    assert.ok(Object.keys(data.MetaWiki).length >= 1);
  });

  it("jeder Stub hat title, definition_de, definition_en", () => {
    const wiki = readJson("data/wikistub_seed.json").MetaWiki;
    let checked = 0;
    for (const subs of Object.values(wiki)) {
      for (const entries of Object.values(subs)) {
        for (const e of entries) {
          assert.ok(e.title,         `title fehlt in Eintrag: ${JSON.stringify(e).slice(0, 60)}`);
          assert.ok(e.definition_de, `definition_de fehlt bei "${e.title}"`);
          assert.ok(e.definition_en, `definition_en fehlt bei "${e.title}"`);
          checked++;
        }
      }
    }
    assert.ok(checked >= 10, `Nur ${checked} Stubs geprüft — Daten zu dünn`);
  });

  it("enthält ≥500 Stubs (Vollexport)", () => {
    const wiki = readJson("data/wikistub_seed.json").MetaWiki;
    let total = 0;
    for (const subs of Object.values(wiki)) {
      for (const entries of Object.values(subs)) total += entries.length;
    }
    assert.ok(total >= 500, `Nur ${total} Stubs, erwartet ≥500`);
  });
});

// ── 2: search-index.json ──────────────────────────────────────────────────────
describe("data/search-index.json", () => {
  it("existiert", () => {
    assert.ok(fileExists("data/search-index.json"));
  });

  it("ist Array mit id, cat, sub, title", () => {
    const idx = readJson("data/search-index.json");
    assert.ok(Array.isArray(idx));
    assert.ok(idx.length >= 1);
    const first = idx[0];
    assert.ok(typeof first.id === "number");
    assert.ok(typeof first.cat === "string");
    assert.ok(typeof first.sub === "string");
    assert.ok(typeof first.title === "string");
  });
});

// ── 3: manifest.webmanifest Pflichtfelder ────────────────────────────────────
describe("manifest.webmanifest", () => {
  let m;
  it("existiert und ist valides JSON", () => {
    m = readJson("manifest.webmanifest");
  });
  it("hat name und short_name", () => {
    m = m || readJson("manifest.webmanifest");
    assert.ok(m.name,       "name fehlt");
    assert.ok(m.short_name, "short_name fehlt");
    assert.ok(m.short_name.length <= 16, `short_name zu lang: "${m.short_name}" (${m.short_name.length} Zeichen)`);
  });
  it("hat start_url, scope, id", () => {
    m = m || readJson("manifest.webmanifest");
    assert.ok(m.start_url, "start_url fehlt");
    assert.ok(m.scope,     "scope fehlt");
    assert.ok(m.id,        "id fehlt");
  });
  it("display ist standalone oder minimal-ui", () => {
    m = m || readJson("manifest.webmanifest");
    const allowed = ["standalone", "minimal-ui", "fullscreen"];
    assert.ok(allowed.includes(m.display), `display "${m.display}" ungültig für PWA-Installierbarkeit`);
  });
  it("hat theme_color und background_color", () => {
    m = m || readJson("manifest.webmanifest");
    assert.ok(m.theme_color,      "theme_color fehlt");
    assert.ok(m.background_color, "background_color fehlt");
  });
  it("hat ≥2 Icons (any + maskable)", () => {
    m = m || readJson("manifest.webmanifest");
    const purposes = (m.icons || []).map((i) => i.purpose || "any");
    assert.ok(purposes.some((p) => p.includes("any")),      "Kein Icon mit purpose=any");
    assert.ok(purposes.some((p) => p.includes("maskable")), "Kein Icon mit purpose=maskable");
  });
  it("Icons ≥192px und ≥512px vorhanden", () => {
    m = m || readJson("manifest.webmanifest");
    const sizes = (m.icons || []).map((i) => i.sizes || "");
    assert.ok(sizes.some((s) => s.includes("192")), "Kein 192px Icon im Manifest");
    assert.ok(sizes.some((s) => s.includes("512")), "Kein 512px Icon im Manifest");
  });
});

// ── 4: Icon-Dateien physisch vorhanden ───────────────────────────────────────
describe("icons/", () => {
  for (const name of ["Icon-192.png", "Icon-512.png", "Icon-maskable-192.png", "Icon-maskable-512.png"]) {
    it(`${name} existiert`, () => {
      assert.ok(fileExists(`icons/${name}`), `icons/${name} fehlt — _gen_icons.py ausführen`);
    });
  }
});

// ── 5: index.html referenziert manifest + app.js ─────────────────────────────
describe("index.html", () => {
  let html;
  it("existiert", () => {
    html = readText("index.html");
  });
  it("verlinkt manifest.webmanifest", () => {
    html = html || readText("index.html");
    assert.ok(html.includes("manifest.webmanifest"), "manifest.webmanifest-Link fehlt in index.html");
  });
  it("lädt app.js", () => {
    html = html || readText("index.html");
    assert.ok(html.includes("app.js"), "app.js-Script-Tag fehlt in index.html");
  });
});

// ── 6: sw.js ist in ASSETS vollständig ───────────────────────────────────────
describe("sw.js ASSETS", () => {
  let sw;
  it("existiert", () => {
    sw = readText("sw.js");
  });
  it("cached data/wikistub_seed.json", () => {
    sw = sw || readText("sw.js");
    assert.ok(sw.includes("./data/wikistub_seed.json"), "data/wikistub_seed.json fehlt in SW ASSETS");
  });
  it("cached index.html und app.js", () => {
    sw = sw || readText("sw.js");
    assert.ok(sw.includes("./index.html"), "index.html fehlt in SW ASSETS");
    assert.ok(sw.includes("./app.js"),     "app.js fehlt in SW ASSETS");
  });
  it("nutzt skipWaiting + clients.claim", () => {
    sw = sw || readText("sw.js");
    assert.ok(sw.includes("skipWaiting"),    "skipWaiting fehlt in sw.js");
    assert.ok(sw.includes("clients.claim"), "clients.claim fehlt in sw.js");
  });
});

// ── 7: app.js registriert Service Worker ─────────────────────────────────────
describe("app.js", () => {
  it("registriert sw.js via serviceWorker.register", () => {
    const js = readText("app.js");
    assert.ok(js.includes("serviceWorker"), "serviceWorker.register fehlt in app.js");
    assert.ok(js.includes("sw.js"),         "sw.js-Pfad fehlt in serviceWorker.register");
  });

  it("rendert Datensatzfelder ohne innerHTML-Injektion", () => {
    const js = readText("app.js");
    assert.ok(!js.includes("detail.innerHTML"), "Detailansicht rendert Datensatzwerte per innerHTML");
    assert.ok(js.includes("textContent"), "Sicheres DOM-Rendering per textContent fehlt");
  });

  it("nutzt eindeutige ID-Hashes und toleriert Legacy-Hashes", () => {
    const js = readText("app.js");
    assert.ok(js.includes("stub="), "Eindeutiger ID-basierter Deep-Link fehlt");
    assert.ok(js.includes("decodeURIComponent"), "Legacy-Titelhash-Unterstützung fehlt");
  });

  it("macht klickbare Listen per Tastatur bedienbar", () => {
    const js = readText("app.js");
    assert.ok(js.includes("function bindActivation"), "Gemeinsame Tastaturaktivierung fehlt");
    assert.ok(js.includes('event.key === "Enter"'), "Enter-Aktivierung fehlt");
    assert.ok(js.includes('event.key === " "'), "Leertasten-Aktivierung fehlt");
    assert.ok(js.includes('setAttribute("role", "button")'), "Interaktive Semantik fehlt");
  });
});

describe("PWA-Aktualität", () => {
  it("lädt veränderliche Datendateien network-first mit Offline-Fallback", () => {
    const sw = readText("sw.js");
    assert.ok(sw.includes("networkFirst"), "Network-first-Strategie für Datendateien fehlt");
    assert.ok(sw.includes("cache.put"), "Online-Daten werden nicht in den Offline-Cache aktualisiert");
  });

  it("hält die Ergebnisliste auf schmalen Mobilgeräten sichtbar", () => {
    const html = readText("index.html");
    const mobileRule = html.slice(html.indexOf("@media (max-width: 420px)"));
    assert.ok(mobileRule.includes("#stub-panel"), "Mobile Stub-Liste wird nicht gestaltet");
    assert.ok(!mobileRule.includes("#stub-panel { display: none; }"), "Mobile Stub-Liste wird ausgeblendet");
    assert.ok(mobileRule.includes("width: 100%"), "Mobile Stub-Liste nutzt nicht die verfügbare Breite");
  });
});

// ── 8: iOS PWA-Installierbarkeit ─────────────────────────────────────────────
describe("iOS PWA-Installierbarkeit", () => {
  it("index.html hat viewport-fit=cover", () => {
    const html = readText("index.html");
    assert.ok(html.includes("viewport-fit=cover"), "viewport-fit=cover fehlt");
  });
  it("index.html hat apple-touch-icon Link auf 180px Icon", () => {
    const html = readText("index.html");
    assert.ok(
      html.includes("apple-touch-icon") && html.includes("apple-touch-icon-180.png"),
      "apple-touch-icon Link fehlt oder zeigt nicht auf 180px Datei"
    );
  });
  it("index.html hat apple-mobile-web-app-title Meta-Tag", () => {
    const html = readText("index.html");
    assert.ok(html.includes("apple-mobile-web-app-title"), "apple-mobile-web-app-title fehlt");
  });
  it("index.html hat apple-mobile-web-app-status-bar-style Meta-Tag", () => {
    const html = readText("index.html");
    assert.ok(html.includes("apple-mobile-web-app-status-bar-style"), "apple-mobile-web-app-status-bar-style fehlt");
  });
  it("index.html body nutzt safe-area-inset CSS", () => {
    const html = readText("index.html");
    assert.ok(html.includes("safe-area-inset"), "env(safe-area-inset-*) fehlt in CSS");
  });
  it("apple-touch-icon-180.png existiert physisch", () => {
    assert.ok(fileExists("icons/apple-touch-icon-180.png"), "icons/apple-touch-icon-180.png fehlt");
  });
  it("sw.js CACHE_NAME ist wikistub-seed-v1", () => {
    const sw = readText("sw.js");
    assert.ok(sw.includes('"wikistub-seed-v1"'), 'CACHE_NAME muss "wikistub-seed-v1" sein');
  });
  it("sw.js enthält apple-touch-icon-180.png in ASSETS", () => {
    const sw = readText("sw.js");
    assert.ok(sw.includes("apple-touch-icon-180.png"), "apple-touch-icon-180.png fehlt in SW ASSETS");
  });
  it("manifest display ist standalone (moderne iOS-Installierbarkeit)", () => {
    const m = readJson("manifest.webmanifest");
    assert.strictEqual(m.display, "standalone", "manifest display muss standalone sein");
  });
});

describe("Mehrsprachige Datenmaps", () => {
  it("jeder Stub hat normalisierte Sprachmaps für Definition und Relevanz", () => {
    const wiki = readJson("data/wikistub_seed.json").MetaWiki;
    const expected = ["de", "en", "es", "zh", "ja", "ru"];
    let checked = 0;
    for (const subs of Object.values(wiki)) {
      for (const entries of Object.values(subs)) {
        for (const e of entries) {
          assert.ok(e.definitions && typeof e.definitions === "object", `definitions fehlt bei "${e.title}"`);
          assert.ok(e.relevance_i18n && typeof e.relevance_i18n === "object", `relevance_i18n fehlt bei "${e.title}"`);
          for (const lang of expected) {
            assert.ok(Object.hasOwn(e.definitions, lang), `definitions.${lang} fehlt bei "${e.title}"`);
            assert.ok(Object.hasOwn(e.relevance_i18n, lang), `relevance_i18n.${lang} fehlt bei "${e.title}"`);
          }
          checked++;
        }
      }
    }
    assert.ok(checked >= 10, `Nur ${checked} Stubs geprüft`);
  });

  it("search-index enthält Sprachfelder für Browser-Fallbacks", () => {
    const first = readJson("data/search-index.json")[0];
    assert.ok(first.definitions && typeof first.definitions === "object");
    assert.ok(first.relevance_i18n && typeof first.relevance_i18n === "object");
    assert.ok(Object.hasOwn(first.definitions, "de"));
    assert.ok(Object.hasOwn(first.definitions, "en"));
  });

  it("app.js nutzt Sprach-Fallbackfunktionen", () => {
    const js = readText("app.js");
    assert.ok(js.includes("function localizedText"), "localizedText fehlt");
    assert.ok(js.includes("function definitionText"), "definitionText fehlt");
    assert.ok(js.includes("function relevanceText"), "relevanceText fehlt");
  });
});
