"""Service layer wrapping the ai-factory CLI logic for API use."""
import os
import sys
import json
import shutil
import subprocess
import datetime
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# Add project root to path for appdefs imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import factory
from app.models.app_build import AppBuild, BuildStatus
from app.models.audit_log import AuditLog
from app.core.database import get_session


@dataclass
class BuildResult:
    """Result of a build operation."""
    success: bool
    app_name: str
    repo_name: str
    error_message: Optional[str] = None
    github_url: Optional[str] = None
    commit_sha: Optional[str] = None


class FactoryService:
    """Service for managing app factory operations."""

    def __init__(self):
        self.settings = factory.get_settings() if hasattr(factory, 'get_settings') else None
        # Use factory module's configuration
        self.gh_token = os.environ.get("GITHUB_TOKEN", "")
        self.gh_user = os.environ.get("GH_USER", "ALANDVO")
        self.email = os.environ.get("EMAIL", "alanvo@gmail.com")
        self.base_dir = Path(os.environ.get("BASE", "~/ai-factory/repos")).expanduser()
        self.log_file = Path(os.environ.get("LOG", "~/ai-factory/pushed.log")).expanduser()
        self.state_file = Path(os.environ.get("STATE", "~/ai-factory/state.json")).expanduser()

    async def list_apps(self) -> List[Dict[str, Any]]:
        """List all available app definitions."""
        apps = factory.load_all_apps()
        return [
            {
                "name": app["name"],
                "description": app["desc"],
                "features": app["features"],
                "tech": app["tech"],
                "api_key": app["api_key"],
            }
            for app in apps
        ]

    async def get_app(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific app definition by name (API format)."""
        apps = factory.load_all_apps()
        for app in apps:
            if app["name"] == app_name:
                return {
                    "name": app["name"],
                    "description": app["desc"],
                    "features": app["features"],
                    "tech": app["tech"],
                    "api_key": app["api_key"],
                }
        return None

    def _get_raw_app(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get raw app definition for factory operations."""
        apps = factory.load_all_apps()
        for app in apps:
            if app["name"] == app_name:
                return app
        return None

    async def dry_run(self, app_name: str) -> Dict[str, Any]:
        """Generate app files locally without pushing."""
        app_def = self._get_raw_app(app_name)
        if not app_def:
            raise ValueError(f"App '{app_name}' not found")

        # Capture the dry-run output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            factory.run_dry_run(app_def)

        output = f.getvalue()
        return {
            "app_name": app_name,
            "output": output,
        }

    async def build_and_push(self, app_name: str, is_update: bool = False) -> BuildResult:
        """Build and push an app to GitHub."""
        app_def = self._get_raw_app(app_name)
        if not app_def:
            raise ValueError(f"App '{app_name}' not found")

        repo_name = factory.repo_name(app_name)

        # Create audit log entry
        async with get_session() as session:
            build_record = AppBuild(
                app_name=app_name,
                repo_name=repo_name,
                status=BuildStatus.BUILDING,
                is_update=is_update,
            )
            session.add(build_record)
            await session.flush()
            build_id = build_record.id

            audit = AuditLog(
                action="build_start",
                resource_type="app_build",
                resource_id=str(build_id),
                details=f"Started {'update' if is_update else 'build'} for {app_name}",
            )
            session.add(audit)
            await session.commit()

        try:
            if is_update:
                # For updates, we need the existing repo entry
                state = factory.load_state()
                repo_entry = next((r for r in state["repos"] if r["name"] == repo_name), None)
                if not repo_entry:
                    raise ValueError(f"Repo {repo_name} not found in state for update")

                # Run update cycle
                all_apps = factory.load_all_apps()
                factory.update_repo(repo_entry, all_apps)
            else:
                # Build new app
                build_dir, _ = factory.build_app(app_def)

                # Push to GitHub
                ok, err = factory.push(build_dir, repo_name)
                if not ok:
                    raise RuntimeError(f"Push failed: {err}")

                # Mark as pushed
                factory.mark_pushed(repo_name, is_update=False)
                factory.clean_local(repo_name)

                # Get commit SHA from the repo
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                )
                commit_sha = result.stdout.strip() if result.returncode == 0 else None

            github_url = f"https://github.com/{self.gh_user}/{repo_name}"

            # Update build record
            async with get_session() as session:
                build_record = await session.get(AppBuild, build_id)
                if build_record:
                    build_record.status = BuildStatus.COMPLETED
                    build_record.github_url = github_url
                    build_record.commit_sha = commit_sha

                audit = AuditLog(
                    action="build_complete",
                    resource_type="app_build",
                    resource_id=str(build_id),
                    details=f"Completed {'update' if is_update else 'build'} for {app_name}",
                    success=True,
                )
                session.add(audit)
                await session.commit()

            return BuildResult(
                success=True,
                app_name=app_name,
                repo_name=repo_name,
                github_url=github_url,
                commit_sha=commit_sha,
            )

        except Exception as e:
            # Update build record with failure
            async with get_session() as session:
                build_record = await session.get(AppBuild, build_id)
                if build_record:
                    build_record.status = BuildStatus.FAILED
                    build_record.error_message = str(e)

                audit = AuditLog(
                    action="build_failed",
                    resource_type="app_build",
                    resource_id=str(build_id),
                    details=f"Failed {'update' if is_update else 'build'} for {app_name}: {e}",
                    success=False,
                    error_message=str(e),
                )
                session.add(audit)
                await session.commit()

            return BuildResult(
                success=False,
                app_name=app_name,
                repo_name=repo_name,
                error_message=str(e),
            )

    async def run_factory_cycle(self) -> List[BuildResult]:
        """Run one factory cycle: create next unpushed app or update oldest."""
        results = []

        # Load state and apps
        state = factory.load_state()
        all_apps = factory.load_all_apps()
        pushed_names = {r["name"] for r in state.get("repos", [])}

        # Find unpushed apps
        unpushed = [a for a in all_apps if factory.repo_name(a["name"]) not in pushed_names]

        if unpushed:
            # Create next unpushed app
            app_def = unpushed[0]
            result = await self.build_and_push(app_def["name"], is_update=False)
            results.append(result)
        else:
            # Update cycle: find oldest repo
            if state.get("repos"):
                oldest = min(state["repos"], key=lambda r: r.get("updated_at", r.get("pushed_at", "")))
                result = await self.build_and_push(oldest["name"].replace("-alan-vo", ""), is_update=True)
                results.append(result)

        return results

    async def get_build_history(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get build history with pagination."""
        from sqlalchemy import select, desc
        from app.core.database import get_session

        async with get_session() as session:
            stmt = select(AppBuild).order_by(desc(AppBuild.created_at)).offset(offset).limit(limit)
            result = await session.execute(stmt)
            builds = result.scalars().all()

            return [
                {
                    "id": b.id,
                    "app_name": b.app_name,
                    "repo_name": b.repo_name,
                    "status": b.status.value,
                    "is_update": b.is_update,
                    "error_message": b.error_message,
                    "github_url": b.github_url,
                    "commit_sha": b.commit_sha,
                    "created_at": b.created_at.isoformat() if b.created_at else None,
                    "updated_at": b.updated_at.isoformat() if b.updated_at else None,
                }
                for b in builds
            ]

    async def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs with pagination."""
        from sqlalchemy import select, desc
        from app.core.database import get_session

        async with get_session() as session:
            stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
            result = await session.execute(stmt)
            logs = result.scalars().all()

            return [
                {
                    "id": log.id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "user_id": log.user_id,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "success": log.success,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]

    async def clean_local(self) -> Dict[str, Any]:
        """Clean all local build artifacts."""
        factory.clean_all()
        return {"status": "cleaned", "message": "Local build artifacts and state removed"}


# Singleton instance
_factory_service: Optional[FactoryService] = None


def get_factory_service() -> FactoryService:
    """Get or create factory service singleton."""
    global _factory_service
    if _factory_service is None:
        _factory_service = FactoryService()
    return _factory_service