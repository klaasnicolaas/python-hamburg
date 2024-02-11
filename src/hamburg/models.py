"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytz


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
    def from_dict(cls: type[DisabledParking], data: dict[str, Any]) -> DisabledParking:
        """Return a DisabledParking object from a dictionary.

        Args:
        ----
            data: The data from the API.

        Returns:
        -------
            A DisabledParking object.

        """

        def strip_spaces(string: str) -> str | None:
            """Strip spaces from a string.

            Args:
            ----
                string: The string to strip.

            Returns:
            -------
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
    park_type: str
    address: str
    construction_year: int
    public_transport_line: str
    disabled_parking_spaces: int
    tickets: dict[str, int]
    url: str

    free_space: int
    capacity: int
    availability_pct: float | None

    longitude: float
    latitude: float
    updated_at: datetime

    @classmethod
    def from_dict(cls: type[ParkAndRide], data: dict[str, Any]) -> ParkAndRide:
        """Return a ParkAndRide object from a dictionary.

        Args:
        ----
            data: The data from the API.

        Returns:
        -------
            A ParkAndRide object.

        """
        attr = data["properties"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=str(data.get("id")),
            name=attr.get("name"),
            park_type=attr.get("art"),
            address=attr.get("adresse"),
            construction_year=attr.get("baujahr"),
            public_transport_line=attr.get("linie"),
            disabled_parking_spaces=int(attr.get("stellplaetze_behinderte_gesamt")),
            tickets={
                "day": attr.get("ticket_1_tag"),
                "month": attr.get("ticket_30_tage"),
                "year": attr.get("ticket_1_jahr"),
            },
            url=attr.get("homepage"),
            free_space=int(attr.get("stellplaetze_frei")),
            capacity=int(attr.get("stellplaetze_gesamt")),
            availability_pct=availability_calc(
                attr.get("stellplaetze_frei"),
                attr.get("stellplaetze_gesamt"),
            ),
            longitude=geo[0],
            latitude=geo[1],
            updated_at=strptime(
                attr.get("aktualitaet_belegungsdaten"), "%Y-%m-%d %H:%M:%S"
            ),
        )


@dataclass
class Garage:
    """Object representing a garage."""

    spot_id: str
    name: str
    park_type: str
    disabled_parking_spaces: int | None
    status: str
    address: str | None
    price: str | None
    data_origin: str | None

    free_space: int | None
    capacity: int | None
    availability_pct: float | None

    longitude: float
    latitude: float
    updated_at: datetime | None

    @classmethod
    def from_dict(cls: type[Garage], data: dict[str, Any]) -> Garage:
        """Return a Garage object from a dictionary.

        Args:
        ----
            data: The data from the API.

        Returns:
        -------
            A Garage object.

        """
        attr = data["properties"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=str(data.get("id")),
            name=attr.get("name"),
            park_type=attr.get("art"),
            disabled_parking_spaces=attr.get("behindertenst"),
            status=attr.get("situation"),
            address=f"{attr.get('strasse')} {attr.get('hausnr')}"
            if attr.get("strasse")
            else None,
            price=None if attr.get("preise") == " " else attr.get("preise"),
            data_origin=attr.get("datenherkunft"),
            free_space=attr.get("frei"),
            capacity=attr.get("stellplaetze_gesamt"),
            availability_pct=availability_calc(
                attr.get("frei"),
                attr.get("stellplaetze_gesamt"),
            ),
            longitude=geo[0],
            latitude=geo[1],
            updated_at=strptime(attr.get("received"), "%d.%m.%Y, %H:%M"),
        )


def availability_calc(
    free_space: int,
    capacity: int,
    default: None = None,
) -> float | None:
    """Calculate the availability percentage.

    Args:
    ----
        free_space: The free space.
        capacity: The capacity.
        default: The default value.

    Returns:
    -------
        The availability percentage.

    """
    try:
        return round(
            (float(free_space) / float(capacity)) * 100,
            1,
        )
    except TypeError:
        return default
    except ZeroDivisionError:
        return None


def strptime(date_string: str, date_format: str, default: None = None) -> Any:
    """Strptime function with default value.

    Args:
    ----
        date_string: The date string.
        date_format: The format of the date string.
        default: The default value.

    Returns:
    -------
        The datetime object.

    """
    try:
        return datetime.strptime(date_string, date_format).replace(
            tzinfo=pytz.timezone("Europe/Berlin")
        )
    except (ValueError, TypeError):
        return default
