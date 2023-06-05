"""Asynchronous Python client providing Urban Data information of Hamburg."""


class UDPHamburgError(Exception):
    """Generic Urban Data Platform Hamburg exception."""


class UDPHamburgConnectionError(UDPHamburgError):
    """Urban Data Platform Hamburg - connection error."""
