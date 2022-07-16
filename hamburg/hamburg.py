"""Asynchronous Python client providing Urban Data information of Hamburg."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import aiohttp
import async_timeout
from aiohttp import hdrs
from yarl import URL

from .exceptions import UDPHamburgConnectionError, UDPHamburgError
from .models import DisabledParking, ParkAndRide


@dataclass
class UDPHamburg:
    """Main class for handling data fetchting from Urban Data Platform of Hamburg."""

    request_timeout: float = 10.0
    session: aiohttp.client.ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = hdrs.METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Urban Data Platform API of Hamburg.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (text) with the response from
            the Urban Data Platform API.

        Raises:
            UDPHamburgConnectionError: Timeout occurred while
                connecting to the Urban Data Platform API.
            UDPHamburgError: If the data is not valid.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https", host="api.hamburg.de", path="/datasets/v1/"
        ).join(URL(uri))

        headers = {
            "Accept": "application/geo+json",
            "User-Agent": f"PythonUDPHamburg/{version}",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise UDPHamburgConnectionError(
                "Timeout occurred while connecting to the Urban Data Platform API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise UDPHamburgConnectionError(
                "Error occurred while communicating with Urban Data Platform API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/geo+json" not in content_type:
            text = await response.text()
            raise UDPHamburgError(
                "Unexpected content type response from the Urban Data Platform API",
                {"Content-Type": content_type, "Response": text},
            )

        return await response.json()

    async def disabled_parkings(
        self, limit: int = 10, bulk: str = "false"
    ) -> list[DisabledParking]:
        """Get all disabled parking spaces.

        Args:
            limit: Number of items to return.
            bulk: Whether to return all items or the limit.

        Returns:
            A list of DisabledParking objects.
        """

        results: list[DisabledParking] = []
        locations = await self._request(
            "behindertenstellplaetze/collections/verkehr_behindertenparkpl/items",
            params={"limit": limit, "bulk": bulk},
        )

        for item in locations["features"]:
            results.append(DisabledParking.from_dict(item))
        return results

    async def park_and_rides(
        self, limit: int = 10, bulk: str = "false"
    ) -> list[ParkAndRide]:
        """Get all park and ride spaces.

        Args:
            limit: Number of items to return.
            bulk: Whether to return all items or the limit.

        Returns:
            A list of ParkAndRide objects.
        """
        results: list[ParkAndRide] = []
        locations = await self._request(
            "p_und_r/collections/p_und_r/items",
            params={"limit": limit, "bulk": bulk},
        )
        for item in locations["features"]:
            results.append(ParkAndRide.from_dict(item))
        return results

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> UDPHamburg:
        """Async enter.

        Returns:
            The Urban Data Platform object.
        """
        return self

    async def __aexit__(self, *_exc_info: str) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()
