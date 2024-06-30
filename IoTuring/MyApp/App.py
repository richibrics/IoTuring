from importlib.metadata import metadata
from pathlib import Path

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
    URLS = METADATA.get_all("Project-URL") or ""
    URL_HOMEPAGE = URLS[0].split(', ')[1].strip()
    URL_RELEASES = URLS[-1].split(', ')[1].strip()

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

    @staticmethod
    def getRootPath() -> Path:
        """Get the project root path

        Returns:
            Path: The path to th project root as a pathlib.Path
        """
        return Path(__file__).parents[1]

    def __str__(self) -> str:
        msg = ""
        msg += "Name: " + App.getName() + "\n"
        msg += "Version: " + App.getVersion() + "\n"
        msg += "Description: " + App.getDescription() + "\n"
        return msg
