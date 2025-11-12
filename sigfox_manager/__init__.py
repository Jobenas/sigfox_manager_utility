"""
Sigfox Manager - A Python library for handling Sigfox API operations.

This library provides a simple interface to interact with the Sigfox API,
allowing you to manage devices, contracts, and messages.
"""

__version__ = "0.2.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main classes for easy access
from .sigfox_manager import SigfoxManager
from .models.schemas import (
    ContractsResponse,
    DevicesResponse,
    Device,
    DeviceMessagesResponse,
    DeviceMessageStats,
    BaseDevice,
    ErrorResponse,
    DeviceType,
    DeviceTypesResponse,
)
from .sigfox_manager_exceptions.sigfox_exceptions import (
    SigfoxAPIException,
    SigfoxDeviceNotFoundError,
    SigfoxAuthError,
    SigfoxDeviceCreateConflictException,
    SigfoxDeviceTypeNotFoundException,
)

# Define what gets imported with "from sigfox_manager import *"
__all__ = [
    "SigfoxManager",
    "ContractsResponse",
    "DevicesResponse",
    "Device",
    "DeviceMessagesResponse",
    "DeviceMessageStats",
    "BaseDevice",
    "ErrorResponse",
    "DeviceType",
    "DeviceTypesResponse",
    "SigfoxAPIException",
    "SigfoxDeviceNotFoundError",
    "SigfoxAuthError",
    "SigfoxDeviceCreateConflictException",
    "SigfoxDeviceTypeNotFoundException",
]
