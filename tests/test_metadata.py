"""Metadata, manifest parity and documentation tests for WikiStub-Seed."""

import json
import re
from pathlib import Path

from language_model import iter_metawiki_entries


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# tomllib is stdlib only from Python 3.11 on; pyproject.toml's own
# requires-python = ">=3.10" commits this project to 3.10 too, and CI's
# python-tests matrix actually runs 3.10 (found failing this way on
# Windows and Ubuntu 3.10 runners: "ModuleNotFoundError: No module named
# 'tomllib'"). A single-line regex read of `version = "..."` under
# [project] needs no TOML parser (and no new dependency) for the one field
# this test actually uses.
_VERSION_RE = re.compile(r'(?m)^\s*version\s*=\s*"([^"]+)"')


def _pyproject_version(pyproject_path: Path) -> str | None:
    content = pyproject_path.read_text(encoding="utf-8")
    match = _VERSION_RE.search(content)
    return match.group(1) if match else None


def test_version_parity():
    """Verify version parity across pyproject.toml and CHANGELOG.md."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"

    pyproject_version = _pyproject_version(pyproject_path)
    assert pyproject_version, "Version missing in pyproject.toml"

    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    assert changelog_path.is_file(), "CHANGELOG.md missing"
    changelog_content = changelog_path.read_text(encoding="utf-8")

    assert f"[{pyproject_version}]" in changelog_content, (
        f"Version {pyproject_version} not documented in CHANGELOG.md"
    )


def test_core_documentation_files_exist():
    """Verify all core documentation and governance files exist and are non-empty."""
    required_files = [
        "README.md",
        "README_de.md",
        "llms.txt",
        "CHANGELOG.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "EMBEDDING_SEARCH_API.md",
        "EXPORTFORMAT.md",
        "ellmos-module.v2.json",
        "MARKETING-LOG.txt",
        "THIRD_PARTY_LICENSES.md",
    ]

    for fname in required_files:
        fpath = PROJECT_ROOT / fname
        assert fpath.is_file(), f"Required file {fname} is missing"
        assert fpath.stat().st_size > 50, f"File {fname} is unexpectedly small or empty"


def test_llms_txt_structure_and_freshness():
    """Verify llms.txt contains necessary metadata, links and recent timestamp."""
    llms_path = PROJECT_ROOT / "llms.txt"
    assert llms_path.is_file(), "llms.txt missing"

    content = llms_path.read_text(encoding="utf-8")

    assert re.search(r"## Last-checked: 2026-09-\d{2}", content), "Last-checked timestamp missing in llms.txt"
    assert "https://github.com/dev-bricks/WikiStub-Seed" in content, "Canonical repo link missing in llms.txt"
    assert "wikistub_seed.json" in content, "Authoritative dataset not mentioned in llms.txt"
    assert "630" in content, "Stub count missing in llms.txt"


def test_ellmos_module_schema():
    """Verify ellmos-module.v2.json contains valid module metadata."""
    manifest_path = PROJECT_ROOT / "ellmos-module.v2.json"
    assert manifest_path.is_file(), "ellmos-module.v2.json missing"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("schema") == "ellmos.module.v2"
    assert data.get("id") == "WikiStub-Seed"
    assert data.get("visibility") == "public"
    assert "provides" in data and len(data["provides"]) >= 1


def test_dataset_integrity():
    """Verify wikistub_seed.json has 630 stubs across 12 top-level domains."""
    data_path = PROJECT_ROOT / "wikistub_seed.json"
    assert data_path.is_file(), "wikistub_seed.json missing"

    data = json.loads(data_path.read_text(encoding="utf-8"))
    root = data.get("MetaWiki", {})
    assert len(root) == 12, f"Expected 12 categories, found {len(root)}"

    entries = list(iter_metawiki_entries(data))
    assert len(entries) == 630, f"Expected 630 stubs, found {len(entries)}"

    for cat, sub, entry in entries:
        assert "title" in entry, f"Entry in {cat}/{sub} missing title"
        assert "definitions" in entry, f"Stub {entry['title']} missing definitions map"
        assert "relevance_i18n" in entry, f"Stub {entry['title']} missing relevance_i18n map"


def test_pyproject_classifiers_and_urls():
    """Verify PEP 621/639 metadata, python version support, OS classifiers and project URLs."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"
    content = pyproject_path.read_text(encoding="utf-8")

    assert re.search(r'(?m)^requires\s*=\s*\[\s*"setuptools>=77\.0\.3"\s*\]\s*$', content)
    assert '"Programming Language :: Python :: 3.10"' in content
    assert '"Programming Language :: Python :: 3.11"' in content
    assert '"Programming Language :: Python :: 3.12"' in content
    assert '"Programming Language :: Python :: 3.13"' in content
    assert '"Operating System :: OS Independent"' in content
    assert '"Operating System :: Microsoft :: Windows"' in content
    assert '"Operating System :: POSIX :: Linux"' in content
    assert '"Operating System :: MacOS"' in content
    assert re.search(r'(?m)^license\s*=\s*"MIT"\s*$', content)
    assert re.search(r'(?m)^license-files\s*=\s*\[\s*"LICENSE"\s*\]\s*$', content)
    assert '"License :: OSI Approved :: MIT License"' not in content

    assert 'Homepage = "https://github.com/dev-bricks/WikiStub-Seed"' in content
    assert 'Repository = "https://github.com/dev-bricks/WikiStub-Seed.git"' in content
    assert 'Documentation = "https://github.com/dev-bricks/WikiStub-Seed#readme"' in content
    assert '"Bug Tracker" = "https://github.com/dev-bricks/WikiStub-Seed/issues"' in content
    assert 'Issues = "https://github.com/dev-bricks/WikiStub-Seed/issues"' in content
    assert 'Changelog = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/CHANGELOG.md"' in content
    assert 'Security = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/SECURITY.md"' in content
    assert '"Parent Organization" = "https://github.com/dev-bricks"' in content
    assert '"Umbrella Ecosystem" = "https://github.com/open-bricks"' in content
    assert "[project.optional-dependencies]" in content
    assert 'addopts = "-ra -v"' in content


