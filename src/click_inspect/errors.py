import textwrap


class UnsupportedDocstringStyle(Exception):
    MAX_WIDTH = 79

    def __init__(self, doc: str):
        width = self.MAX_WIDTH - len(self.__class__.__name__) - 2  # Account for ": ".
        super().__init__(textwrap.shorten(doc, width=width, placeholder='...'))


class UnsupportedTypeHint(Exception):
    pass
