"""Basic tests for the Urban Data Platform API of Hamburg."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from hamburg import UDPHamburg
from hamburg.exceptions import UDPHamburgConnectionError, UDPHamburgError

from . import load_fixtures


async def test_json_request(
    aresponses: ResponsesMockServer, hamburg_client: UDPHamburg
) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    response = await hamburg_client._request("test")
    assert response is not None
    await hamburg_client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    async with UDPHamburg() as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout from the Urban Data Platform API of Hamburg."""

    # Faking a timeout by sleeping
    async def response_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("disabled_parking.geojson"),
        )

    aresponses.add("api.hamburg.de", "/datasets/v1/test", "GET", response_handler)

    async with ClientSession() as session:
        client = UDPHamburg(
            session=session,
            request_timeout=0.1,
        )
        with pytest.raises(UDPHamburgConnectionError):
            assert await client._request("test")


async def test_content_type(
    aresponses: ResponsesMockServer, hamburg_client: UDPHamburg
) -> None:
    """Test request content type error from Urban Data Platform API of Hamburg."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )
    with pytest.raises(UDPHamburgError):
        assert await hamburg_client._request("test")


async def test_client_error() -> None:
    """Test request client error from the Urban Data Platform API of Hamburg."""
    async with ClientSession() as session:
        client = UDPHamburg(session=session)
        with patch.object(
            session,
            "request",
            side_effect=ClientError,
        ), pytest.raises(UDPHamburgConnectionError):
            assert await client._request("test")
