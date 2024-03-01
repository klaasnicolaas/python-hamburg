# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""

from __future__ import annotations

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on fetching the disabled parking data of Hamburg."""
    async with UDPHamburg() as client:
        disabled_parkings = await client.disabled_parkings(limit=1000)

        count = len(disabled_parkings)
        for item in disabled_parkings:
            print(item)

        # Count unique id's in disabled_parkings
        unique_values: list[str] = [
            str(location.spot_id) for location in disabled_parkings
        ]
        num_values = len(set(unique_values))

        print("__________________________")
        print(f"Total locations found: {count}")
        print(f"Unique ID values: {num_values}")


if __name__ == "__main__":
    asyncio.run(main())