def test_security_policy_invariants():
    """Verify SECURITY.md contains bilingual sections, zero-egress invariants, SLA and contacts."""
    sec_path = PROJECT_ROOT / "SECURITY.md"
    assert sec_path.is_file(), "SECURITY.md missing"
    content = sec_path.read_text(encoding="utf-8")

    assert "## Deutsch" in content
    assert "## English" in content
    assert "Unterstützte Versionen" in content
    assert "Supported Versions" in content
    assert "Zero-Egress" in content or "zero-egress" in content.lower()
    assert "Local-First" in content or "local-first" in content.lower()
    assert "48 Stunden" in content or "48 hours" in content
    assert "security@open-bricks.org" in content
    assert "security@dev-bricks.org" in content
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "lukas@open-bricks.org" in content
    assert "Private Vulnerability Reporting" in content
    assert "48" in content  # 48h SLA
    assert "security/advisories" in content


def test_ci_workflow_integrity():
    """Verify GitHub Actions workflow file exists, configures multi-version matrix and concurrency."""
    ci_path = PROJECT_ROOT / ".github" / "workflows" / "tests.yml"
    assert ci_path.is_file(), "tests.yml missing"
    content = ci_path.read_text(encoding="utf-8")

    assert "python-version" in content
    assert "'3.10'" in content or '"3.10"' in content
    assert "'3.13'" in content or '"3.13"' in content
    assert "ubuntu-latest" in content
    assert "windows-latest" in content
    assert "node --test" in content
    assert "cancel-in-progress: true" in content
    assert "concurrency:" in content


