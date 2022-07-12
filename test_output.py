# pylint: disable=W0621
"""Asynchronous Python client providing Urban Data information of Hamburg."""

import asyncio

from hamburg import UDPHamburg


async def main() -> None:
    """Show example on using the Hamburg API client."""
    async with UDPHamburg() as client:
        locations = await client.disabled_parkings(bulk="true")
        count: int

        for index, item in enumerate(locations, 1):
            count = index
            print(item)
        print(f"{count} locations found")


if __name__ == "__main__":
    asyncio.run(main())
