"""Exceptions for Parking Hamburg."""


class UDPError(Exception):
    """Generic Parking Hamburg exception."""


class UDPConnectionError(UDPError):
    """Parking Hamburg - connection error."""


class UDPResultsError(UDPError):
    """Parking Hamburg - results error."""