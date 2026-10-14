"""Publish-index rules: local environments and generated files stay out of git."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATTERNS = (
    ".venv/",
    "node_modules/",
    "dist/",
    "__pycache__/",
    ".env",
    "*.db",
    "*.sqlite",
    "*.egg-info/",
    ".antigravitycli/",
    ".omp/",
)

IGNORED_SAMPLES = (
    ".venv/bin/Activate.ps1",
    "frontend/node_modules/react/index.js",
    "frontend/dist/index.html",
    "backend/__pycache__/main.cpython-312.pyc",
    ".env",
    "ai_factory.db",
    "backend/ai_factory.db",
    "state.sqlite",
    "ai_factory.egg-info/PKG-INFO",
    ".antigravitycli/session.json",
    ".omp/state.json",
)


def _check_ignore(*paths: str) -> tuple[int, set[str]]:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-v", *paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    ignored = set()
    for line in result.stdout.splitlines():
        if "\t" in line:
            ignored.add(line.split("\t", 1)[1])
    return result.returncode, ignored


def test_gitignore_lists_local_artifact_patterns():
    """The factory repo ignore file names every local artifact class."""
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    patterns = {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    missing = [pattern for pattern in REQUIRED_PATTERNS if pattern not in patterns]
    assert missing == []


def test_git_ignores_venv_dependencies_and_databases():
    """Git ignore rules match virtualenv, dependency, database, and metadata paths."""
    code, ignored = _check_ignore(*IGNORED_SAMPLES)
    assert code == 0
    assert ignored == set(IGNORED_SAMPLES)


def test_env_example_stays_publishable():
    """The blank env template is a source file, so git must not ignore it."""
    code, ignored = _check_ignore(".env.example")
    assert code == 1
    assert ignored == set()


def test_index_does_not_track_venv_or_egg_info():
    """The index must not publish a virtualenv or setuptools metadata."""
    result = subprocess.run(
        ["git", "ls-files", "--", ".venv", "ai_factory.egg-info"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ""
