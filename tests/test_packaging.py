from __future__ import annotations

import fnmatch
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import venv
import zipfile
from os import walk
from pathlib import Path, PurePosixPath
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
WHEEL_MODULES = {
    "data_policy.py",
    "language_model.py",
    "safe_io.py",
    "translate.py",
    "wiki_auth.py",
    "wiki_store.py",
}


def _copy_git_snapshot(destination: Path) -> None:
    """Copy a git snapshot or bounded public sdist tree, without private files."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            capture_output=True,
        )
    except FileNotFoundError:
        result = None
    if result is not None and result.returncode == 0:
        paths = [Path(os.fsdecode(raw_path)) for raw_path in result.stdout.split(b"\0") if raw_path]
    else:
        # A source archive has no .git metadata. Only accept the generated,
        # public sdist shape; refuse to scan arbitrary git-less directories.
        if not (ROOT / "PKG-INFO").is_file() or not (ROOT / "pyproject.toml").is_file():
            raise RuntimeError("git metadata is unavailable and this is not a setuptools sdist")
        excluded_dirs = {
            ".git", ".githubbot", ".sync", "_aftercare", "_archive", "_private",
            "_user", "keyring", "__pycache__", ".pytest_cache", ".pytest_temp",
            ".ruff_cache", ".venv", "venv", "build", "dist", "node_modules",
        }
        excluded_names = {
            "pkg-info", "wiki_auth.json", "wikistub_seed_trash.json",
            "credentials.json", "token.json", "gates.md", "lock.txt", ".automation-lock",
        }
        excluded_patterns = (
            "LOCK.*", "LOCK*.txt", "*.team-lock*", "*.lock", "client_secret*.json",
            "secrets.*", "*.pem", "*.key", ".env", ".env.*", "*.pyc", "*.pyo",
            "*.egg-info",
        )
        paths = []
        for current, directories, filenames in walk(ROOT):
            directories[:] = [
                name for name in directories
                if name.casefold() not in excluded_dirs and not name.casefold().endswith(".egg-info")
            ]
            current_path = Path(current)
            for name in filenames:
                if name.casefold() in excluded_names or any(fnmatch.fnmatch(name, pattern) for pattern in excluded_patterns):
                    continue
                paths.append((current_path / name).relative_to(ROOT))

    for relative in paths:
        source = ROOT / relative
        if not source.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


class DistributionSmokeTests(unittest.TestCase):
    maxDiff = None

    def test_gitless_sdist_snapshot_fallback_is_bounded(self):
        with tempfile.TemporaryDirectory(prefix="wikistub-sdist-fallback-") as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            (root / "PKG-INFO").write_text("Metadata-Version: 2.1\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[build-system]\n", encoding="utf-8")
            (root / "README.md").write_text("public source", encoding="utf-8")
            private = root / ".GITHUBBOT" / "logs"
            private.mkdir(parents=True)
            (private / "EXECUTION.md").write_text("private marker", encoding="utf-8")
            (root / "wiki_auth.json").write_text("synthetic secret", encoding="utf-8")
            destination = Path(tmp) / "copy"
            destination.mkdir()

            with patch(__name__ + ".ROOT", root), patch("subprocess.run", side_effect=FileNotFoundError("git")):
                _copy_git_snapshot(destination)

            self.assertEqual((destination / "README.md").read_text(encoding="utf-8"), "public source")
            self.assertFalse((destination / ".GITHUBBOT").exists())
            self.assertFalse((destination / "wiki_auth.json").exists())
            self.assertFalse((destination / "PKG-INFO").exists())

    def test_wheel_sdist_and_installed_api_are_real_and_contained(self):
        with tempfile.TemporaryDirectory(prefix="wikistub-package-smoke-") as tmp:
            temporary = Path(tmp)
            source = temporary / "source"
            source.mkdir()
            _copy_git_snapshot(source)

            # Verify manifest exclusions against synthetic private artifacts,
            # without reading any real credential, guard, or care-log file.
            synthetic_private = {
                "LOCK.team.synthetic.IDEAPAD-GEI.txt": "synthetic lock marker",
                "GATES.md": "synthetic guard marker",
                "wiki_auth.json": '{"password_hash":"synthetic-secret"}',
                ".GITHUBBOT/logs/EXECUTION.md": "synthetic private receipt",
                "_aftercare/notes.md": "synthetic private note",
            }
            for relative, contents in synthetic_private.items():
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")

            source_artifacts = temporary / "source-artifacts"
            source_artifacts.mkdir()
            source_build = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--sdist",
                    "--outdir",
                    str(source_artifacts),
                    str(source),
                ],
                cwd=temporary,
                capture_output=True,
                text=True,
                timeout=300,
            )
            self.assertEqual(
                source_build.returncode,
                0,
                f"sdist build failed:\n{source_build.stdout}\n{source_build.stderr}",
            )
            source_archives = list(source_artifacts.glob("*.tar.gz"))
            self.assertEqual(len(source_archives), 1, source_build.stdout + source_build.stderr)

            extracted_root = temporary / "extracted-sdist"
            extracted_root.mkdir()
            with tarfile.open(source_archives[0], "r:gz") as archive:
                sdist_names = {name.replace("\\", "/") for name in archive.getnames()}
                if sys.version_info >= (3, 12):
                    archive.extractall(extracted_root, filter="data")
                else:
                    archive.extractall(extracted_root)
            for required in (
                "README.md",
                "README_de.md",
                "README_es.md",
                "README_ja.md",
                "README_ru.md",
                "README_zh-Hans.md",
                "pyproject.toml",
                "wikistub_seed.json",
                "assets/banner.svg",
                "locales/translations.json",
                "web_publisher/index.html",
                "web_publisher/data/wikistub_seed.json",
                "web_publisher/tests/publisher.test.mjs",
                "tests/test_packaging.py",
                ".github/workflows/tests.yml",
                "01_Mathematik/Statistik/Varianz.md",
            ):
                self.assertTrue(
                    any(name.endswith("/" + required) for name in sdist_names),
                    f"sdist is missing {required}",
                )

            extracted_roots = list(extracted_root.iterdir())
            self.assertEqual(len(extracted_roots), 1)
            extracted_source = extracted_roots[0]
            wheel_artifacts = temporary / "sdist-built-wheel"
            wheel_artifacts.mkdir()
            wheel_build = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--wheel",
                    "--outdir",
                    str(wheel_artifacts),
                    str(extracted_source),
                ],
                cwd=temporary,
                capture_output=True,
                text=True,
                timeout=300,
            )
            self.assertEqual(
                wheel_build.returncode,
                0,
                f"wheel build from sdist failed:\n{wheel_build.stdout}\n{wheel_build.stderr}",
            )
            wheels = list(wheel_artifacts.glob("*.whl"))
            self.assertEqual(len(wheels), 1, wheel_build.stdout + wheel_build.stderr)
            wheel = wheels[0]

            with zipfile.ZipFile(wheel) as archive:
                wheel_names = set(archive.namelist())
                top_level_python = {
                    PurePosixPath(name).name
                    for name in wheel_names
                    if "/" not in name and name.endswith(".py")
                }
                self.assertEqual(top_level_python, WHEEL_MODULES)
                for excluded in (
                    "wikistub_seed.json",
                    "wiki_auth.json",
                    "wikistub_seed_trash.json",
                    "wikistub_seed_cli.py",
                    "wikistub_seed_pipeline.py",
                    "edit_server.py",
                ):
                    self.assertNotIn(excluded, wheel_names)
                self.assertFalse(any(name.startswith("web_publisher/") for name in wheel_names))
                self.assertFalse(any(name.startswith("assets/") for name in wheel_names))
            lowered_names = {name.lower() for name in sdist_names}
            for marker in (
                "lock.team.synthetic.ideapad-gei.txt",
                "gates.md",
                "wiki_auth.json",
                ".githubbot/",
                "_aftercare/",
            ):
                self.assertFalse(any(marker in name for name in lowered_names), marker)

            install = temporary / "venv"
            venv.EnvBuilder(with_pip=True).create(install)
            python = install / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            pip_result = subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-index",
                    "--no-deps",
                    str(wheel),
                ],
                cwd=temporary,
                capture_output=True,
                text=True,
                timeout=180,
            )
            self.assertEqual(
                pip_result.returncode,
                0,
                f"wheel installation failed:\n{pip_result.stdout}\n{pip_result.stderr}",
            )

            runner = temporary / "outside-worktree"
            runner.mkdir()
            script = r'''
import os
import sys
from pathlib import Path
import data_policy, language_model, safe_io, translate, wiki_auth, wiki_store

source = Path(sys.argv[1]).resolve()
package_dir = Path(wiki_store.__file__).resolve().parent
assert all(Path(module.__file__).resolve().parent == package_dir for module in (
    data_policy, language_model, safe_io, translate, wiki_auth, wiki_store
))
assert str(source).casefold() not in {str(Path(item).resolve()).casefold() for item in sys.path if item}
assert not (package_dir / "wikistub_seed.json").exists()
before = set(package_dir.iterdir())

for operation, expected_error in (
    (lambda: wiki_store.load(), wiki_store.StoragePathRequiredError),
    (lambda: wiki_store.save({"MetaWiki": {}}), wiki_store.StoragePathRequiredError),
    (lambda: wiki_store.list_trash(), wiki_store.StoragePathRequiredError),
    (lambda: wiki_auth.load_auth(), RuntimeError),
    (lambda: wiki_auth.set_password("synthetic"), RuntimeError),
):
    try:
        operation()
    except expected_error:
        pass
    else:
        raise AssertionError("installed defaults must require explicit data paths")

for operation, expected_error in (
    (lambda: wiki_store.save({"MetaWiki": {}}, package_dir / "must-not-write.json"), wiki_store.StoragePathRequiredError),
    (lambda: wiki_auth.load_auth(package_dir / "must-not-read.json"), RuntimeError),
):
    try:
        operation()
    except expected_error:
        pass
    else:
        raise AssertionError("site-packages must not be used as a data directory")

external = Path(sys.argv[2]) / "external-data"
external.mkdir()
dataset = external / "wiki.json"
trash = external / "trash.json"
data = {"MetaWiki": {"Category": {"Subcategory": []}}}
wiki_store.save(data, dataset)
data = wiki_store.load(dataset)
entry = wiki_store.create_entry(data, "Category", "Subcategory", {
    "title": "Synthetic note", "definition_de": "Beispiel", "definition_en": "Example"
})
assert entry["title"] == "Synthetic note"
wiki_store.save(data, dataset)
wiki_store.delete_entry(data, "Category", "Subcategory", "Synthetic note", trash)
wiki_store.save(data, dataset)
assert len(wiki_store.list_trash(trash)) == 1
assert wiki_store.load(dataset)["MetaWiki"]["Category"]["Subcategory"] == []

auth_path = external / "auth.json"
record = wiki_auth.set_password("synthetic password", path=auth_path)
assert wiki_auth.verify_password("synthetic password", wiki_auth.load_auth(auth_path))
wiki_auth.set_anonymous_permissions({"edit": False}, path=auth_path, existing=record)
assert wiki_auth.compute_permissions(wiki_auth.load_auth(auth_path), authenticated=False)["edit"] is False
assert set(package_dir.iterdir()) == before, "data or bytecode was written inside site-packages"
'''
            environment = os.environ.copy()
            environment["PYTHONPATH"] = str(source)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            smoke = subprocess.run(
                [str(python), "-I", "-c", script, str(source), str(temporary)],
                cwd=runner,
                env=environment,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                smoke.returncode,
                0,
                f"installed API smoke failed:\n{smoke.stdout}\n{smoke.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
