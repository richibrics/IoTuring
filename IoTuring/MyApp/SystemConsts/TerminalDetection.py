import sys
import os
import shutil


class TerminalDetection:
    @staticmethod
    def CheckTerminalSupportsColors() -> bool:
        """
        Returns True if the running system's terminal supports color, and False
        otherwise.
        """
        plat = sys.platform
        supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                      'ANSICON' in os.environ)
        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported_platform and is_a_tty

    @staticmethod
    def CheckTerminalSupportsSize() -> bool:
        return any(shutil.get_terminal_size(fallback=(0,0)))


    @staticmethod
    def GetTerminalLines() -> int:
        return shutil.get_terminal_size().lines

    @staticmethod
    def GetTerminalColumns() -> int:
        return shutil.get_terminal_size().columns


    @staticmethod
    def CalculateNumberOfLines(string_length: int) -> int:
        """Get the number of lines required to display a text with the given length

        Args:
            string_length (int): Length of the text

        Returns:
            int: Number of lines required
        """
        return (string_length // shutil.get_terminal_size().columns) + 1
