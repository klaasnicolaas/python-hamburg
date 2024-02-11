# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on fetching the garage data of Hamburg."""
    async with UDPHamburg() as client:
        garages = await client.garages(limit=10, set_filter="frei >= 0")

        count: int = len(garages)
        for item in garages:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [str(location.spot_id) for location in garages]
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total garages found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
