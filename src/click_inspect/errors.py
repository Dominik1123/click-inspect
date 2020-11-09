import textwrap


class UnsupportedDocstringStyle(Exception):
    """Use this error if a docstring cannot be parsed into its parameters."""

    MAX_WIDTH = 79

    def __init__(self, doc: str):
        width = self.MAX_WIDTH - len(self.__class__.__name__) - 2  # Account for ": ".
        super().__init__(textwrap.shorten(doc, width=width, placeholder='...'))
