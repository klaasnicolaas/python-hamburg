"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

from dataclasses import dataclass
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
