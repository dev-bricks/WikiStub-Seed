"""Metadata, manifest parity and documentation tests for WikiStub-Seed."""

import json
import re
from pathlib import Path

from language_model import iter_metawiki_entries
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version


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


def test_dev_test_pytest_floor_excludes_cve_2025_71176_range():
    """Keep each test installer above pytest's affected pre-9.0.3 range."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    extras_match = re.search(
        r"(?ms)^\[project\.optional-dependencies\]\s*(.*?)(?=^\[|\Z)",
        pyproject,
    )
    assert extras_match is not None, "Project optional dependencies are missing"

    def extra_requirements(extra: str) -> list[Requirement]:
        match = re.search(
            rf"(?ms)^\s*{re.escape(extra)}\s*=\s*\[(.*?)^\s*\]",
            extras_match.group(1),
        )
        assert match is not None, f"The {extra!r} extra is missing"
        values = re.findall(r'(?m)^\s*"([^"\n]+)"\s*,?\s*$', match.group(1))
        return [Requirement(value) for value in values]

    requirements_file = (PROJECT_ROOT / "requirements-dev.txt").read_text(
        encoding="utf-8"
    )
    file_requirements = [
        Requirement(line.split("#", 1)[0].strip())
        for line in requirements_file.splitlines()
        if line.split("#", 1)[0].strip()
    ]

    pytest_requirements = [
        requirement
        for group in (extra_requirements("dev"), extra_requirements("test"), file_requirements)
        for requirement in group
        if canonicalize_name(requirement.name) == "pytest"
    ]
    assert len(pytest_requirements) == 3, (
        "Expected pytest declarations in the dev and test extras and the CI requirements file"
    )

    affected_versions = tuple(
        Version(version)
        for version in ("8.0.0", "8.4.0", "9.0.0", "9.0.2", "9.0.3rc1")
    )
    patched_floor = Version("9.0.3")
    acceptable_releases = tuple(
        Version(version) for version in ("9.0.3", "9.0.4", "9.1.0", "10.0.0")
    )
    for requirement in pytest_requirements:
        assert requirement.specifier, f"pytest requirement {requirement!s} has no version constraint"
        lower_bounds = [
            specifier
            for specifier in requirement.specifier
            if specifier.operator in {">=", ">", "==", "~="}
            and not specifier.version.endswith(".*")
            and Version(specifier.version) >= patched_floor
        ]
        assert lower_bounds, (
            f"pytest requirement {requirement!s} has no semantic lower bound at or above {patched_floor}"
        )
        assert any(requirement.specifier.contains(release) for release in acceptable_releases), (
            f"pytest requirement {requirement!s} admits no supported patched release"
        )
        for affected in affected_versions:
            assert not requirement.specifier.contains(affected, prereleases=True), (
                f"pytest requirement {requirement!s} permits affected version {affected}"
            )


def test_core_documentation_files_exist():
    """Verify all core documentation and governance files exist and are non-empty."""
    required_files = [
        "README.md",
        "README_de.md",
        "llms.txt",
        "CHANGELOG.md",
        "LICENSE",
        "NOTICE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "EMBEDDING_SEARCH_API.md",
        "EXPORTFORMAT.md",
        "ellmos-module.v2.json",
        "MARKETING-LOG.txt",
        "THIRD_PARTY_LICENSES.md",
        "THIRD_PARTY_LICENSES.txt",
    ]

    for fname in required_files:
        fpath = PROJECT_ROOT / fname
        assert fpath.is_file(), f"Required file {fname} is missing"
        assert fpath.stat().st_size > 50, f"File {fname} is unexpectedly small or empty"


def test_llms_txt_structure_and_scope():
    """Verify the project index links to the canonical repo and primary data/docs."""
    llms_path = PROJECT_ROOT / "llms.txt"
    assert llms_path.is_file(), "llms.txt missing"

    content = llms_path.read_text(encoding="utf-8")

    assert "https://github.com/dev-bricks/WikiStub-Seed" in content, "Canonical repo link missing in llms.txt"
    assert "wikistub_seed.json" in content, "Authoritative dataset not mentioned in llms.txt"
    assert "630" in content, "Stub count missing in llms.txt"
    assert "README.md" in content and "README_de.md" in content
    assert "THIRD_PARTY_LICENSES.md" in content and "SECURITY.md" in content
    for filename in ("README.md", "README_de.md", "THIRD_PARTY_LICENSES.md", "SECURITY.md", "wikistub_seed.json"):
        assert (PROJECT_ROOT / filename).is_file(), f"Indexed target {filename} is missing"


def test_ellmos_module_schema():
    """Verify ellmos-module.v2.json contains valid module metadata."""
    manifest_path = PROJECT_ROOT / "ellmos-module.v2.json"
    assert manifest_path.is_file(), "ellmos-module.v2.json missing"

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data.get("schema") == "ellmos.module.v2"
    assert data.get("id") == "WikiStub-Seed"
    assert data.get("visibility") == "public"
    assert "provides" in data and len(data["provides"]) >= 1
    assert data.get("boundaries", {}).get("network") == "optional"


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
    assert re.search(r'(?m)^license-files\s*=\s*\[\s*"LICENSE",\s*"NOTICE",\s*"THIRD_PARTY_LICENSES\.md",\s*"THIRD_PARTY_LICENSES\.txt"\s*\]\s*$', content)
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
    assert '"Dependency and License References" = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert "[project.optional-dependencies]" in content
    assert 'addopts = "-ra -v --basetemp=.pytest_temp"' in content


def test_security_policy_invariants():
    """Verify bilingual security navigation and published reporting routes."""
    sec_path = PROJECT_ROOT / "SECURITY.md"
    assert sec_path.is_file(), "SECURITY.md missing"
    content = sec_path.read_text(encoding="utf-8")

    assert "## Deutsch" in content
    assert "## English" in content
    assert "[English](#english)" in content
    assert "[Deutsch](#deutsch)" in content
    version = _pyproject_version(PROJECT_ROOT / "pyproject.toml")
    assert version and f"`{version}`" in content
    assert "security@open-bricks.org" in content
    assert "security@dev-bricks.org" in content
    assert "security@ellmos.ai" in content
    assert "support@lukasgeiger.com" in content
    assert "lukas@open-bricks.org" in content
    assert "https://github.com/dev-bricks/WikiStub-Seed/security/advisories/new" in content


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
        assert "version-1.1.12" in content
        assert "dev--bricks" in content
        assert "open--bricks" in content
        assert "attribution-NOTICE" in content
        assert "marketing%20log" in content
        assert "flowchart TD" in content
        assert "sequenceDiagram" in content
        assert "autonumber" in content


def test_quick_navigation_anchors_and_parity():
    """Verify each bilingual navigation link resolves to a retained explicit section anchor."""
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")

    for filename, content in (("README.md", readme_en), ("README_de.md", readme_de)):
        navigation = content.split('<a id="sec-01"></a>', 1)[0]
        targets = re.findall(r"^- \[[^\]]+\]\(#([^)]+)\)", navigation, flags=re.MULTILINE)
        anchors = set(re.findall(r'<a id="([^"]+)"></a>', content))
        assert len(targets) == 18, f"Expected 18 navigation links in {filename}, found {len(targets)}"
        assert all(target in anchors for target in targets), f"Broken navigation fragment in {filename}"
        for index in range(1, 19):
            assert f"sec-{index:02d}" in anchors, f"Missing stable section anchor sec-{index:02d} in {filename}"

    # Verify backwards-compatibility anchors for historical links.
    assert '<a id="13-third-party-licenses--transparency"></a>' in readme_en
    assert '<a id="14-marketing--target-personas"></a>' in readme_en
    assert '<a id="13-drittanbieter-lizenzen--transparenz"></a>' in readme_de
    assert '<a id="14-marketing--zielgruppen"></a>' in readme_de


def test_readme_local_links_resolve():
    """Verify repository-relative documentation links point to files that ship in the source tree."""
    for filename in ("README.md", "README_de.md"):
        content = (PROJECT_ROOT / filename).read_text(encoding="utf-8")
        targets = re.findall(r"\[[^\]]*\]\(([^)]+)\)", content)
        for target in targets:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0].split("?", 1)[0]
            if relative:
                assert (PROJECT_ROOT / relative).exists(), f"Broken local link {target!r} in {filename}"


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
    """Verify the marketing log exists and is non-empty."""
    mlog_path = PROJECT_ROOT / "MARKETING-LOG.txt"
    assert mlog_path.is_file(), "MARKETING-LOG.txt missing"
    assert mlog_path.stat().st_size > 0, "MARKETING-LOG.txt is empty"


def test_dependency_reference_files_and_links():
    """Verify dependency notes link to their real local source and attribution files."""
    for filename in ("THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"):
        path = PROJECT_ROOT / filename
        assert path.is_file(), f"{filename} missing"
        content = path.read_text(encoding="utf-8")
        for source in ("pyproject.toml", "requirements.txt", "requirements-dev.txt"):
            assert source in content, f"{filename} does not identify {source}"
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0].split("?", 1)[0]
            if relative:
                assert (PROJECT_ROOT / relative).exists(), f"Broken local link {target!r} in {filename}"


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


def test_notice_attribution_file():
    """Verify NOTICE file exists and references project, organization, umbrella and third-party licenses."""
    notice_path = PROJECT_ROOT / "NOTICE"
    assert notice_path.is_file(), "NOTICE file missing"
    content = notice_path.read_text(encoding="utf-8")

    assert "WikiStub-Seed" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content
    assert "MIT License" in content
    assert "THIRD_PARTY_LICENSES.md" in content


def test_ci_welcome_and_stale_concurrency():
    """Verify welcome.yml and stale.yml have concurrency groups and cancel-in-progress configured."""
    for wfname in ["welcome.yml", "stale.yml"]:
        wf_path = PROJECT_ROOT / ".github" / "workflows" / wfname
        assert wf_path.is_file(), f"{wfname} missing"
        content = wf_path.read_text(encoding="utf-8")
        assert "concurrency:" in content, f"concurrency missing in {wfname}"
        assert "cancel-in-progress: true" in content, f"cancel-in-progress missing in {wfname}"


def test_gitignore_cloud_sync_and_canonical_locks():
    """Verify .gitignore contains comprehensive multi-host, cloud-sync, canonical lock, and cache guards."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    assert gitignore_path.is_file(), ".gitignore missing"
    content = gitignore_path.read_text(encoding="utf-8")

    required_patterns = [
        "*conflicted copy*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        "*-MacBook*",
        "LOCK.user.*",
        "LOCK.until.*",
        "LOCK.condition.*",
        ".automation-lock",
        "uv.lock",
        ".pytest_temp/",
        ".turbo/",
        ".tox/",
    ]
    for pattern in required_patterns:
        assert pattern in content, f"Missing pattern '{pattern}' in .gitignore"