def test_sibling_tools_matrix():
    """Verify sibling tools matrix exists in both README.md and README_de.md."""
    for fname in ["README.md", "README_de.md"]:
        path = PROJECT_ROOT / fname
        assert path.is_file(), f"{fname} missing"
        content = path.read_text(encoding="utf-8")
        assert "dev-bricks/DevCenter" in content or "DevCenter" in content
        assert "dev-bricks/CodeBox" in content or "CodeBox" in content
        assert "dev-bricks/safe-start-for-codex" in content or "safe-start-for-codex" in content
        assert "open-bricks" in content


def test_readme_bilingual_badges_and_mermaid():
    """Verify modern badges and dual Mermaid diagrams in README.md and README_de.md."""
    for fname in ["README.md", "README_de.md"]:
        path = PROJECT_ROOT / fname
        assert path.is_file(), f"{fname} missing"
        content = path.read_text(encoding="utf-8")

        assert "shields.io" in content
        assert "version-1.1.11" in content
        assert "dev--bricks" in content
        assert "open--bricks" in content
        assert "third--party%20licenses" in content
        assert "marketing%20log" in content
        assert "flowchart TD" in content
        assert "sequenceDiagram" in content
        assert "autonumber" in content


def test_quick_navigation_anchors_and_parity():
    """Verify 15-point quick navigation exists with bidirectional anchor parity across README.md and README_de.md."""
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### Quick Navigation" in readme_en
    assert "### Schnellnavigation" in readme_de

    en_points = [
        "1. Executive Summary",
        "2. System Architecture & Data Flow",
        "3. Zero-Egress Lifecycle & Query Flow",
        "4. Safety Model & Governance Invariants",
        "5. Installation & Quick Start",
        "6. Local Edit Mode & HTTP Server",
        "7. Core Commands & CLI Operations",
        "8. Repository Map & Key Files",
        "9. Data Shape & Knowledge Schema",
        "10. Sibling Tools & Ecosystem Matrix",
        "11. Discovery & Search Keywords",
        "12. Security & Vulnerability Reporting",
        "13. Third-Party Licenses & Transparency",
        "14. Marketing & Target Personas",
        "15. German Documentation / Deutsche Version",
    ]
    for pt in en_points:
        assert pt in readme_en, f"Missing English quick navigation point: {pt}"

    de_points = [
        "1. Übersicht & Management Summary",
        "2. Systemarchitektur & Datenfluss",
        "3. Zero-Egress Lebenszyklus & Abfragefluss",
        "4. Sicherheitsmodell & Governance-Invarianten",
        "5. Installation & Schnellstart",
        "6. Lokaler Editiermodus & HTTP-Server",
        "7. Kernbefehle & CLI-Betrieb",
        "8. Repository-Struktur & Hauptdateien",
        "9. Datenstruktur & Wissensschema",
        "10. Geschwisterwerkzeuge & Ökosystem-Matrix",
        "11. Auffindbarkeit & Suchbegriffe",
        "12. Sicherheitsrichtlinie & Meldewege",
        "13. Drittanbieter-Lizenzen & Transparenz",
        "14. Marketing & Zielgruppen",
        "15. Englische Dokumentation / English Version",
    ]
    for pt in de_points:
        assert pt in readme_de, f"Missing German quick navigation point: {pt}"

    # Verify bidirectional anchor parity
    assert "(#13-third-party-licenses--transparency)" in readme_en
    assert "(#14-marketing--target-personas)" in readme_en
    assert "(#13-drittanbieter-lizenzen--transparenz)" in readme_de
    assert "(#14-marketing--zielgruppen)" in readme_de


