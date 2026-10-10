"""Asynchronous Python client providing Urban Data information of Hamburg."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import UDPHamburgConnectionError, UDPHamburgError
from .models import DisabledParking, Garage, ParkAndRide, ParkAndRideCollection

VERSION = metadata.version("hamburg")


@dataclass
class UDPHamburg:
    """Main class for handling data fetching from Urban Data Platform of Hamburg."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Urban Data Platform API of Hamburg.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (text) with the response from
            the Urban Data Platform API.

        Raises:
        ------
            UDPHamburgConnectionError: Timeout occurred while
                connecting to the Urban Data Platform API.
            UDPHamburgError: If the data is not valid.

        """
        url = URL.build(
            scheme="https",
            host="api.hamburg.de",
            path="/datasets/v1/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/geo+json",
            "User-Agent": f"PythonUDPHamburg/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Urban Data Platform API."
            raise UDPHamburgConnectionError(
                msg,
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with Urban Data Platform API."
            raise UDPHamburgConnectionError(
                msg,
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/geo+json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Urban Data Platform API"
            raise UDPHamburgError(
                msg,
                {"Content-Type": content_type, "Response": text},
            )

        return await response.json()

    async def disabled_parkings(
        self,
        limit: int = 10,
    ) -> list[DisabledParking]:
        """Get all disabled parking spaces.

        Args:
        ----
            limit: Number of items to return.

        Returns:
        -------
            A list of DisabledParking objects.

        """
        locations = await self._request(
            "behindertenstellplaetze/collections/verkehr_behindertenparkpl/items",
            params={"limit": limit},
        )
        return [DisabledParking.from_dict(item) for item in locations["features"]]

    async def park_and_rides(
        self,
        limit: int = 10,
    ) -> list[ParkAndRide]:
        """Get all park and ride spaces.

        Args:
        ----
            limit: Number of items to return.

        Returns:
        -------
            A list of ParkAndRide objects.

        """
        locations = await self._request(
            "p_und_r/collections/p_und_r/items",
            params={"limit": limit},
        )
        return [ParkAndRide.from_dict(item) for item in locations["features"]]

    async def park_and_ride_collection(
        self, *, max_records: int = 10000
    ) -> ParkAndRideCollection:
        """Retrieve the full P+R selection; a safety ceiling never truncates it.

        Validate counts and IDs across offset pages. No source-wide transactional
        revision is available, so this proves pagination completeness, not an
        atomic observation of every facility at the same instant.
        """
        if type(max_records) is not int or max_records < 1:
            msg = "max_records must be positive"
            raise ValueError(msg)
        records: list[ParkAndRide] = []
        identifiers: set[str] = set()
        total: int | None = None
        pages = 0
        while True:
            data = await self._request(
                "p_und_r/collections/p_und_r/items",
                params={"limit": min(1000, max_records), "offset": len(records)},
            )
            count = data.get("numberMatched")
            features = data.get("features")
            if (
                type(count) is not int
                or not 0 <= count <= max_records
                or not isinstance(features, list)
                or type(data.get("numberReturned")) is not int
                or data["numberReturned"] != len(features)
                or (total is not None and count != total)
            ):
                msg = "Invalid or changed P+R collection count"
                raise UDPHamburgError(msg)
            total = count
            pages += 1
            for feature in features:
                identifier = feature.get("id")
                if (
                    isinstance(identifier, bool)
                    or not isinstance(identifier, (str, int))
                    or not str(identifier).strip()
                    or str(identifier) in identifiers
                ):
                    msg = "Missing or duplicate P+R source ID"
                    raise UDPHamburgError(msg)
                identifiers.add(str(identifier))
                records.append(ParkAndRide.from_dict(feature))
            if len(records) == total:
                return ParkAndRideCollection(records, total, pages, complete=True)
            if not features or len(records) > total:
                msg = "Incomplete P+R collection"
                raise UDPHamburgError(msg)

    async def garages(
        self,
        limit: int = 10,
        set_filter: str | None = None,
    ) -> list[Garage]:
        """Get all garages.

        Args:
        ----
            limit: Number of items to return.
            set_filter: Filter the garages by a defined filter expression.

        Returns:
        -------
            A list of Garage objects.

        """
        params: dict[str, Any] = {"limit": limit}

        if set_filter is not None:
            params["filter"] = str(set_filter)

        locations = await self._request(
            "parkhaeuser/collections/verkehr_parkhaeuser/items",
            params=params,
        )

        # By default filter out garages without location coordinates.
        return [
            Garage.from_dict(item)
            for item in locations["features"]
            if item["geometry"] is not None
        ]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Urban Data Platform object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
