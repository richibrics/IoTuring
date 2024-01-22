import re
import platform
import time
import logging
from ctypes import *
from ctypes.wintypes import *
from comtypes import GUID

from .const import *
from .profile import Profile

ERROR_SUCCESS = 0
CLIENT_VERSION = 2

native_wifi = windll.wlanapi

class WLAN_INTERFACE_INFO(Structure):

    _fields_ = [
        ("InterfaceGuid", GUID),
        ("strInterfaceDescription", c_wchar * 256),
        ("isState", c_uint)
    ]

def _wlan_open_handle(self, client_version, _nego_version, handle):

    func = native_wifi.WlanOpenHandle
    func.argtypes = [DWORD, c_void_p, POINTER(DWORD), POINTER(HANDLE)]
    func.restypes = [DWORD]
    return func(client_version, None, _nego_version, handle)

def _wlan_enum_interfaces(self, handle, ifaces):

    func = native_wifi.WlanEnumInterfaces
    func.argtypes = [HANDLE, c_void_p, POINTER(
        POINTER(WLAN_INTERFACE_INFO_LIST))]
    func.restypes = [DWORD]
    return func(handle, None, ifaces)

def interfaces(self):
    """Get the wifi interface lists."""

    ifaces = []

    if self._wlan_open_handle(CLIENT_VERSION,
                                byref(self._nego_version),
                                byref(self._handle)) \
        is not ERROR_SUCCESS:
        self._logger.error("Open handle failed!")

    if self._wlan_enum_interfaces(self._handle, byref(self._ifaces)) \
        is not ERROR_SUCCESS:
        self._logger.error("Enum interface failed!")

    interfaces = cast(self._ifaces.contents.InterfaceInfo,
                    POINTER(WLAN_INTERFACE_INFO))
    for i in range(0, self._ifaces.contents.dwNumberOfItems):
        iface = {}
        iface['guid'] = interfaces[i].InterfaceGuid
        iface['name'] = interfaces[i].strInterfaceDescription
        ifaces.append(iface)

    return ifaces