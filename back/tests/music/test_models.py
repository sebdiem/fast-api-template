"""Tests for music domain models."""

import pytest

from tests.core.factories.base import SQLModelFaker
from tests.music.factories import create_band, create_musician


@pytest.mark.asyncio
async def test_band_creation(factory: SQLModelFaker):
    """Test that we can create a band with the factory."""
    band = await create_band(factory, name="The Beatles", genre="Rock")

    assert band.id is not None
    assert band.name == "The Beatles"
    assert band.genre == "Rock"
    assert band.created_at is not None


@pytest.mark.asyncio
async def test_musician_creation(factory: SQLModelFaker):
    """Test that we can create a musician with the factory."""
    musician = await create_musician(factory, name="John Lennon", instrument="Guitar")

    assert musician.id is not None
    assert musician.name == "John Lennon"
    assert musician.instrument == "Guitar"
    assert musician.created_at is not None


@pytest.mark.asyncio
async def test_band_musician_relationship(factory: SQLModelFaker):
    """Test the relationship between bands and musicians."""
    band = await create_band(factory, name="The Beatles")
    musician = await create_musician(factory, name="John Lennon", band_id=band.id)

    assert musician.band_id == band.id

    # Test relationship access (would require additional session loading in real use)
    assert band.id is not None
    assert musician.id is not None
