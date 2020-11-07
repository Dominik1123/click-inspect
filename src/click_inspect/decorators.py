from __future__ import annotations

import builtins
from collections import defaultdict
import inspect
from inspect import Parameter
import re
from typing import get_type_hints, Sequence
try:
    from typing import get_args, get_origin
except ImportError:                                     # pragma: no cover
    from typing_extensions import get_args, get_origin  # pragma: no cover
import warnings

import click

from .errors import UnsupportedDocstringStyle, UnsupportedTypeHint
from .parser import parse_docstring


POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
KEYWORD_ONLY = Parameter.KEYWORD_ONLY
EMPTY = Parameter.empty


def add_options_from(func,
                     *,
                     names: dict[str, Sequence[str]] = None,
                     include: set[str] = None,
                     exclude: set[str] = None,
                     custom: [dict[str, dict]] = None):
    """Inspect `func` and add corresponding options to the decorated command.

    Args:
        func (callable): The function which provides the options through inspection.
        names (dict): Map parameter names in `func` to `click.option` names.
        include (set): Parameter names to be used from `func`.
        exclude (set): Parameter names to be excluded from `func`.
        custom (dict): Map parameter names to custom kwargs for the corresponding option.
    """
    include = include or set()
    names = names or {}
    custom = custom or {}
    try:
        p_doc = parse_docstring(func.__doc__ or '')
    except UnsupportedDocstringStyle:
        p_doc = defaultdict(dict)
    type_hints = get_type_hints(func)
    parameters = inspect.signature(func).parameters
    to_be_used = (include or parameters.keys()) - (exclude or set())
    parameters = [(name, parameter) for name, parameter in parameters.items() 
                  if name in to_be_used]

    def _decorator(f):
        for name, parameter in reversed(parameters):
            has_default = parameter.default is not EMPTY
            condition = (  # Whether to use this parameter or not.
                name in include
                or parameter.kind is KEYWORD_ONLY
                or parameter.kind is POSITIONAL_OR_KEYWORD and has_default
            )
            if condition:
                try:
                    opt_names = names[name]
                except KeyError:
                    opt_names = f'--{name.replace("_", "-")}',

                kwargs = {}
                if 'help' in p_doc[name]:
                    kwargs['help'] = p_doc[name]['help']

                if has_default:
                    kwargs['default'] = parameter.default
                else:
                    kwargs['required'] = True

                    if parameter.annotation is not EMPTY:
                        tp = type_hints[name]
                        kwargs['type'] = get_origin(tp) or tp
                    else:
                        tp_candidates = p_doc[name].get('type', ())
                        try:
                            kwargs['type'] = getattr(builtins, tp_candidates[0])
                        except IndexError:
                            warnings.warn(f'No type hint for parameter {name!r}')
                        except AttributeError:
                            msg = f'{tp_candidates[0]} (only builtin types are supported)'
                            raise UnsupportedTypeHint(msg) from None
                kwargs.update(custom.get(name, {}))
                click.option(*opt_names, **kwargs)(f)
        return f

    return _decorator
