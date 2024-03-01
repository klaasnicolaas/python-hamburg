"""Test the models."""

from __future__ import annotations

from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from hamburg import DisabledParking, Garage, ParkAndRide, UDPHamburg

from . import load_fixtures


async def test_all_parking_spaces(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    hamburg_client: UDPHamburg,
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
    spaces: list[DisabledParking] = await hamburg_client.disabled_parkings()
    assert spaces == snapshot
    for item in spaces:
        assert isinstance(item, DisabledParking)
        assert item.street is None or isinstance(item.street, str)
        assert item.limitation is None or isinstance(item.limitation, str)


async def test_park_and_rides(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    hamburg_client: UDPHamburg,
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
    spaces: list[ParkAndRide] = await hamburg_client.park_and_rides()
    assert spaces == snapshot


async def test_garages(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    hamburg_client: UDPHamburg,
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
    spaces: list[Garage] = await hamburg_client.garages()
    assert spaces == snapshot
    for item in spaces:
        assert isinstance(item, Garage)


async def test_garages_live_data(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    hamburg_client: UDPHamburg,
) -> None:
    """Test park and ride spaces function."""
    aresponses.add(
        "api.hamburg.de",
        "/datasets/v1/parkhaeuser/collections/verkehr_parkhaeuser/items",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/geo+json"},
            text=load_fixtures("garages_live.geojson"),
        ),
    )
    spaces: list[Garage] = await hamburg_client.garages(set_filter="frei>=0")
    assert spaces == snapshot
    for item in spaces:
        assert isinstance(item, Garage)
