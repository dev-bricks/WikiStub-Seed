# WikiStub-Seed Web/PWA Publisher

Stand: 2026-06-14

Dieser Ordner dokumentiert den geplanten plattformübergreifenden Pfad für WikiStub-Seed. Die Umsetzung soll einen statischen Web-Build aus `wikistub_seed.json` erzeugen, der auf GitHub Pages oder einem anderen statischen Host laufen kann.

## Ziel

- Statische, durchsuchbare Oberfläche für alle WikiStub-Seed-Stubs.
- Offlinefähige PWA für Android, iOS und Desktop-Browser.
- Keine Serverpflicht und keine Nutzerkonten.
- Suchindex und Manifest werden reproduzierbar aus `wikistub_seed.json` erzeugt.

## Nicht-Ziele

- Kein nativer Android- oder iOS-Clone.
- Keine Windows-Store-App ohne fertige lokale Oberfläche.
- Keine zweite Datenquelle neben `wikistub_seed.json`.
- Keine automatische externe API-Kommunikation im Web-Build.

## Erste Umsetzungsschritte

Stand 2026-06-14: Der Build normalisiert `definitions.{lang}` und `relevance_i18n.{lang}` für `de`, `en`, `es`, `zh`, `ja` und `ru`. Der sichtbare Web-Reader nutzt weiter DE/EN, liest aber bereits über Sprach-Fallbacks.

1. Datenhülle `wikistub-seed-data-v1` aus `wikistub_seed.json` erzeugen.
2. Statischen Suchindex für Titel, Kategorien, Definitionen und Tags bauen.
3. Minimalen Reader mit Kategoriebaum, Suche und Stub-Detailansicht erstellen.
4. PWA-Manifest und Offline-Cache ergänzen.
5. Mobile Smoke-Tests für Android- und iOS-Browser dokumentieren.
