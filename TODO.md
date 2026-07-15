# TODO

## STATUS

| Category | Status | Notes |
|---|---|---|
| Tests | PASS | Python, CLI/pipeline and static PWA gates run on Windows; CI covers Windows, Linux and macOS source paths. |
| Documentation | READY | Public README, security, contribution, changelog, format and release-gate documents are present. |
| Release hygiene | PASS | Public repository metadata, pinned project Actions, GitHub default CodeQL and fail-closed data writes were reviewed on 2026-07-15. |
| Integration | READY | Standalone multilingual dataset and offline Web/PWA module with `wikistub-seed-data-v1` export. |

## Open

- [ ] Decide whether English relevance texts should be authored independently; the reader currently falls back to German where `relevance_i18n.en` is empty.
- [ ] Run and document manual browser/device smokes for offline install and deep links on current iOS, Android and desktop browsers.
- [ ] Specify an optional embedding/search API without making network access or external dependencies part of the core runtime.

## Completed

- [x] Provide language-specific CLI, pipeline export and PWA selection for DE/EN/ES/ZH/JA/RU.
- [x] Remove hard-coded DE/EN assumptions from shared localization helpers and generated Web data.
- [x] Make required JSON inputs fail closed and make generated/output writes atomic.
- [x] Add explicit translation call, cost and finite-budget gates.
- [x] Add `RELEASE_GATE.md`, retain GitHub default CodeQL, and pin project GitHub Actions.
