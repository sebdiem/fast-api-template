from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlmodel import Field, SQLModel

from template_app.core.database.base import now_factory


class Base(AsyncAttrs, SQLModel):
    pass


class TimestampMixin(Base):
    """Mixin for adding timestamps to models."""

    created_at: datetime = Field(
        default_factory=now_factory, sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime | None = Field(
        default=None, sa_column_kwargs={"onupdate": func.now()}
    )


class BaseModel(TimestampMixin):
    """Base model with common fields."""

    id: int | None = Field(default=None, primary_key=True)
