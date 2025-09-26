from sqlmodel import Field, Relationship

from template_app.core.database.models import BaseModel


class Band(BaseModel, table=True):
    """A music band with musicians."""

    name: str = Field(index=True)
    genre: str
    formed_year: int | None = None
    country: str | None = None

    # Relationships
    musicians: list["Musician"] = Relationship(back_populates="band")


class Musician(BaseModel, table=True):
    """A musician who can be part of a band."""

    name: str = Field(index=True)
    instrument: str
    band_id: int | None = Field(default=None, foreign_key="band.id")

    # Relationships
    band: Band | None = Relationship(back_populates="musicians")
