# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu diesem Projekt beizutragen!

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit dem Label `bug`.
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit dem Label `enhancement`.
3. **Dokumentation verbessern:** Reichen Sie Vorschläge mit dem Label `documentation` ein.
4. **Code beitragen:** Erstellen Sie einen Pull Request.

### Pull Requests & Workflow

1. Forken Sie das Repository auf GitHub.
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`.
3. Committen Sie Ihre Änderungen nach standardisierten Konventionen (`feat:`, `fix:`, `docs:`, `chore:`).
4. Führen Sie alle lokalen Quality Gates aus (siehe unten).
5. Pushen Sie den Branch: `git push origin feature/mein-feature`.
6. Erstellen Sie einen Pull Request. Neue PRs werden via `.github/workflows/auto-assign.yml` automatisch zugewiesen.

### Quality Gates (Vor dem Commit)

Vor jedem Commit und Pull Request müssen folgende Verifikationsschritte 100% grün durchlaufen:

```bash
# 1. Python Testsuite (179 Tests)
pytest -v

# 2. Node.js PWA Testsuite (45 Tests)
node --test web_publisher/tests/publisher.test.mjs

# 3. Linter & Format-Check
ruff check .

# 4. Bytecode-Kompilierung
python -m compileall .

# 5. Dataset-Integrität & Pipeline-Validierung
python wikistub_seed_cli.py stats
python wikistub_seed_pipeline.py validate
```

### Entwicklungsrichtlinien & Invarianten

- **Plan D Architektur:** Entwicklungsarbeiten finden ausschließlich im lokalen Git-Klon statt (`C:\_Local_DEV\repos\WikiStub-Seed`). OneDrive-Ordner dienen rein als spiegelnde Projektion.
- **Version Freeze Disziplin:** Die Version `1.1.12` ist gemäß Richtlinie `T-20260920-167562623` eingefroren. Änderungen und Ergänzungen werden unter `## [Unreleased]` im `CHANGELOG.md` dokumentiert.
- **100% Local-First & Zero Egress (INV-LOCAL-01 / INV-SEC-02):** Unprivilegierte Ausführung (`RunAsInvoker`), keine Telemetrie, keine unerwünschten Netzwerkverbindungen.
- **Encoding:** Strikte UTF-8-Codierung für alle Quell- und Datendateien.

---

## English

Thank you for your interest in contributing to WikiStub-Seed!

### How to Contribute

1. **Report bugs:** Create an issue with the `bug` label.
2. **Suggest features:** Create an issue with the `enhancement` label.
3. **Improve documentation:** Submit proposals with the `documentation` label.
4. **Contribute code:** Open a Pull Request.

### Pull Requests & Workflow

1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Commit your changes following conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
4. Run all local quality gates (see below).
5. Push your branch: `git push origin feature/my-feature`.
6. Open a Pull Request. New PRs are automatically triaged via `.github/workflows/auto-assign.yml`.

### Quality Gates (Pre-Commit Verification)

Before committing and submitting a PR, ensure all verification gates are 100% green:

```bash
# 1. Python test suite (179 tests)
pytest -v

# 2. Node.js PWA test suite (45 tests)
node --test web_publisher/tests/publisher.test.mjs

# 3. Linter & formatting checks
ruff check .

# 4. Bytecode compilation
python -m compileall .

# 5. Dataset integrity & pipeline validation
python wikistub_seed_cli.py stats
python wikistub_seed_pipeline.py validate
```

### Architectural & Governance Invariants

- **Plan D Architecture:** Canonical development takes place solely in the local clone (`C:\_Local_DEV\repos\WikiStub-Seed`). OneDrive paths serve only as mirrors.
- **Version Freeze Discipline:** Version `1.1.12` is frozen per `T-20260920-167562623`. All additions must be documented under `## [Unreleased]` in `CHANGELOG.md`.
- **100% Local-First & Zero Egress (INV-LOCAL-01 / INV-SEC-02):** Unprivileged user mode (`RunAsInvoker`), zero telemetry, zero unsolicited external egress.
- **Encoding:** Strict UTF-8 encoding across all data and code assets.
