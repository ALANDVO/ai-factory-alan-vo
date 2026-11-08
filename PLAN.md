# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

continue-implementation

## Roadmap

### test-fix-and-version-sync — Fix version test and sync versions across project

Status: done

Acceptance:
- Version test in tests/test_factory.py reads dynamically from VERSION file via factory.get_version()
- pyproject.toml version matches VERSION file (1.2.0)
- Frontend package.json version matches VERSION file (1.2.0)
- pytest configuration supports asyncio_mode = "auto" for backend async tests
- All 45 Python tests pass (31 factory + 14 backend, 2 skipped)
- All 4 frontend tests pass

Implementation: `tests/test_factory.py`, `pyproject.toml`, `frontend/package.json`, `CHANGELOG.md`, `PLAN.md`, `STATUS.md`

Tests: `tests/test_factory.py::TestVersion::test_version_flag_prints_version`, `backend/tests/test_api.py`

### version-sync-complete — Complete version sync across all project files

Status: done

Acceptance:
- pyproject.toml version matches VERSION file (1.3.0)
- Frontend package.json version matches VERSION file (1.3.0)
- All tests pass with synced versions

Implementation: `pyproject.toml`, `frontend/package.json`

Tests: `tests/test_factory.py`, `backend/tests/test_api.py`, `frontend tests`

### continue-implementation — Continue implementation and resolve known failures

Status: done

Acceptance:
- Run checks, fix failures, and implement the next planned feature
- Fixed FastAPI/Starlette version incompatibility (APIRouter on_startup error)
- Synced versions across all project files (1.4.0)
- Backend health/root endpoints use dynamic version from VERSION file
- All 49 tests pass (31 factory + 14 backend + 4 frontend)

Implementation: `backend/requirements.txt`, `backend/app/api/routes.py`, `backend/app/core/config.py`, `backend/tests/test_api.py`, `pyproject.toml`, `frontend/package.json`

Tests: `tests/test_factory.py`, `backend/tests/test_api.py`, `frontend tests`

### docker-compose-integration — Full docker-compose stack with backend, frontend, and database

Status: planned

Acceptance:
- docker-compose.yml builds and runs backend, frontend, and PostgreSQL
- Health endpoints respond on all services
- Frontend proxies API calls to backend

### github-actions-ci — CI/CD pipeline for automated testing and deployment

Status: planned

Acceptance:
- GitHub Actions workflow runs on push/PR
- Runs Python tests, frontend tests, and lint
- Builds Docker images

### frontend-dashboard-enhancements — Dashboard UI improvements

Status: planned

Acceptance:
- Real-time build status updates
- App template browser with search/filter
- Build history visualization

### api-authentication — API authentication and authorization

Status: planned

Acceptance:
- JWT-based authentication for API endpoints
- Role-based access control (admin, user)
- Protected routes for build/cycle/clean operations

---

Alan Vo · [alanvo.net](https://alanvo.net) · [X: @alanvoasi](https://x.com/alanvoasi)