def test_governance_invariants_table():
    """Verify 10-point Governance Invariants table and canonical IDs in README.md and README_de.md."""
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## 4. Safety Model & Governance Invariants" in readme_en
    assert "## 4. Sicherheitsmodell & Governance-Invarianten" in readme_de

    invariants = [
        "100% Local-First & Zero-Egress",
        "Non-Elevation (RunAsInvoker",
        "Deterministic Knowledge Schema",
        "Pure Offline Storage & Zero Telemetry",
        "Localhost-Bound Edit Server (127.0.0.1",
        "PBKDF2 Password Hashing & Soft-Delete Trash",
        "Cross-Platform Operating Parity",
        "Pure Python Standard Library Core",
        "Cloud-Sync Conflict Defense",
        "48h Security SLA & Coordinated Disclosure",
    ]
    for inv in invariants:
        assert inv in readme_en, f"Missing invariant in README.md: {inv}"

    de_invariants = [
        "100% Local-First & Zero-Egress",
        "Non-Elevation (RunAsInvoker",
        "Deterministisches Wissensschema",
        "Reine Offline-Speicherung & Null Telemetrie",
        "Localhost-gebundener Editierserver (127.0.0.1",
        "PBKDF2-Passworthash & Soft-Delete-Papierkorb",
        "Plattformübergreifende Betriebsparität",
        "Reiner Python-Standardbibliothek-Kern",
        "Cloud-Sync-Konflikt-Schutz",
        "48h Sicherheits-SLA & CVD",
    ]
    for inv in de_invariants:
        assert inv in readme_de, f"Missing invariant in README_de.md: {inv}"

    canonical_ids = [
        "INV-LOCAL-01",
        "INV-SEC-02",
        "INV-SCHEMA-03",
        "INV-STORE-04",
        "INV-SRV-05",
        "INV-AUTH-06",
        "INV-PLAT-07",
        "INV-CORE-08",
        "INV-SYNC-09",
        "INV-SLA-10",
    ]
    for inv_id in canonical_ids:
        assert inv_id in readme_en, f"Missing {inv_id} in README.md"
        assert inv_id in readme_de, f"Missing {inv_id} in README_de.md"


def test_gitignore_conflict_and_lock_patterns():
    """Verify .gitignore filters cloud-sync conflicts, multi-agent lock patterns and caches."""
    gi_path = PROJECT_ROOT / ".gitignore"
    assert gi_path.is_file(), ".gitignore missing"
    content = gi_path.read_text(encoding="utf-8")

    assert "*.sync-conflict-*" in content
    assert "*.conflict" in content
    assert "*-conflict-*" in content
    assert "LOCK.*" in content
    assert "*.lock" in content
    assert "LOCK*.txt" in content
    assert "wheelhouse/" in content
    assert ".wheel-smoke/" in content
    assert "coverage/" in content
    assert ".nyc_output/" in content
    assert ".hypothesis/" in content
    assert "node_modules/" in content
    assert "*.orig" in content
    assert "*.rej" in content


def test_ci_concurrency_configured():
    """Verify concurrency group and cancel-in-progress are configured in CI workflows."""
    for wfname in ["tests.yml", "source-platform-smoke.yml"]:
        wf_path = PROJECT_ROOT / ".github" / "workflows" / wfname
        assert wf_path.is_file(), f"{wfname} missing"
        content = wf_path.read_text(encoding="utf-8")
        assert "concurrency:" in content, f"concurrency missing in {wfname}"
        assert "cancel-in-progress: true" in content, f"cancel-in-progress missing in {wfname}"


def test_ci_no_duplicate_concurrency():
    """Verify CI workflows do not contain duplicate top-level concurrency blocks."""
    for wfname in ["tests.yml", "source-platform-smoke.yml"]:
        wf_path = PROJECT_ROOT / ".github" / "workflows" / wfname
        assert wf_path.is_file(), f"{wfname} missing"
        content = wf_path.read_text(encoding="utf-8")
        concurrency_count = len(re.findall(r'(?m)^concurrency:\s*$', content))
        assert concurrency_count == 1, f"Expected exactly 1 concurrency block in {wfname}, found {concurrency_count}"


def test_ci_job_timeouts_configured():
    """Verify that CI workflows define explicit job timeout-minutes to guard against hung runners."""
    expected_timeouts = {
        "tests.yml": ["timeout-minutes: 15", "timeout-minutes: 10"],
        "source-platform-smoke.yml": ["timeout-minutes: 10"],
        "stale.yml": ["timeout-minutes: 5"],
        "welcome.yml": ["timeout-minutes: 5"],
    }
    for wfname, timeouts in expected_timeouts.items():
        wf_path = PROJECT_ROOT / ".github" / "workflows" / wfname
        assert wf_path.is_file(), f"{wfname} missing"
        content = wf_path.read_text(encoding="utf-8")
        for expected in timeouts:
            assert expected in content, f"Expected '{expected}' in {wfname}"


