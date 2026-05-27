# MetaWiki Web/PWA Publisher

Stand: 2026-05-27

Dieser Ordner dokumentiert den geplanten plattformübergreifenden Pfad für MetaWiki. Die Umsetzung soll einen statischen Web-Build aus `metawiki.json` erzeugen, der auf GitHub Pages oder einem anderen statischen Host laufen kann.

## Ziel

- Statische, durchsuchbare Oberfläche für alle MetaWiki-Stubs.
- Offlinefähige PWA für Android, iOS und Desktop-Browser.
- Keine Serverpflicht und keine Nutzerkonten.
- Suchindex und Manifest werden reproduzierbar aus `metawiki.json` erzeugt.

## Nicht-Ziele

- Kein nativer Android- oder iOS-Clone.
- Keine Windows-Store-App ohne fertige lokale Oberfläche.
- Keine zweite Datenquelle neben `metawiki.json`.
- Keine automatische externe API-Kommunikation im Web-Build.

## Erste Umsetzungsschritte

1. Datenhülle `metawiki-data-v1` aus `metawiki.json` erzeugen.
2. Statischen Suchindex für Titel, Kategorien, Definitionen und Tags bauen.
3. Minimalen Reader mit Kategoriebaum, Suche und Stub-Detailansicht erstellen.
4. PWA-Manifest und Offline-Cache ergänzen.
5. Mobile Smoke-Tests für Android- und iOS-Browser dokumentieren.
