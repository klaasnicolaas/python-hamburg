"""Test the models."""
from __future__ import annotations

from aiohttp import ClientSession
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from hamburg import DisabledParking, Garage, ParkAndRide, UDPHamburg

from . import load_fixtures


async def test_all_parking_spaces(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
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
    async with ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[DisabledParking] = await client.disabled_parkings()
        assert spaces == snapshot


async def test_park_and_rides(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
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
    async with ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[ParkAndRide] = await client.park_and_rides()
        assert spaces == snapshot


async def test_garages(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test park and ride spaces function."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/parkhaeuser/collections/verkehr_parkhaeuser/items",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("garages.geojson"),
        ),
    )
    async with ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[Garage] = await client.garages()
        assert spaces == snapshot


async def test_garages_live_data(
    aresponses: ResponsesMockServer, snapshot: SnapshotAssertion
) -> None:
    """Test park and ride spaces function."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/parkhaeuser/collections/verkehr_parkhaeuser/items",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("garages.geojson"),
        ),
    )
    async with ClientSession() as session:
        client = UDPHamburg(session=session)
        spaces: list[Garage] = await client.garages(available=">=0")
        assert spaces == snapshot
