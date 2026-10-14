"""Backend API tests."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app
from app.core.database import init_db, create_tables, close_db, get_session_dependency
from app.models.app_build import AppBuild, BuildStatus
from app.models.audit_log import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def app():
    """Create test app."""
    test_app = create_app()
    init_db()
    await create_tables()
    yield test_app
    await close_db()


@pytest.fixture
async def client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    """Get database session for tests."""
    async for session in get_session_dependency():
        yield session


class TestHealth:
    """Health check tests."""

    async def test_health_endpoint(self, client):
        """Health endpoint returns ok."""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.1.0"

    async def test_root_endpoint(self, client):
        """Root endpoint returns app info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ai-factory"
        assert data["version"] == "1.1.0"


class TestAppsAPI:
    """Apps API tests."""

    async def test_list_apps(self, client):
        """List apps returns available templates."""
        response = await client.get("/api/v1/apps")
        assert response.status_code == 200
        data = response.json()
        assert "apps" in data
        assert "total" in data
        assert isinstance(data["apps"], list)
        assert data["total"] > 0
        # Verify app structure
        if data["apps"]:
            app = data["apps"][0]
            assert "name" in app
            assert "description" in app
            assert "features" in app
            assert "tech" in app
            assert "api_key" in app

    async def test_get_app(self, client):
        """Get specific app by name."""
        # First get list to find a valid name
        list_resp = await client.get("/api/v1/apps")
        apps = list_resp.json()["apps"]
        if apps:
            app_name = apps[0]["name"]
            response = await client.get(f"/api/v1/apps/{app_name}")
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == app_name

    async def test_get_nonexistent_app(self, client):
        """Get nonexistent app returns 404."""
        response = await client.get("/api/v1/apps/nonexistent-app")
        assert response.status_code == 404


class TestDryRunAPI:
    """Dry run API tests."""

    async def test_dry_run_existing_app(self, client):
        """Dry run for existing app."""
        list_resp = await client.get("/api/v1/apps")
        apps = list_resp.json()["apps"]
        if apps:
            app_name = apps[0]["name"]
            response = await client.post(f"/api/v1/apps/{app_name}/dry-run")
            assert response.status_code == 200
            data = response.json()
            assert "app_name" in data
            assert "output" in data
            assert data["app_name"] == app_name

    async def test_dry_run_nonexistent_app(self, client):
        """Dry run for nonexistent app returns 404."""
        response = await client.post("/api/v1/apps/nonexistent/dry-run")
        assert response.status_code == 404


class TestBuildsAPI:
    """Builds API tests."""

    async def test_get_build_history_empty(self, client):
        """Get build history returns empty list initially."""
        response = await client.get("/api/v1/builds")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)

    async def test_get_build_history_pagination(self, client):
        """Get build history with pagination."""
        response = await client.get("/api/v1/builds?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0


class TestAuditAPI:
    """Audit log API tests."""

    async def test_get_audit_logs_empty(self, client):
        """Get audit logs returns empty list initially."""
        response = await client.get("/api/v1/audit")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    async def test_get_audit_logs_pagination(self, client):
        """Get audit logs with pagination."""
        response = await client.get("/api/v1/audit?limit=50&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 50
        assert data["offset"] == 0


class TestCycleAPI:
    """Factory cycle API tests."""

    @pytest.mark.skip(reason="Calls the real factory cycle, which can create and push a GitHub repository")
    async def test_run_cycle(self, client):
        """Run factory cycle."""
        response = await client.post("/api/v1/cycle")
        # May succeed or fail depending on GitHub token, but should not crash
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestCleanAPI:
    """Clean API tests."""

    @pytest.mark.skip(reason="clean_all deletes the operator BASE, STATE, and LOG paths under the home directory")
    async def test_clean_artifacts(self, client):
        """Clean local artifacts."""
        response = await client.post("/api/v1/clean")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cleaned"


class TestDatabaseModels:
    """Database model tests."""

    async def test_app_build_creation(self, db_session: AsyncSession):
        """Create and query AppBuild."""
        build = AppBuild(
            app_name="test-app",
            repo_name="test-app-alan-vo",
            status=BuildStatus.COMPLETED,
            is_update=False,
            github_url="https://github.com/ALANDVO/test-app-alan-vo",
            commit_sha="abc123",
        )
        db_session.add(build)
        await db_session.commit()
        await db_session.refresh(build)

        assert build.id is not None
        assert build.app_name == "test-app"
        assert build.status == BuildStatus.COMPLETED

    async def test_audit_log_creation(self, db_session: AsyncSession):
        """Create and query AuditLog."""
        log = AuditLog(
            action="build_start",
            resource_type="app_build",
            resource_id="1",
            details="Test build started",
            success=True,
        )
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)

        assert log.id is not None
        assert log.action == "build_start"
        assert log.success is True

    async def test_build_status_enum(self):
        """BuildStatus enum values."""
        assert BuildStatus.PENDING == "pending"
        assert BuildStatus.BUILDING == "building"
        assert BuildStatus.PUSHING == "pushing"
        assert BuildStatus.COMPLETED == "completed"
        assert BuildStatus.FAILED == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])