def test_local_marketing_log_exists():
    """Verify local MARKETING-LOG.txt exists and logs recent Pfad B improvements."""
    mlog_path = PROJECT_ROOT / "MARKETING-LOG.txt"
    assert mlog_path.is_file(), "MARKETING-LOG.txt missing"
    content = mlog_path.read_text(encoding="utf-8")
    assert "[GITHUBBOT_ONE_REPO_MARKETING_AND_DESIGN]" in content
    assert "PFAD_B_UPGRADE" in content
    assert "WikiStub-Seed" in content


def test_readme_security_sla_badges():
    """Verify both README.md and README_de.md contain Security SLA badges."""
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "security%20SLA-48h%20response-blue.svg" in readme_en or "security--SLA-48h" in readme_en
    assert "SECURITY.md" in readme_en

    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "security%20SLA-48h%20response-blue.svg" in readme_de or "Sicherheits--SLA-48h" in readme_de
    assert "SECURITY.md" in readme_de


def test_third_party_licenses_audit():
    """Verify THIRD_PARTY_LICENSES.md contains 100% permissive inventory and all 10 governance invariants."""
    lic_path = PROJECT_ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.is_file(), "THIRD_PARTY_LICENSES.md missing"
    content = lic_path.read_text(encoding="utf-8")

    assert "PSFL-2.0" in content
    assert "MIT License" in content or "MIT" in content
    assert "Apache-2.0" in content or "Apache" in content
    assert "Zero-Egress" in content
    assert "RunAsInvoker" in content

    # Verify all 10 governance invariant IDs
    for i in range(1, 11):
        if i == 1:
            code = "INV-LOCAL-01"
        elif i == 2:
            code = "INV-SEC-02"
        elif i == 3:
            code = "INV-SCHEMA-03"
        elif i == 4:
            code = "INV-STORE-04"
        elif i == 5:
            code = "INV-SRV-05"
        elif i == 6:
            code = "INV-AUTH-06"
        elif i == 7:
            code = "INV-PLAT-07"
        elif i == 8:
            code = "INV-CORE-08"
        elif i == 9:
            code = "INV-SYNC-09"
        else:
            code = "INV-SLA-10"
        assert code in content, f"Missing {code} in THIRD_PARTY_LICENSES.md"


def test_pyproject_extended_urls():
    """Verify PEP 621 URLs include Third-Party Licenses, Marketing Log, and LLM Ready."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"
    content = pyproject_path.read_text(encoding="utf-8")

    assert '"Third-Party Licenses"' in content
    assert "THIRD_PARTY_LICENSES.md" in content
    assert '"Marketing Log"' in content
    assert "MARKETING-LOG.txt" in content
    assert '"LLM Ready"' in content
    assert "llms.txt" in content


def test_marketing_log_full_pfad_b_structure():
    """Verify MARKETING-LOG.txt follows standard Pfad B structure with personas and competitive matrix."""
    mlog_path = PROJECT_ROOT / "MARKETING-LOG.txt"
    assert mlog_path.is_file(), "MARKETING-LOG.txt missing"
    content = mlog_path.read_text(encoding="utf-8")

    assert "1. REPOSITORY AUDIT & DISCOVERABILITY BASELINE" in content
    assert "2. TARGET PERSONAS & USER JOURNEYS" in content
    assert "3. HIGH-INTENT SEARCH QUERIES (BILINGUAL EN & DE)" in content
    assert "4. COMPETITIVE DIFFERENTIATION MATRIX" in content
    assert "5. STRATEGIC ACTION ITEMS & DISCOVERABILITY ROADMAP" in content
    assert "AI & LLM Engineers" in content
    assert "Kiwix" in content

