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


async def create_band(
    factory: SQLModelFaker,
    name: str | UnsetType = UNSET,
    genre: MusicGenre | UnsetType = UNSET,
    musicians: list[tuple[Musician, MusicInstrument]] | UnsetType = UNSET,
) -> Band:
    """Create a test band with realistic data."""
    factory.register("Band.name", factory.fake.company)
    factory.register(
        "Band.formed_year", lambda: factory.fake.random_int(min=1960, max=2020)
    )

    band = await factory.create(Band, name=name, genre=genre)

    async def _associate_musicians(n: int):
        # Create musicians sequentially to avoid session conflicts
        musicians = []
        for _ in range(n):
            musician = await create_musician(factory)
            musicians.append(musician)

        # Create memberships sequentially
        instruments = factory.fake.random_choices(MusicInstrument, length=n)
        for i, musician in enumerate(musicians):
            await factory.create(
                BandMembership,
                band_id=band.id,
                musician_id=musician.id,
                instrument=instruments[i],
            )

    match musicians:
        case UnsetType():
            await _associate_musicians(n=4)
        case []:
            # Don't create any musicians when empty list is provided
            pass

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
