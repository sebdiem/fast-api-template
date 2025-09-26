from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from template_app.core.exceptions import ConflictError, NotFoundError
from template_app.music import schemas
from template_app.music.models import Band, Musician


class MusicService:
    """Service layer for music domain operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_band(self, band_data: schemas.BandCreate) -> Band:
        """Create a new band."""
        # Check if band already exists
        existing_band = await self.session.scalar(
            select(Band).where(Band.name == band_data.name)
        )
        if existing_band:
            raise ConflictError(f"Band '{band_data.name}' already exists")

        band = Band(**band_data.model_dump())
        self.session.add(band)
        await self.session.flush()
        return band

    async def get_band(self, band_id: int) -> Band:
        """Get a band by ID with its musicians."""
        band = await self.session.scalar(
            select(Band).options(selectinload(Band.musicians)).where(Band.id == band_id)  # type: ignore[arg-type]
        )
        if not band:
            raise NotFoundError(f"Band with ID {band_id} not found")
        return band

    async def get_bands(
        self, skip: int = 0, limit: int = 100, genre: str | None = None
    ) -> list[Band]:
        """Get all bands with optional filtering."""
        query = select(Band).options(selectinload(Band.musicians))  # type: ignore[arg-type]

        if genre:
            query = query.where(Band.genre == genre)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_band(self, band_id: int, band_data: schemas.BandUpdate) -> Band:
        """Update a band."""
        band = await self.session.scalar(select(Band).where(Band.id == band_id))
        if not band:
            raise NotFoundError(f"Band with ID {band_id} not found")

        update_data = band_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(band, field, value)

        await self.session.flush()
        return band

    async def delete_band(self, band_id: int) -> None:
        """Delete a band and all its musicians."""
        band = await self.session.scalar(select(Band).where(Band.id == band_id))
        if not band:
            raise NotFoundError(f"Band with ID {band_id} not found")

        # Delete associated musicians first
        await self.session.execute(select(Musician).where(Musician.band_id == band_id))

        await self.session.delete(band)
        await self.session.flush()

    async def create_musician(self, musician_data: schemas.MusicianCreate) -> Musician:
        """Create a new musician."""
        # Validate band exists if band_id is provided
        if musician_data.band_id:
            band = await self.session.scalar(
                select(Band).where(Band.id == musician_data.band_id)
            )
            if not band:
                raise NotFoundError(f"Band with ID {musician_data.band_id} not found")

        musician = Musician(**musician_data.model_dump())
        self.session.add(musician)
        await self.session.flush()
        return musician

    async def get_musician(self, musician_id: int) -> Musician:
        """Get a musician by ID."""
        musician = await self.session.scalar(
            select(Musician).where(Musician.id == musician_id)
        )
        if not musician:
            raise NotFoundError(f"Musician with ID {musician_id} not found")
        return musician

    async def get_musicians(
        self, skip: int = 0, limit: int = 100, band_id: int | None = None
    ) -> list[Musician]:
        """Get all musicians with optional filtering by band."""
        query = select(Musician)

        if band_id is not None:
            query = query.where(Musician.band_id == band_id)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_musician(
        self, musician_id: int, musician_data: schemas.MusicianUpdate
    ) -> Musician:
        """Update a musician."""
        musician = await self.session.scalar(
            select(Musician).where(Musician.id == musician_id)
        )
        if not musician:
            raise NotFoundError(f"Musician with ID {musician_id} not found")

        # Validate band exists if band_id is being updated
        if (
            musician_data.band_id is not None
            and musician_data.band_id != musician.band_id
        ):
            band = await self.session.scalar(
                select(Band).where(Band.id == musician_data.band_id)
            )
            if not band:
                raise NotFoundError(f"Band with ID {musician_data.band_id} not found")

        update_data = musician_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(musician, field, value)

        await self.session.flush()
        return musician

    async def delete_musician(self, musician_id: int) -> None:
        """Delete a musician."""
        musician = await self.session.scalar(
            select(Musician).where(Musician.id == musician_id)
        )
        if not musician:
            raise NotFoundError(f"Musician with ID {musician_id} not found")

        await self.session.delete(musician)
        await self.session.flush()
