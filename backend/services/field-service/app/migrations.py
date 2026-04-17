import asyncio

from alembic import command
from alembic.config import Config


def _run_upgrade() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def run_migrations() -> None:
    await asyncio.to_thread(_run_upgrade)
