from __future__ import annotations

from collections import defaultdict
import inspect

from sphinx.ext.napoleon import Config, GoogleDocstring, NumpyDocstring

from .errors import UnsupportedDocstringStyle


CONFIG = Config(napoleon_use_param=True)
GOOGLE_HEADER = 'Args:'
NUMPY_HEADER = 'Parameters\n----------'


def parse_docstring(doc: str) -> dict[str, dict[str, str]]:
    doc = inspect.cleandoc(doc)
    if NUMPY_HEADER in doc:
        lines = NumpyDocstring(doc, config=CONFIG).lines()
    elif GOOGLE_HEADER in doc:
        lines = GoogleDocstring(doc, config=CONFIG).lines()
    elif ':param' in doc:  # reST-style
        lines = doc.splitlines()
    else:
        raise UnsupportedDocstringStyle(doc)
    parameters = defaultdict(dict)
    for line in lines:
        if line.startswith(':param '):
            name, parameters[name]['help'] = _find_name_and_remainder(line)
        elif line.startswith(':type'):
            name, type_string = _find_name_and_remainder(line)
            parameters[name]['type'] = _parse_type_string(type_string)
    return parameters


def _find_name_and_remainder(s):
    assert s.startswith(':')
    j = s.find(' ') + 1
    k = s.find(':', 1)
    return s[j:k], s[k+1:].lstrip()


def _parse_type_string(s):
    candidates = s.split(' or ')
    candidates = [x.split(' of ')[0] for x in candidates]
    return candidates
