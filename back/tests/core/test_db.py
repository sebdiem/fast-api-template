import subprocess

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from alembic.env import include_object  # type: ignore
except Exception:
    include_object = None


def test_models_match_database(db_session: AsyncSession):
    result = subprocess.run(
        ["alembic", "-x", "check-models=1", "check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"\n# stdout {'#' * 81}\n{result.stdout}\n# stderr {'#' * 81}\n{result.stderr}"
    )
