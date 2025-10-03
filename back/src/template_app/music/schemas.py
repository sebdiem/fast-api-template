from pydantic import BaseModel, ConfigDict


class MusicianBase(BaseModel):
    name: str
    instrument: str


class MusicianCreate(MusicianBase):
    band_id: int | None = None


class MusicianUpdate(BaseModel):
    name: str | None = None
    instrument: str | None = None
    band_id: int | None = None


class Musician(MusicianBase):
    id: int
    band_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class BandBase(BaseModel):
    name: str
    genre: str
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
    musicians: list[Musician] = []

    model_config = ConfigDict(from_attributes=True)
