"""Test factories for the music domain."""

import logging

from template_app.music.models import (
    Band,
    BandMembership,
    MusicGenre,
    Musician,
    MusicInstrument,
)
from tests.core.factories.base import UNSET, SQLModelFaker, UnsetType

logger = logging.getLogger(__name__)


MusicianWithInstrument = tuple[Musician, MusicInstrument]


async def associate_musicians_to_band(
    factory, band: Band, musicians: list[MusicianWithInstrument]
) -> list[BandMembership]:
    memberships = []
    for musician, instrument in musicians:
        link = await factory.create(
            BandMembership,
            band_id=band.id,
            musician_id=musician.id,
            instrument=instrument,
        )
        memberships.append(link)
    return memberships


async def create_band(
    factory: SQLModelFaker,
    name: str | UnsetType = UNSET,
    genre: MusicGenre | UnsetType = UNSET,
    musicians: list[MusicianWithInstrument] | UnsetType = UNSET,
) -> Band:
    """Create a test band with realistic data."""
    factory.register("Band.name", factory.fake.company)
    factory.register(
        "Band.formed_year", lambda: factory.fake.random_int(min=1960, max=2020)
    )

    band = await factory.create(Band, name=name, genre=genre)

    async def _create_musicians_with_instruments(
        n: int,
    ) -> list[tuple[Musician, MusicInstrument]]:
        musicians: list[Musician] = []
        for _ in range(n):
            musician = await create_musician(factory)
            musicians.append(musician)
        instruments = factory.fake.random_choices(MusicInstrument, length=n)
        return list(zip(musicians, instruments, strict=True))

    match musicians:
        case UnsetType():
            musicians_ = await _create_musicians_with_instruments(n=4)
        case _:
            musicians_ = musicians

    await associate_musicians_to_band(factory, band, musicians_)
    return band


async def create_musician(
    factory: SQLModelFaker,
    name: str | UnsetType = UNSET,
    instrument: MusicInstrument | UnsetType = UNSET,
    band: Band | UnsetType = UNSET,
) -> Musician:
    """Create a test musician with realistic data."""
    musician = await factory.create(Musician, name=name)

    # Create band membership if band is provided
    if band is not UNSET and band is not None:
        instrument_value = (
            instrument
            if instrument is not UNSET
            else factory.fake.enum(MusicInstrument)
        )
        await factory.create(
            BandMembership,
            band_id=band.id,
            musician_id=musician.id,
            instrument=instrument_value,
        )

    return musician
