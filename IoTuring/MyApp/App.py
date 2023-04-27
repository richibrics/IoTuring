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
    
    # "Project-URL": "homepage, https://github.com/richibrics/IoTuring",
    # "Project-URL": "documentation, https://github.com/richibrics/IoTuring",
    # "Project-URL": "repository, https://github.com/richibrics/IoTuring",
    # "Project-URL": "changelog, https://github.com/richibrics/IoTuring/releases",
    URL_HOMEPAGE = METADATA.get_all("Project-URL")[0].split(', ')[1].strip()
    URL_RELEASES = METADATA.get_all("Project-URL")[-1].split(', ')[1].strip()

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
    
    @staticmethod
    def getUrlHomepage() -> str:
        return App.URL_HOMEPAGE

    @staticmethod
    def getUrlReleases() -> str:
        return App.URL_RELEASES

    def __str__(self) -> str:
        msg = ""
        msg += "Name: " + App.getName() + "\n"
        msg += "Version: " + App.getVersion() + "\n"
        msg += "Description: " + App.getDescription() + "\n"
        return msg
