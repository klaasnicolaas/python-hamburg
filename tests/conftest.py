"""Fixtures for the UDP Hamburg tests."""
from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from hamburg import UDPHamburg


@pytest.fixture(name="hamburg_client")
async def client() -> AsyncGenerator[UDPHamburg, None]:
    """Return a UDP Hamburg client."""
    async with ClientSession() as session, UDPHamburg(
        session=session
    ) as hamburg_client:
        yield hamburg_client
