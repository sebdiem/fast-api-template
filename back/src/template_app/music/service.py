from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from template_app.core.exceptions import ConflictError, NotFoundError
from template_app.music import schemas
from template_app.music.models import Band, BandMembership, Musician


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
        # Refresh to get relationships loaded
        await self.session.refresh(band, ["memberships"])
        return band

    async def get_band(self, band_id: int) -> Band:
        """Get a band by ID with its musicians."""
        band = await self.session.scalar(
            select(Band)
            .options(selectinload(Band.memberships))  # type: ignore[arg-type]
            .where(Band.id == band_id)
        )
        if not band:
            raise NotFoundError(f"Band with ID {band_id} not found")
        return band

    async def get_bands(
        self, skip: int = 0, limit: int = 100, genre: str | None = None
    ) -> list[Band]:
        """Get all bands with optional filtering."""
        query = select(Band).options(selectinload(Band.memberships))  # type: ignore[arg-type]

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
        # Refresh to get relationships loaded
        await self.session.refresh(band, ["memberships"])
        return band

    async def delete_band(self, band_id: int) -> None:
        """Delete a band and all its memberships."""
        band = await self.session.scalar(select(Band).where(Band.id == band_id))
        if not band:
            raise NotFoundError(f"Band with ID {band_id} not found")

        # Delete associated memberships first
        memberships = await self.session.execute(
            select(BandMembership).where(BandMembership.band_id == band_id)
        )
        for membership in memberships.scalars():
            await self.session.delete(membership)

        await self.session.delete(band)
        await self.session.flush()

    async def create_musician(self, musician_data: schemas.MusicianCreate) -> Musician:
        """Create a new musician."""
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
        if band_id is not None:
            # Get musicians that are members of the specified band
            memberships_result = await self.session.execute(
                select(BandMembership).where(BandMembership.band_id == band_id)
            )
            musician_ids = [m.musician_id for m in memberships_result.scalars()]
            if not musician_ids:
                return []

            query = select(Musician).where(col(Musician.id).in_(musician_ids))
        else:
            query = select(Musician)

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

        update_data = musician_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(musician, field, value)

        await self.session.flush()
        return musician

    async def delete_musician(self, musician_id: int) -> None:
        """Delete a musician and all their band memberships."""
        musician = await self.session.scalar(
            select(Musician).where(Musician.id == musician_id)
        )
        if not musician:
            raise NotFoundError(f"Musician with ID {musician_id} not found")

        # Delete associated memberships first
        memberships = await self.session.execute(
            select(BandMembership).where(BandMembership.musician_id == musician_id)
        )
        for membership in memberships.scalars():
            await self.session.delete(membership)

        await self.session.delete(musician)
        await self.session.flush()

    async def create_band_membership(
        self, membership_data: schemas.BandMembershipCreate
    ) -> BandMembership:
        """Create a new band membership."""
        # Validate band exists
        band = await self.session.scalar(
            select(Band).where(Band.id == membership_data.band_id)
        )
        if not band:
            raise NotFoundError(f"Band with ID {membership_data.band_id} not found")

        # Validate musician exists
        musician = await self.session.scalar(
            select(Musician).where(Musician.id == membership_data.musician_id)
        )
        if not musician:
            raise NotFoundError(
                f"Musician with ID {membership_data.musician_id} not found"
            )

        membership = BandMembership(**membership_data.model_dump())
        self.session.add(membership)
        await self.session.flush()
        return membership
