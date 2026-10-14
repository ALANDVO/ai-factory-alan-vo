"""API routes for ai-factory backend."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_dependency
from app.services.factory_service import get_factory_service, FactoryService, BuildResult
from app.models.app_build import BuildStatus


router = APIRouter(prefix="/api/v1", tags=["factory"])


# Request/Response models
class AppResponse(BaseModel):
    name: str
    description: str
    features: List[str]
    tech: List[str]
    api_key: str


class AppListResponse(BaseModel):
    apps: List[AppResponse]
    total: int


class DryRunResponse(BaseModel):
    app_name: str
    output: str


class BuildRequest(BaseModel):
    app_name: str
    is_update: bool = False


class BuildResponse(BaseModel):
    success: bool
    app_name: str
    repo_name: str
    error_message: Optional[str] = None
    github_url: Optional[str] = None
    commit_sha: Optional[str] = None


class BuildHistoryResponse(BaseModel):
    id: int
    app_name: str
    repo_name: str
    status: str
    is_update: bool
    error_message: Optional[str] = None
    github_url: Optional[str] = None
    commit_sha: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    created_at: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    limit: int
    offset: int


class CleanResponse(BaseModel):
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str


# Routes
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.1.0")


@router.get("/apps", response_model=AppListResponse)
async def list_apps(service: FactoryService = Depends(get_factory_service)):
    """List all available app definitions."""
    apps = await service.list_apps()
    return AppListResponse(apps=[AppResponse(**a) for a in apps], total=len(apps))


@router.get("/apps/{app_name}", response_model=AppResponse)
async def get_app(app_name: str, service: FactoryService = Depends(get_factory_service)):
    """Get a specific app definition."""
    app = await service.get_app(app_name)
    if not app:
        raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")
    return AppResponse(**app)


@router.post("/apps/{app_name}/dry-run", response_model=DryRunResponse)
async def dry_run_app(app_name: str, service: FactoryService = Depends(get_factory_service)):
    """Generate app files locally without pushing."""
    try:
        result = await service.dry_run(app_name)
        return DryRunResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dry run failed: {e}")


@router.post("/build", response_model=BuildResponse)
async def build_app(request: BuildRequest, service: FactoryService = Depends(get_factory_service)):
    """Build and push an app to GitHub."""
    try:
        result = await service.build_and_push(request.app_name, request.is_update)
        return BuildResponse(**result.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Build failed: {e}")


@router.post("/cycle", response_model=List[BuildResponse])
async def run_cycle(service: FactoryService = Depends(get_factory_service)):
    """Run one factory cycle (create next or update oldest)."""
    try:
        results = await service.run_factory_cycle()
        return [BuildResponse(**r.__dict__) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cycle failed: {e}")


@router.get("/builds", response_model=PaginatedResponse)
async def get_build_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: FactoryService = Depends(get_factory_service),
):
    """Get build history with pagination."""
    builds = await service.get_build_history(limit, offset)
    return PaginatedResponse(items=builds, total=len(builds), limit=limit, offset=offset)


@router.get("/audit", response_model=PaginatedResponse)
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: FactoryService = Depends(get_factory_service),
):
    """Get audit logs with pagination."""
    logs = await service.get_audit_logs(limit, offset)
    return PaginatedResponse(items=logs, total=len(logs), limit=limit, offset=offset)


@router.post("/clean", response_model=CleanResponse)
async def clean_artifacts(service: FactoryService = Depends(get_factory_service)):
    """Clean all local build artifacts and state."""
    result = await service.clean_local()
    return CleanResponse(**result)