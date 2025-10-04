from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from enum import StrEnum
from types import UnionType
from typing import (
    Any,
    Optional,
    Protocol,
    TypeVar,
    get_args,
    get_origin,
)
from uuid import uuid4

from faker import Faker
from pydantic_core import PydanticUndefined
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class UnsetType:
    """To be used in function definition to distinguish between user provided or default value.

    Example usage:
    ```
        def my_function(arg: None | UnsetType = UNSET): ...
    ```
    """

    __slots__ = ()

    def __eq__(self, value: object, /) -> bool:
        return value is UnsetType

    def __repr__(self) -> str:
        return "UNSET"


UNSET = UnsetType()


class ModelBuilder(Protocol):
    def build(self, model: type[T], /, **overrides: Any) -> T:
        """Builds an instance of model T."""
        ...

    def register(self, key: Any, fn: Callable[[], Any]) -> None:
        """Register or override a value generator for a python type or field name."""
        ...


class SQLModelFaker:
    """Auto-generates SQLModel instances with realistic fake values for tests.

    Attributes:
        fake: Faker instance (seedable).
        session: database session or None. If provided, will save objects in db.
        generators: Map of (python_type or field_name) -> callable returning a value.
    """

    def __init__(self, fake: Faker | None = None, session: AsyncSession | None = None):
        self.fake = fake or Faker()
        self.session = session
        # type-based generators
        self.generators: dict[Any, Callable[[], Any]] = {
            int: self.fake.pyint,
            float: self.fake.pyfloat,
            bool: self.fake.pybool,
            str: self.fake.pystr,
            datetime: self.fake.date_time,
            date: self.fake.date_object,
        }
        # field-name heuristics for nicer realism
        self.generators["email"] = self.fake.unique.email
        self.generators["name"] = self.fake.name
        self.generators["full_name"] = self.fake.name
        self.generators["country"] = self.fake.country
        self.generators["uuid"] = lambda: str(uuid4())
        self.generators["id"] = (
            self.fake.random_int
        )  # if you want auto ids here (often repo sets id)

    def register(self, key: Any, fn: Callable[[], Any]) -> None:
        """Register or override a generator for a python type or field name."""
        self.generators[key] = fn

    def _is_optional(self, annotation: Any) -> tuple[bool, Any]:
        origin = get_origin(annotation)
        if origin is Optional or origin is UnionType:
            args = get_args(annotation)
            non_none = [a for a in args if a is not type(None)]
            return True, non_none[0] if non_none else Any
        return False, annotation

    def _by_field_name(self, name: str) -> Callable[[], Any] | None:
        return self.generators.get(name)

    def _by_type(self, pytype: Any) -> Callable[[], Any] | None:
        if pytype in self.generators:
            return self.generators[pytype]
        if issubclass(pytype, StrEnum):
            return lambda: self.fake.enum(pytype)
        try:
            from pydantic import EmailStr

            if pytype is EmailStr:
                return self.fake.unique.email
        except Exception:
            pass

        return None

    def build(self, model: type[T], /, **overrides: Any) -> T:
        """Create a SQLModel instance with fake data.

        Args:
            model: SQLModel subclass to instantiate.
            **overrides: explicit field values.

        Returns:
            model instance.
        """
        field_map = model.model_fields
        values: dict[str, Any] = {}

        for name, finfo in field_map.items():
            if name in overrides:
                values[name] = overrides.pop(name)
                continue

            # Skip if default or default_factory exists
            default_present = getattr(finfo, "default", None) not in (
                None,
                "",
                PydanticUndefined,
                ...,
            )
            default_factory = getattr(finfo, "default_factory", None)
            if default_present or default_factory is not None:
                continue

            # Determine annotation/inner type
            annotation = getattr(finfo, "annotation", None) or getattr(
                finfo, "outer_type_", None
            )
            _optional, inner = self._is_optional(annotation)

            # Try field-name generator first (email, name, etc.)
            g = self._by_field_name(f"{model.__name__}.{name}") or self._by_field_name(
                name
            )
            if not g:
                # Try by python type
                pytype = getattr(finfo, "annotation", None) or getattr(
                    finfo, "type_", None
                )
                g = self._by_type(inner or pytype)
            if not g:
                # Try by faker name
                if hasattr(self.fake, name):
                    g = getattr(self.fake, name)
            if g:
                values[name] = g()
            else:
                # last resort: a stable fake string
                values[name] = f"{name}-{self.fake.pystr(min_chars=6, max_chars=10)}"

        if len(overrides):
            msg = f"unknown attributes for model {model} used in model factory: {','.join(overrides)}"
            raise RuntimeError(msg)

        return model(**values)  # type: ignore[arg-type]

    async def create(self, model: type[T], **overrides: Any) -> T:
        """Build and persist a SQLModel instance to the database.

        Args:
            model: SQLModel subclass to create
            **overrides: explicit field values to override

        Returns:
            Persisted model instance with database-generated fields populated
        """
        overrides = {k: v for k, v in overrides.items() if v is not UNSET}
        instance = self.build(model, **overrides)
        if self.session is not None:
            self.session.add(instance)
            await self.session.flush()
        return instance

    async def create_multiple(
        self, model: type[T], count: int, **shared_overrides: Any
    ) -> list[T]:
        """Create multiple instances of the same model efficiently.

        Args:
            model: SQLModel subclass to create
            count: Number of instances to create
            **shared_overrides: Common field values for all instances

        Returns:
            List of persisted model instances
        """
        shared_overrides = {
            k: v for k, v in shared_overrides.items() if v is not UNSET
        }
        instances = []
        for _ in range(count):
            instance = self.build(model, **shared_overrides)
            instances.append(instance)
            if self.session:
                self.session.add(instance)

        if self.session:
            await self.session.flush()

        return instances
