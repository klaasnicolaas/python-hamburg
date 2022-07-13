"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from hamburg import DisabledParking, ParkAndRide, UDPHamburg

from . import load_fixtures


@pytest.mark.asyncio
async def test_all_parking_spaces(aresponses: ResponsesMockServer) -> None:
    """Test all parking spaces function."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/behindertenstellplaetze/collections/verkehr_behindertenparkpl/items",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("disabled_parking.geojson"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[DisabledParking] = await client.disabled_parkings()
        assert spaces is not None
        for item in spaces:
            assert isinstance(item, DisabledParking)
            assert item.spot_id is not None
            assert item.street is None or isinstance(item.street, str)
            assert item.limitation is None or isinstance(item.limitation, str)
            assert item.longitude is not None
            assert item.latitude is not None


@pytest.mark.asyncio
async def test_park_and_rides(aresponses: ResponsesMockServer) -> None:
    """Test park and ride spaces function."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/p_und_r/collections/p_und_r/items",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("park_and_ride.geojson"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[ParkAndRide] = await client.park_and_ride()
        assert spaces is not None
        for item in spaces:
            assert item.spot_id is not None
            assert item.address is not None
            assert isinstance(item.tickets, dict)
            assert isinstance(item.longitude, float)
            assert isinstance(item.latitude, float)
