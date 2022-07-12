"""Asynchronous Python client providing Urban Data information of Hamburg."""


class UDPError(Exception):
    """Generic Urban Data Platform Hamburg exception."""


class UDPConnectionError(UDPError):
    """Urban Data Platform Hamburg - connection error."""


class UDPResultsError(UDPError):
    """Urban Data Platform Hamburg - results error."""
