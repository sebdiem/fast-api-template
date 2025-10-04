"""Tests for music domain models."""

from sqlalchemy.ext.asyncio import AsyncSession

from template_app.music.models import BandMembership, MusicGenre, MusicInstrument
from tests.core.factories.base import SQLModelFaker
from tests.music.factories import create_band, create_musician


async def test_band_creation(factory: SQLModelFaker):
    """Test that we can create a band with the factory."""
    band = await create_band(factory, name="The Beatles", genre=MusicGenre.ROCK)

    assert band.id is not None
    assert band.name == "The Beatles"
    assert band.genre == MusicGenre.ROCK
    assert band.created_at is not None


async def test_musician_creation(factory: SQLModelFaker):
    """Test that we can create a musician with the factory."""

    musician = await create_musician(factory, name="John Lennon")

    assert musician.id is not None
    assert musician.name == "John Lennon"
    assert musician.created_at is not None


async def test_band_musician_relationship(
    factory: SQLModelFaker, db_session: AsyncSession
):
    """Test the relationship between bands and musicians through membership."""

    band = await create_band(factory, name="The Beatles", musicians=[])
    musician = await create_musician(
        factory, name="John Lennon", band=band, instrument=MusicInstrument.GUITAR
    )

    # Test that objects were created
    assert band.id is not None
    assert musician.id is not None
    assert band.name == "The Beatles"
    assert musician.name == "John Lennon"
    memberships: list[BandMembership] = await band.awaitable_attrs.memberships
    assert len(memberships) == 1
    assert memberships[0].musician_id == musician.id
