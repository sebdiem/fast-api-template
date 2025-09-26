"""Test factories for the music domain."""

from template_app.music.models import Band, Musician
from tests.core.factories.base import SQLModelFaker


async def create_band(factory: SQLModelFaker, **overrides) -> Band:
    """Create a test band with realistic data."""
    defaults = {
        "name": factory.fake.company(),
        "genre": factory.fake.random_element(
            elements=("Rock", "Pop", "Jazz", "Blues", "Folk", "Electronic", "Hip Hop")
        ),
        "formed_year": factory.fake.random_int(min=1960, max=2020),
        "country": factory.fake.country(),
    }
    defaults.update(overrides)

    factory.register("Band.name", lambda: factory.fake.company())
    factory.register(
        "Band.genre",
        lambda: factory.fake.random_element(
            elements=("Rock", "Pop", "Jazz", "Blues", "Folk", "Electronic", "Hip Hop")
        ),
    )
    factory.register(
        "Band.formed_year", lambda: factory.fake.random_int(min=1960, max=2020)
    )
    factory.register("Band.country", lambda: factory.fake.country())

    return await factory.create(Band, **defaults)


async def create_musician(factory: SQLModelFaker, **overrides) -> Musician:
    """Create a test musician with realistic data."""
    defaults = {
        "name": factory.fake.name(),
        "instrument": factory.fake.random_element(
            elements=(
                "Guitar",
                "Bass",
                "Drums",
                "Vocals",
                "Keyboard",
                "Violin",
                "Saxophone",
            )
        ),
    }
    defaults.update(overrides)

    factory.register("Musician.name", lambda: factory.fake.name())
    factory.register(
        "Musician.instrument",
        lambda: factory.fake.random_element(
            elements=(
                "Guitar",
                "Bass",
                "Drums",
                "Vocals",
                "Keyboard",
                "Violin",
                "Saxophone",
            )
        ),
    )

    return await factory.create(Musician, **defaults)
