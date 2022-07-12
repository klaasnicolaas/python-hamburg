"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from hamburg import DisabledParking, UDPHamburg

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
            text=load_fixtures("parking_hamburg.geojson"),
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
            assert item.longitude is not None
            assert item.latitude is not None
