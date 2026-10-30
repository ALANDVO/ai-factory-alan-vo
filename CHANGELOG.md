# Changelog

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [1.2.0] - 2026-10-30

### Fixed
- Version test in `tests/test_factory.py` now reads version dynamically from VERSION file via `factory.get_version()` instead of hardcoded "1.1.0"
- pytest configuration updated with `asyncio_mode = "auto"` and backend tests path for proper async test support

### Changed
- Updated pyproject.toml version to 1.2.0 (matches VERSION file)
- Backend API tests now run correctly with pytest-asyncio

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## Unreleased

### Fixed
- `.gitignore` now excludes `.venv/`, `node_modules/`, `dist/`, databases, egg-info, bytecode, and local agent metadata. Those paths were removed from the git index so a virtualenv is not published.
- Env examples no longer contain a token-shaped placeholder. `GITHUB_TOKEN` is blank.
- One catalog prompt no longer uses an unfinished-work marker that the local checklist treated as incomplete code.

### Changed
- README states the deterministic catalog workflow, the `ai-factory --list` check (31 templates on 2026-10-14), and that the browser console is unfinished.
- Default pytest path stays `tests/`. The unfinished API tests are not collected. Cycle and clean API tests are skipped because they can push to GitHub or delete `~/ai-factory` state.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [1.1.0] - 2026-10-14

### Added
- `--clean` CLI flag to remove local build artifacts and state (repos directory, state.json, pushed.log)
  with informative output about what was removed
- `--version` CLI flag to display version from VERSION file and exit early

### Fixed
- SyntaxWarning invalid escape sequences in `appdefs_batch3.py` by making triple-quoted code templates raw strings
- `.gitignore` now excludes `.venv/` directory

### Changed
- Updated feature-plan.json and PLAN.md to mark completed features

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## [0.4.0] - 2026-10-14

### Added
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running pytest and lint on push/PR
- Uses ubuntu-latest runner, no paid services or custom runners
- Build job verifies CLI works and package builds correctly

### Changed
- Updated feature-plan.json and PLAN.md to mark github-actions-ci as complete

## [0.3.0] - 2026-10-14

### Added
- `gen_portfolio_json()` function in `factory.py` generating portfolio.json for each app
- `portfolio.json` included in all generated apps (both new builds and updates)
- Schema-compliant portfolio.json with: schema_version, name, owner, email, domain, workflows, auth, llm_providers, summary
- Domain auto-derived from app tech tags (Security, Cloud/Infrastructure, Data/Observability, AI/ML)
- Workflows derived from app features (minimum 3, padded with generics if needed)
- Summary extracted from first sentence of app description
- New test suite `tests/test_portfolio_json.py` with 7 tests covering:
  - Portfolio JSON structure and required fields
  - Domain derivation from tech tags
  - Workflow derivation from features
  - Padding for apps with fewer than 3 features
  - Summary extraction from description
  - Integration tests for build_app and build_app_into

### Changed
- `build_app()` now generates portfolio.json alongside standard files
- `build_app_into()` now generates portfolio.json during update cycle
## [0.2.0] - 2026-10-14

### Added
- CLI argument parsing with `argparse` in `factory.py`
- `--list` — show all 31 available apps with descriptions and feature counts
- `--app <name>` — build and push a specific app by name (without -alan-vo suffix)
- `--dry-run` — generate app files locally without pushing to GitHub
- `--update-only` — run update cycle only (skip new app creation)
- Help text with usage examples

### Changed
- `main()` now accepts optional `argv` parameter for testing

## [0.1.0] - 2026-10-14

### Added
- `pyproject.toml` with package metadata, dependencies, and pytest configuration
- Comprehensive test suite (`tests/test_factory.py`) with 29 unit tests covering:
  - State management (load/save/mark_pushed)
  - Repository naming convention
  - GitHub API helpers (mocked)
  - App definition loading from multiple modules
  - File generation helpers (README, LICENSE, Dockerfile, docker-compose, .env.example)
  - Build orchestration (build_app, build_app_into, main, clean_local)
- Editable installation via `pip install -e .`
- `README.md` with project overview, usage, architecture diagram, and configuration
- `LICENSE` (MIT)
- `.env.example` with required and optional environment variables

### Changed
- Tests now mock `factory.log` to avoid filesystem dependency on log directory

### Fixed
- TOML syntax error in `pyproject.toml` optional-dependencies section

## [0.0.1] - 2026-10-14 (pre-release)

### Added
- Core factory orchestration in `factory.py`
- App definitions across 6 modules (`appdefs.py`, `appdefs_batch2.py`, `appdefs_batch3.py`, `appdefs_cloud.py`, `appdefs_enterprise.py`)
- Shared generation helpers in `apps.py`
- Legacy entry point `gen.py`
- GitHub integration (repo creation, push, state tracking)
- Local cleanup after push
- 1-for-1 rotation: create new repos, then update oldest