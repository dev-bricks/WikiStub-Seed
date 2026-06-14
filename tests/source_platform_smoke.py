import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
    )


class SourcePlatformSmokeTests(unittest.TestCase):
    def test_cli_check_runs_successfully(self) -> None:
        result = run_command("wikistub_seed_cli.py", "check")

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "wikistub_seed_cli.py check failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            ),
        )
        self.assertIn("WikiStub-Seed: Konsistenzprüfung", result.stdout)
        self.assertIn("Exakte Duplikate:", result.stdout)

    def test_pipeline_validate_runs_successfully(self) -> None:
        result = run_command("wikistub_seed_pipeline.py", "validate")

        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "wikistub_seed_pipeline.py validate failed.\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            ),
        )
        self.assertIn("VALIDIERUNG", result.stdout)
        self.assertIn("Gültig:", result.stdout)
        self.assertIn("Duplikate:", result.stdout)


if __name__ == "__main__":
    unittest.main()
