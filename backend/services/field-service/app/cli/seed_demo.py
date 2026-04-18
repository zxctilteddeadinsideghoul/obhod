import asyncio

from app.db import SessionLocal, engine
from app.repositories.demo_data import DemoDataRepository


async def main() -> None:
    async with SessionLocal() as session:
        await DemoDataRepository(session).seed()
    await engine.dispose()
    print("Demo data seeded")


if __name__ == "__main__":
    asyncio.run(main())
