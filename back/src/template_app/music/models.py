from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel

from template_app.core.database.models import BaseModel


class MusicGenre(StrEnum):
    ROCK = "ROCK"
    POP = "POP"
    JAZZ = "JAZZ"
    BLUES = "BLUES"
    FOLK = "FOLK"
    ELECTRONIC = "ELECTRONIC"
    HIP_HOP = "HIP_HOP"


class MusicInstrument(StrEnum):
    GUITAR = "GUITAR"
    BASS = "BASS"
    DRUMS = "DRUMS"
    VOCALS = "VOCALS"
    KEYBOARD = "KEYBOARD"
    VIOLIN = "VIOLIN"
    SAXOPHONE = "SAXOPHONE"


class BandMembership(SQLModel, table=True):
    band_id: int = Field(foreign_key="band.id", primary_key=True)
    musician_id: int = Field(foreign_key="musician.id", primary_key=True)
    instrument: MusicInstrument

    band: "Band" = Relationship(back_populates="memberships")
    musician: "Musician" = Relationship(back_populates="memberships")


class Band(BaseModel, table=True):
    """A music band with musicians."""

    name: str = Field(index=True)
    genre: MusicGenre
    formed_year: int | None = None
    country: str | None = None

    # Relationships
    memberships: list[BandMembership] = Relationship(back_populates="band")


class Musician(BaseModel, table=True):
    """A musician who can be part of a band."""

    name: str = Field(index=True)

    # Relationships
    memberships: list[BandMembership] = Relationship(back_populates="musician")
