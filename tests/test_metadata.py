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

    assert "## Last-checked:" in content, "Last-checked timestamp missing in llms.txt"
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
    """Verify pyproject.toml PEP 621 classifiers, python version support and project URLs."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"
    content = pyproject_path.read_text(encoding="utf-8")

    assert '"Programming Language :: Python :: 3.10"' in content
    assert '"Programming Language :: Python :: 3.11"' in content
    assert '"Programming Language :: Python :: 3.12"' in content
    assert '"Programming Language :: Python :: 3.13"' in content
    assert '"Operating System :: OS Independent"' in content
    assert '"License :: OSI Approved :: MIT License"' in content

    assert 'Homepage = "https://github.com/dev-bricks/WikiStub-Seed"' in content
    assert 'Repository = "https://github.com/dev-bricks/WikiStub-Seed.git"' in content
    assert 'Documentation = "https://github.com/dev-bricks/WikiStub-Seed#readme"' in content
    assert '"Bug Tracker" = "https://github.com/dev-bricks/WikiStub-Seed/issues"' in content


def test_security_policy_invariants():
    """Verify SECURITY.md contains bilingual sections, zero-egress invariants and contacts."""
    sec_path = PROJECT_ROOT / "SECURITY.md"
    assert sec_path.is_file(), "SECURITY.md missing"
    content = sec_path.read_text(encoding="utf-8")

    assert "## Deutsch" in content
    assert "## English" in content
    assert "Zero-Egress" in content or "zero-egress" in content.lower()
    assert "Local-First" in content or "local-first" in content.lower()
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "Private Vulnerability Reporting" in content


def test_ci_workflow_integrity():
    """Verify GitHub Actions workflow file exists and configures multi-version matrix."""
    ci_path = PROJECT_ROOT / ".github" / "workflows" / "tests.yml"
    assert ci_path.is_file(), "tests.yml missing"
    content = ci_path.read_text(encoding="utf-8")

    assert "python-version" in content
    assert "'3.10'" in content or '"3.10"' in content
    assert "'3.13'" in content or '"3.13"' in content
    assert "ubuntu-latest" in content
    assert "windows-latest" in content
    assert "node --test" in content


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