def test_pyproject_notice_url_and_pytest_options():
    """Verify PEP 621 Notice URL and hardened pytest options are configured in pyproject.toml."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"
    content = pyproject_path.read_text(encoding="utf-8")

    assert 'Notice = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/NOTICE"' in content
    assert 'minversion = "7.0"' in content
    assert "norecursedirs" in content


def test_changelog_unreleased_section():
    """Verify CHANGELOG.md keeps the conventional unreleased section at its head."""
    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    assert changelog_path.is_file(), "CHANGELOG.md missing"
    headings = [line for line in changelog_path.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
    assert headings and headings[0] == "## [Unreleased]"


def test_sec_dual_html_anchors_parity():
    """Verify canonical <a id="sec-01"></a> through <a id="sec-18"></a> exist in both READMEs."""
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in readme_en, f"Missing anchor {anchor} in README.md"
        assert anchor in readme_de, f"Missing anchor {anchor} in README_de.md"


def test_umlaut_purity_in_markdown():
    """Verify German end-user passages across the multilingual READMEs use real umlauts."""
    for fname in ["README.md", "README_de.md", "README_es.md", "README_ja.md", "README_ru.md", "README_zh-Hans.md"]:
        content = (PROJECT_ROOT / fname).read_text(encoding="utf-8")
        assert "fuer" not in content, f"Found ASCII escape 'fuer' in {fname}"
        assert "Domaenen" not in content, f"Found ASCII escape 'Domaenen' in {fname}"

    mlog_content = (PROJECT_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "fuer" not in mlog_content, "Found ASCII escape 'fuer' in MARKETING-LOG.txt"
    assert "Domaenen" not in mlog_content, "Found ASCII escape 'Domaenen' in MARKETING-LOG.txt"


def test_ci_lifecycle_auto_assign_and_label_sync():
    """Verify auto-assign.yml, label-sync.yml and labels.yml exist with correct permissions and timeouts."""
    auto_assign = PROJECT_ROOT / ".github" / "workflows" / "auto-assign.yml"
    assert auto_assign.is_file(), "auto-assign.yml missing"
    aa_content = auto_assign.read_text(encoding="utf-8")
    assert "pull-requests: write" in aa_content
    assert "issues: write" in aa_content
    assert "timeout-minutes: 5" in aa_content
    assert "cancel-in-progress: true" in aa_content

    label_sync = PROJECT_ROOT / ".github" / "workflows" / "label-sync.yml"
    assert label_sync.is_file(), "label-sync.yml missing"
    ls_content = label_sync.read_text(encoding="utf-8")
    assert "issues: write" in ls_content
    assert "timeout-minutes: 5" in ls_content
    assert "cancel-in-progress: true" in ls_content

    labels_yml = PROJECT_ROOT / ".github" / "labels.yml"
    assert labels_yml.is_file(), "labels.yml missing"
    labels_content = labels_yml.read_text(encoding="utf-8")
    for expected_label in ["bug", "enhancement", "good first issue", "help wanted", "documentation", "duplicate", "wontfix", "priority: high", "priority: low", "needs-triage", "stale"]:
        assert f"name: {expected_label}" in labels_content or f"name: '{expected_label}'" in labels_content


def test_gitignore_multi_host_and_agent_locks():
    """Verify .gitignore includes IDEAPAD, WORKSTATION wildcards, Desktop.ini, and agent lock patterns."""
    gitignore_path = PROJECT_ROOT / ".gitignore"
    assert gitignore_path.is_file()
    content = gitignore_path.read_text(encoding="utf-8")

    patterns = [
        "*-IDEAPAD*",
        "*-IDEAPAD-GEI*",
        "*_WORKSTATION*",
        "*_WORKSTATION-LG*",
        "Desktop.ini",
        "TASKPLAN_*.md",
        "LOCK.dev.*",
        "LOCK.antigravity.*",
        "LOCK.bugsearch.*",
        ".pytest_tmp*/",
    ]
    for p in patterns:
        assert p in content, f"Pattern {p} missing in .gitignore"


def test_pep621_extended_project_urls():
    """Verify pyproject.toml defines contributing and bounded dependency/license reference URLs."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    content = pyproject_path.read_text(encoding="utf-8")

    assert 'Contributing = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/CONTRIBUTING.md"' in content
    assert '"Plain-Text License" = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/LICENSE"' in content
    assert '"Third-Party Licenses (Text)" = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert '"Dependency and License References" = "https://github.com/dev-bricks/WikiStub-Seed/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert '--basetemp=.pytest_temp' in content


