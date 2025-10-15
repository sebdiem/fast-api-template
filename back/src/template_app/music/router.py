from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from template_app.core.database import get_session
from template_app.music import schemas
from template_app.music.models import MusicGenre
from template_app.music.service import MusicService

router = APIRouter(prefix="/api/music", tags=["music"])

# Type aliases for dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_music_service(session: SessionDep) -> MusicService:
    return MusicService(session)


MusicServiceDep = Annotated[MusicService, Depends(get_music_service)]


# Band endpoints
@router.post("/bands", response_model=schemas.Band)
async def create_band(
    band: schemas.BandCreate,
    music_service: MusicServiceDep,
):
    """Create a new band."""
    return await music_service.create_band(band)


@router.get("/bands", response_model=list[schemas.Band])
async def get_bands(
    music_service: MusicServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    genre: Annotated[MusicGenre | None, Query()] = None,
):
    """Get all bands with optional filtering by genre."""
    bands, _count = await music_service.get_bands(skip=skip, limit=limit, genre=genre)
    return bands


@router.get("/bands/{band_id}", response_model=schemas.Band)
async def get_band(
    band_id: int,
    music_service: MusicServiceDep,
):
    """Get a specific band by ID."""
    return await music_service.get_band(band_id)


@router.patch("/bands/{band_id}", response_model=schemas.Band)
async def update_band(
    band_id: int,
    band_update: schemas.BandUpdate,
    music_service: MusicServiceDep,
):
    """Update a band."""
    return await music_service.update_band(band_id, band_update)


@router.delete("/bands/{band_id}")
async def delete_band(
    band_id: int,
    music_service: MusicServiceDep,
):
    """Delete a band and all its musicians."""
    await music_service.delete_band(band_id)
    return {"message": "Band deleted successfully"}


# Musician endpoints
@router.post("/musicians", response_model=schemas.Musician)
async def create_musician(
    musician: schemas.MusicianCreate,
    music_service: MusicServiceDep,
):
    """Create a new musician."""
    return await music_service.create_musician(musician)


@router.get("/musicians", response_model=list[schemas.Musician])
async def get_musicians(
    music_service: MusicServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    band_id: Annotated[int | None, Query()] = None,
):
    """Get all musicians with optional filtering by band."""
    return await music_service.get_musicians(skip=skip, limit=limit, band_id=band_id)


@router.get("/musicians/{musician_id}", response_model=schemas.Musician)
async def get_musician(
    musician_id: int,
    music_service: MusicServiceDep,
):
    """Get a specific musician by ID."""
    return await music_service.get_musician(musician_id)


@router.patch("/musicians/{musician_id}", response_model=schemas.Musician)
async def update_musician(
    musician_id: int,
    musician_update: schemas.MusicianUpdate,
    music_service: MusicServiceDep,
):
    """Update a musician."""
    return await music_service.update_musician(musician_id, musician_update)


@router.delete("/musicians/{musician_id}")
async def delete_musician(
    musician_id: int,
    music_service: MusicServiceDep,
):
    """Delete a musician."""
    await music_service.delete_musician(musician_id)
    return {"message": "Musician deleted successfully"}
