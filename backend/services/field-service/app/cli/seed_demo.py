import asyncio
import argparse

from app.db import SessionLocal, engine
from app.repositories.demo_data import DemoDataRepository


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo field-service data")
    parser.add_argument(
        "--without-rounds",
        action="store_true",
        help="Seed dictionaries only: equipment, employees, routes, checklists and parameter definitions",
    )
    args = parser.parse_args()

    async with SessionLocal() as session:
        await DemoDataRepository(session).seed(include_rounds=not args.without_rounds)
    await engine.dispose()
    mode = "without rounds" if args.without_rounds else "with rounds"
    print(f"Demo data seeded ({mode})")


if __name__ == "__main__":
    asyncio.run(main())
