"""Test the models."""
from __future__ import annotations

from datetime import datetime

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
        for item in spaces:
            assert isinstance(item, DisabledParking)
            assert item.spot_id is not None
            assert item.street is None or isinstance(item.street, str)
            assert item.limitation is None or isinstance(item.limitation, str)
            assert item.longitude is not None
            assert item.latitude is not None


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
        for item in spaces:
            assert item.spot_id is not None
            assert item.address is not None
            assert item.availability_pct is not None
            assert item.updated_at is not None
            assert isinstance(item.tickets, dict)
            assert isinstance(item.longitude, float)
            assert isinstance(item.latitude, float)
            assert isinstance(item.updated_at, datetime)


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
        for item in spaces:
            assert item.spot_id is not None
            assert item.name is not None
            assert item.status in [
                "frei",
                "nahezu belegt",
                "besetzt",
                "keine Auslastungsdaten",
            ]
            assert item.address is not None
            assert isinstance(item.longitude, float)
            assert isinstance(item.latitude, float)
            assert isinstance(item.updated_at, datetime) or item.updated_at is None


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
        for item in spaces:
            assert item.spot_id is not None
            assert item.name is not None
            assert item.status in [
                "frei",
                "nahezu belegt",
                "besetzt",
                "keine Auslastungsdaten",
            ]
            assert item.address is not None
            assert item.capacity is None or item.capacity >= 0
            assert isinstance(item.longitude, float)
            assert isinstance(item.latitude, float)
            assert isinstance(item.updated_at, datetime) or item.updated_at is None
