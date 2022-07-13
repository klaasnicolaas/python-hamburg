"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DisabledParking:
    """Object representing a disabled parking."""

    spot_id: str
    street: str | None
    limitation: str | None
    number: int
    longitude: float
    latitude: float

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> DisabledParking:
        """Return a DisabledParking object from a JSON dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
            A DisabledParking object.
        """

        def strip_spaces(string: str) -> str | None:
            """Strip spaces from a string.

            Args:
                string: The string to strip.

            Returns:
                The string without spaces or None if the string is empty.
            """
            if string is None:
                return None
            return string.strip()

        attr = data["properties"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=str(data.get("id")),
            street=strip_spaces(attr.get("nahe_adresse")),
            limitation=strip_spaces(attr.get("befristung")),
            number=attr.get("anzahl"),
            longitude=geo[0],
            latitude=geo[1],
        )


@dataclass
class ParkAndRide:
    """Object representing a park and ride spot."""

    spot_id: str
    name: str
    construction_year: int
    address: str
    public_transport_line: str
    park_type: str
    free_space: int
    capacity: int
    occupancy_percentage: float
    disabled_parking_spaces: int
    tickets: dict[str, int]
    longitude: float
    latitude: float
    updated_at: datetime

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ParkAndRide:
        """Return a ParkAndRide object from a JSON dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
            A ParkAndRide object.
        """

        attr = data["properties"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=str(data.get("id")),
            name=attr.get("name"),
            construction_year=attr.get("baujahr"),
            address=attr.get("adresse"),
            public_transport_line=attr.get("linie"),
            park_type=attr.get("art"),
            free_space=attr.get("stellplaetze_frei"),
            capacity=attr.get("stellplaetze_gesamt"),
            occupancy_percentage=round(attr.get("stellpl_frei_in_prozent"), 2),
            disabled_parking_spaces=attr.get("stellplaetze_behinderte_gesamt"),
            tickets={
                "day": attr.get("ticket_1_tag"),
                "month": attr.get("ticket_30_tage"),
                "year": attr.get("ticket_1_jahr"),
            },
            longitude=geo[0],
            latitude=geo[1],
            updated_at=datetime.strptime(
                attr.get("aktualitaet_belegungsdaten"), "%Y-%m-%d %H:%M:%S"
            ),
        )
