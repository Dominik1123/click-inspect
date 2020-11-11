from __future__ import annotations

from collections import defaultdict
import inspect
from typing import Any, Container, DefaultDict, Dict
import warnings

from sphinx.ext.napoleon import Config, GoogleDocstring, NumpyDocstring  # type: ignore
from typestring_parser import parse as typstr_parse                      # type: ignore
from typestring_parser.errors import UnsupportedTypeString               # type: ignore

from .errors import UnsupportedDocstringStyle


CONFIG = Config(napoleon_use_param=True)
GOOGLE_HEADER = 'Args:'
NUMPY_HEADER = 'Parameters\n----------'


def parse_docstring(obj, *, ignore: Container[str] = frozenset()) -> Dict[str, Dict[str, Any]]:
    """Parse the given docstring or the given obj's docstring.

    Args:
        obj (function or str): Parse the docstring from the given object.
        ignore (set): Ignore the type hint string of those parameters.

    Returns:
        DefaultDict: Per parameter specification containing 'help' and 'type' (if provided).

    Raises:
        UnsupportedDocstringStyle: If the given docstring contains no parameter section.
    """
    if isinstance(obj, str):
        doc, func = inspect.cleandoc(obj), None
    else:
        doc, func = inspect.getdoc(obj), obj  # type: ignore
        if doc is None:
            return defaultdict(dict)
    if NUMPY_HEADER in doc:
        lines = NumpyDocstring(doc, config=CONFIG).lines()
    elif GOOGLE_HEADER in doc:
        lines = GoogleDocstring(doc, config=CONFIG).lines()
    elif ':param' in doc:  # reST-style
        lines = doc.splitlines()
    else:
        raise UnsupportedDocstringStyle(doc)
    parameters: DefaultDict[str, Dict[str, Any]] = defaultdict(dict)
    for line in lines:
        if line.startswith(':param '):
            name, parameters[name]['help'] = _find_name_and_remainder(line)
        elif line.startswith(':type'):
            name, type_string = _find_name_and_remainder(line)
            if name in ignore:
                continue
            try:
                parameters[name]['type'] = typstr_parse(type_string, func=func)
            except NameError as err:
                _name = str(err).split("'")[1]
                warnings.warn(f'Type hint {_name!r} cannot be resolved. '
                               'Continuing as if no type information was provided.')
            except UnsupportedTypeString:
                pass
    return parameters


def _find_name_and_remainder(s):
    assert s.startswith(':')
    j = s.find(' ') + 1
    k = s.find(':', 1)
    return s[j:k], s[k+1:].lstrip()
