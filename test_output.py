# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on using the Hamburg API client."""
    async with UDPHamburg() as client:
        disabled_parkings = await client.disabled_parkings(bulk="true")
        print(disabled_parkings)

        park_and_ride = await client.park_and_ride(bulk="true")
        count: int

        for index, item in enumerate(park_and_ride, 1):
            count = index
            print(item)
        print(f"{count} locations found")


if __name__ == "__main__":
    asyncio.run(main())
