from pydantic import BaseModel, ConfigDict, Field

from template_app.music.models import MusicGenre, MusicInstrument


class MusicianBase(BaseModel):
    name: str


class MusicianCreate(MusicianBase):
    pass


class MusicianUpdate(BaseModel):
    name: str | None = None


class Musician(MusicianBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BandMembershipBase(BaseModel):
    instrument: MusicInstrument


class BandMembershipCreate(BandMembershipBase):
    band_id: int
    musician_id: int


class BandMembership(BandMembershipBase):
    musician: Musician

    model_config = ConfigDict(from_attributes=True)


class BandBase(BaseModel):
    name: str
    genre: MusicGenre
    formed_year: int | None = None
    country: str | None = None


class BandCreate(BandBase):
    pass


class BandUpdate(BaseModel):
    name: str | None = None
    genre: str | None = None
    formed_year: int | None = None
    country: str | None = None


class Band(BandBase):
    id: int
    memberships: list[BandMembership] = Field(
        default_factory=list, serialization_alias="members"
    )

    model_config = ConfigDict(from_attributes=True)