def test_contributing_guide_quality_gates():
    """Verify the contributor guide names runnable checks and matches the frozen package version."""
    contrib_path = PROJECT_ROOT / "CONTRIBUTING.md"
    assert contrib_path.is_file()
    content = contrib_path.read_text(encoding="utf-8")

    assert "python -m pytest" in content
    assert "ruff check ." in content
    assert "python wikistub_seed_cli.py check" in content
    version = _pyproject_version(PROJECT_ROOT / "pyproject.toml")
    assert version and f"`{version}`" in content


def test_marketing_log_pfad_a_20261001():
    """Verify MARKETING-LOG.txt contains the 2026-10-01 Pfad A action tracking entry."""
    mlog_path = PROJECT_ROOT / "MARKETING-LOG.txt"
    assert mlog_path.is_file()
    content = mlog_path.read_text(encoding="utf-8")

    assert "2026-10-01" in content
    assert "[GITHUBBOT_ONE_REPO_CLEANER]" in content
    assert "PFAD_A_HYGIENE" in content


def test_marketing_log_pfad_b_20261003():
    """Verify MARKETING-LOG.txt contains the 2026-10-03 Pfad B action tracking entry."""
    mlog_path = PROJECT_ROOT / "MARKETING-LOG.txt"
    assert mlog_path.is_file()
    content = mlog_path.read_text(encoding="utf-8")

    assert "2026-10-03" in content
    assert "[GITHUBBOT_ONE_REPO_MARKETING_AND_DESIGN]" in content
    assert "PFAD_B_UPGRADE" in content


def test_all_readme_international_badge_parity():
    """Verify modern badge parity across all six language editions (EN, DE, ES, JA, RU, ZH)."""
    readme_files = [
        "README.md",
        "README_de.md",
        "README_es.md",
        "README_ja.md",
        "README_ru.md",
        "README_zh-Hans.md",
    ]
    for rname in readme_files:
        rpath = PROJECT_ROOT / rname
        assert rpath.is_file(), f"{rname} is missing"
        content = rpath.read_text(encoding="utf-8")
        assert "version-1.1.12" in content, f"version badge missing in {rname}"
        assert "dev--bricks" in content, f"dev-bricks ecosystem badge missing in {rname}"
        assert "open--bricks" in content, f"open-bricks umbrella badge missing in {rname}"
