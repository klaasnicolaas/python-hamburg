"""Asynchronous Python client providing Urban Data information of Hamburg."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self, cast

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import UDPHamburgConnectionError, UDPHamburgError
from .models import DisabledParking, Garage, ParkAndRide

VERSION = metadata.version(__package__)


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

        return cast(dict[str, Any], await response.json())

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
