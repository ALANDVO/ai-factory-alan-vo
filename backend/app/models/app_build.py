"""AppBuild model for tracking generated applications."""
import enum
from sqlalchemy import Enum, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class BuildStatus(str, enum.Enum):
    """Status of an app build."""
    PENDING = "pending"
    BUILDING = "building"
    PUSHING = "pushing"
    COMPLETED = "completed"
    FAILED = "failed"


class AppBuild(Base, TimestampMixin):
    """Track each app build/push operation."""

    __tablename__ = "app_builds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    repo_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[BuildStatus] = mapped_column(
        Enum(BuildStatus, native_enum=False),
        default=BuildStatus.PENDING,
        nullable=False,
    )
    is_update: Mapped[bool] = mapped_column(default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_app_builds_app_name_status", "app_name", "status"),
        Index("ix_app_builds_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AppBuild(id={self.id}, app_name='{self.app_name}', status='{self.status}')>"