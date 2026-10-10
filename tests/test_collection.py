"""Complete source retrieval and source-time regression coverage."""

from datetime import UTC
from unittest.mock import AsyncMock, patch

import pytest

from hamburg import Collection, DisabledParking, UDPHamburg
from hamburg.exceptions import UDPHamburgError
from hamburg.models import ParkAndRide


def feature(identifier: object = 1) -> dict:
    """Make a small source feature, including absent measurements."""
    return {
        "id": identifier,
        "geometry": {"type": "Point", "coordinates": [10.0, 53.6]},
        "properties": {
            "name": "Example",
            "nahe_adresse": "Example street",
            "befristung": None,
            "anzahl": 2,
            "art": "Parkhaus",
            "stellplaetze_gesamt": "120",
            "stellplaetze_frei": None,
            "stellplaetze_behinderte_gesamt": None,
            "aktualitaet_belegungsdaten": "2026-10-10  22:00:00",
        },
    }


def page(*identifiers: object, total: int = 2) -> dict:
    """Return count-qualified GeoJSON."""
    return {
        "numberMatched": total,
        "numberReturned": len(identifiers),
        "features": [feature(identifier) for identifier in identifiers],
    }


@pytest.mark.parametrize(
    "method", ["park_and_ride_collection", "disabled_parking_collection"]
)
async def test_collects_all_pages_with_original_ids(method: str) -> None:
    """A short first page must not be treated as a complete selection."""
    async with UDPHamburg() as client:
        with patch.object(
            UDPHamburg, "_request", AsyncMock(side_effect=[page(1), page(2)])
        ) as request:
            result = await getattr(client, method)()
    expected_type = (
        ParkAndRide if method == "park_and_ride_collection" else DisabledParking
    )
    assert all(isinstance(record, expected_type) for record in result.records)
    expected_uri = (
        "p_und_r/collections/p_und_r/items"
        if method == "park_and_ride_collection"
        else "behindertenstellplaetze/collections/behindertenstellplaetze/items"
    )
    assert request.await_args_list[0].args == (expected_uri,)
    assert isinstance(result, Collection)
    assert [record.spot_id for record in result.records] == ["1", "2"]
    assert result.total_count == 2
    assert result.pages_fetched == 2
    assert result.complete is True
    assert request.await_args_list[1].kwargs["params"] == {"limit": 1000, "offset": 1}


@pytest.mark.parametrize(
    "pages",
    [
        [page(1), page(1)],
        [page(1), page(total=2)],
        [page(1), page(2, total=3)],
        [page(None, total=1)],
        [page("", total=1)],
        [page(True, total=1)],  # noqa: FBT003 - deliberately invalid source ID
        [{"features": [], "numberReturned": 0}],
        [{"features": [feature()], "numberMatched": 1, "numberReturned": 0}],
    ],
)
@pytest.mark.parametrize(
    "method", ["park_and_ride_collection", "disabled_parking_collection"]
)
async def test_rejects_invalid_or_incomplete_collections(
    pages: list[dict], method: str
) -> None:
    """No duplicate, missing, changing or partial result is declared complete."""
    async with UDPHamburg() as client:
        with (
            patch.object(UDPHamburg, "_request", AsyncMock(side_effect=pages)),
            pytest.raises(UDPHamburgError),
        ):
            await getattr(client, method)()


@pytest.mark.parametrize(
    "method", ["park_and_ride_collection", "disabled_parking_collection"]
)
async def test_ceiling_rejects_instead_of_truncating(method: str) -> None:
    """A bounded request cannot silently hide additional facilities."""
    async with UDPHamburg() as client:
        with (
            patch.object(UDPHamburg, "_request", AsyncMock(return_value=page(1))),
            pytest.raises(UDPHamburgError),
        ):
            await getattr(client, method)(max_records=1)


@pytest.mark.parametrize("ceiling", [0, -1, True])
@pytest.mark.parametrize(
    "method", ["park_and_ride_collection", "disabled_parking_collection"]
)
async def test_invalid_ceiling(ceiling: int, method: str) -> None:
    """Reject invalid limits before source access."""
    async with UDPHamburg() as client:
        with (
            patch.object(UDPHamburg, "_request", AsyncMock()) as request,
            pytest.raises(ValueError, match="positive"),
        ):
            await getattr(client, method)(max_records=ceiling)
    request.assert_not_awaited()


def test_missing_counts_and_local_measurement_time() -> None:
    """Absent counts stay absent and Berlin summer time converts correctly."""
    record = ParkAndRide.from_dict(feature())
    assert record.free_space is None
    assert record.disabled_parking_spaces is None
    assert record.capacity == 120
    assert record.updated_at is not None
    assert record.updated_at.astimezone(UTC).isoformat() == "2026-10-10T20:00:00+00:00"


@pytest.mark.parametrize(
    "source_time", ["2026-10-25 02:30:00", "2026-03-29 02:30:00", None, "invalid"]
)
def test_unknown_or_ambiguous_source_time(source_time: str | None) -> None:
    """DST ambiguity or missing time cannot become a guessed current measurement."""
    data = feature()
    data["properties"]["aktualitaet_belegungsdaten"] = source_time
    assert ParkAndRide.from_dict(data).updated_at is None


@pytest.mark.parametrize(("value", "error"), [(True, TypeError), (-1, ValueError)])
def test_rejects_invalid_source_counts(value: object, error: type[Exception]) -> None:
    """Boolean and negative source counts cannot become valid occupancy."""
    data = feature()
    data["properties"]["stellplaetze_frei"] = value
    with pytest.raises(error):
        ParkAndRide.from_dict(data)


def test_collection_supports_other_source_record_types() -> None:
    """The collection envelope also carries disabled-parking source records."""
    record = DisabledParking("original-id", "Example", None, 1, 10.0, 53.6)
    result: Collection[DisabledParking] = Collection([record], 1, 1, complete=True)
    assert result.records[0] is record
    assert result.total_count == 1
    assert result.pages_fetched == 1
    assert result.complete is True
