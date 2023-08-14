# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on fetching the park and ride data of Hamburg."""
    async with UDPHamburg() as client:
        park_and_rides = await client.park_and_rides(bulk="true")

        count: int = len(park_and_rides)
        for item in park_and_rides:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [
            str(location.spot_id) for location in park_and_rides
        ]
        num_values = len(unique_values)

        print("__________________________")
        print(f"Total park and rides found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
