# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on using the Hamburg API client."""
    async with UDPHamburg() as client:
        disabled_parkings = await client.disabled_parkings(bulk="true")
        park_and_rides = await client.park_and_rides(bulk="true")
        garages = await client.garages(bulk="true")

        print(disabled_parkings)
        print(park_and_rides)

        count: int
        for index, item in enumerate(garages, 1):
            count = index
            print(item)
        print(f"{count} locations found")


if __name__ == "__main__":
    asyncio.run(main())
