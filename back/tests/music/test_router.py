"""Tests for music domain API endpoints."""

from httpx import AsyncClient

from template_app.music.models import MusicGenre
from tests.core.factories.base import SQLModelFaker
from tests.music.factories import create_band, create_musician


async def test_create_band(http_client: AsyncClient):
    """Test creating a band via API."""
    band_data = {
        "name": "The Beatles",
        "genre": "ROCK",
        "formed_year": 1960,
        "country": "UK",
    }

    response = await http_client.post("/api/music/bands", json=band_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "The Beatles"
    assert data["genre"] == "ROCK"
    assert data["formed_year"] == 1960
    assert data["country"] == "UK"
    assert "id" in data


async def test_get_bands(http_client: AsyncClient, factory: SQLModelFaker):
    """Test getting bands via API."""
    await create_band(factory, name="The Beatles", genre=MusicGenre.ROCK)
    await create_band(factory, name="Led Zeppelin", genre=MusicGenre.ROCK)

    response = await http_client.get("/api/music/bands")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    band_names = [band["name"] for band in data]
    assert "The Beatles" in band_names
    assert "Led Zeppelin" in band_names


async def test_get_band_by_id(http_client: AsyncClient, factory: SQLModelFaker):
    """Test getting a specific band by ID."""
    band = await create_band(factory, name="The Beatles")

    response = await http_client.get(f"/api/music/bands/{band.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == band.id
    assert data["name"] == "The Beatles"


async def test_update_band(http_client: AsyncClient, factory: SQLModelFaker):
    """Test updating a band."""
    band = await create_band(factory, name="The Beatles", genre=MusicGenre.ROCK)

    update_data = {"genre": "POP"}
    response = await http_client.patch(f"/api/music/bands/{band.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["genre"] == "POP"
    assert data["name"] == "The Beatles"  # unchanged


async def test_delete_band(http_client: AsyncClient, factory: SQLModelFaker):
    """Test deleting a band."""
    band = await create_band(factory, name="The Beatles")

    response = await http_client.delete(f"/api/music/bands/{band.id}")
    assert response.status_code == 200

    # Verify it's gone
    response = await http_client.get(f"/api/music/bands/{band.id}")
    assert response.status_code == 404


async def test_create_musician(http_client: AsyncClient, factory: SQLModelFaker):
    """Test creating a musician via API."""
    musician_data = {
        "name": "John Lennon",
    }

    response = await http_client.post("/api/music/musicians", json=musician_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "John Lennon"
    assert "id" in data


async def test_get_musicians_by_band(http_client: AsyncClient, factory: SQLModelFaker):
    """Test filtering musicians by band."""
    from template_app.music.models import MusicInstrument

    band1 = await create_band(factory, name="The Beatles", musicians=[])
    band2 = await create_band(factory, name="Led Zeppelin", musicians=[])

    # Create musicians and their band memberships
    await create_musician(
        factory, name="John Lennon", band=band1, instrument=MusicInstrument.GUITAR
    )
    await create_musician(
        factory, name="Paul McCartney", band=band1, instrument=MusicInstrument.BASS
    )
    await create_musician(
        factory, name="Robert Plant", band=band2, instrument=MusicInstrument.VOCALS
    )

    response = await http_client.get(f"/api/music/musicians?band_id={band1.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    musician_names = [musician["name"] for musician in data]
    assert "John Lennon" in musician_names
    assert "Paul McCartney" in musician_names
    assert "Robert Plant" not in musician_names


async def test_band_not_found(http_client: AsyncClient):
    """Test getting a non-existent band returns 404."""
    response = await http_client.get("/api/music/bands/999999")
    assert response.status_code == 404


async def test_create_duplicate_band(http_client: AsyncClient, factory: SQLModelFaker):
    """Test that creating a duplicate band returns conflict error."""
    await create_band(factory, name="The Beatles")

    band_data = {
        "name": "The Beatles",  # Same name
        "genre": "ROCK",
    }

    response = await http_client.post("/api/music/bands", json=band_data)
    assert response.status_code == 409
