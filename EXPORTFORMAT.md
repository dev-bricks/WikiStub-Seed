# Exportformat - MetaWiki

Stand: 2026-05-27
Schema-Ziel: `metawiki-data-v1`

## Zweck

`metawiki.json` bleibt die autoritative Datenquelle für MetaWiki. Für Web/PWA, LLM-Workflows, Obsidian-Exporte und spätere Such-APIs wird dieses bestehende Format als stabiles Austauschformat geführt und schrittweise mit einer expliziten Schema-Hülle gehärtet.

## Aktueller Datenkern

Die bestehende Datei folgt der Struktur:

```json
{
  "MetaWiki": {
    "07_Informatik_KI": {
      "Software_Engineering": [
        {
          "title": "Domain-Driven Design",
          "definition_de": "Ein Ansatz zur Modellierung komplexer Software, der die Fachdomäne in den Mittelpunkt stellt.",
          "definition_en": "An approach to modeling complex software that places the business domain at the center of development.",
          "relevance": "Hilft, komplexe Systeme verständlich und wartbar zu gestalten.",
          "tags": ["Informatik", "Software Engineering"]
        }
      ]
    }
  }
}
```

## Zielhülle für `metawiki-data-v1`

Für neue Exporte soll eine Hülle ergänzt werden, ohne den aktuellen Kern unnötig zu brechen:

```json
{
  "schema": "metawiki-data-v1",
  "generated_at": "2026-05-27T00:00:00Z",
  "source": "metawiki.json",
  "languages": ["de", "en"],
  "stub_count": 630,
  "data": {
    "MetaWiki": {}
  }
}
```

## Stabilitätsregeln

- `title`, `definition_de`, `definition_en`, `relevance` und `tags` bleiben die Kernfelder.
- Kategorien und Unterkategorien bleiben menschenlesbare Schlüssel.
- Neue Felder sind additiv und dürfen bestehende Parser nicht brechen.
- Web/PWA, Obsidian und API-Exports werden aus demselben Datenkern generiert.
- Der Export enthält keine Nutzerkonten, Tokens oder private Projektdaten.

## Plattformbezug

Das Format ist der Übergabepunkt zwischen Desktop/CLI, Web/PWA und mobilen Browsern. Native Android-/iOS-Apps sind nicht nötig, solange eine PWA denselben Datensatz offline lesen und durchsuchen kann.
