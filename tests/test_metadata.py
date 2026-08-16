"""Metadata, manifest parity and documentation tests for WikiStub-Seed."""

import json
from pathlib import Path
import tomllib

from language_model import iter_metawiki_entries


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_version_parity():
    """Verify version parity across pyproject.toml and CHANGELOG.md."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    pyproject_version = pyproject_data.get("project", {}).get("version")
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
