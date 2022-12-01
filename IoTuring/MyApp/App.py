import inspect
from IoTuring.Logger.Logger import Logger
from importlib_metadata import metadata
import os


class App():
    METADATA = metadata('IoTuring')

    NAME = METADATA['Name']
    DESCRIPTION = METADATA['Summary']
    VENDOR = METADATA['Maintainer-email'].split(' <')[0]
    VERSION = METADATA['Version']

    @staticmethod
    def getName() -> str:
        return App.NAME

    @staticmethod
    def getVendor() -> str:
        return App.VENDOR

    @staticmethod
    def getDescription() -> str:
        return App.DESCRIPTION

    @staticmethod
    def getVersion() -> str:
        return App.VERSION

    def __str__(self) -> str:
        msg = ""
        msg += "Name: " + App.getName() + "\n"
        msg += "Version: " + App.getVersion() + "\n"
        msg += "Description: " + App.getDescription() + "\n"
        return msg
