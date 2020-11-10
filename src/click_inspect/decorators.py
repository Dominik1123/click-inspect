from collections import defaultdict
import collections.abc
import inspect
from inspect import Parameter
import sys
from typing import Any, Dict, Sequence, Set, Union, get_type_hints
try:
    from typing import get_args, get_origin             # type: ignore
except ImportError:                                     # pragma: no cover
    from typing_extensions import get_args, get_origin  # pragma: no cover
import warnings

import click

from .errors import UnsupportedDocstringStyle
from .parser import parse_docstring


POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
KEYWORD_ONLY = Parameter.KEYWORD_ONLY
EMPTY = Parameter.empty


def add_options_from(func,
                     *,
                     names: Dict[str, Sequence[str]] = None,
                     include: Set[str] = None,
                     exclude: Set[str] = None,
                     custom: Dict[str, Dict[str, Any]] = None):
    """Inspect `func` and add corresponding options to the decorated function.

    Args:
        func (callable): The function which provides the options through inspection.
        names (dict): Map parameter names in `func` to `click.option` names.
        include (set): Parameter names to be used from `func`.
        exclude (set): Parameter names to be excluded from `func`.
        custom (dict): Map parameter names to custom kwargs for the corresponding option.

    Returns:
        callable: A decorator which will add the requested options to the decorated function.

    Raises:
        TypeError: If `typing.get_type_hints` raises TypeError on Python >= 3.9.

    Warns:
        UserWarning: If a parameter of `func` has no default and no type information can be
                     retrieved from either `custom`, annotations of the docstring.
                     If `func` type hints contain standard collections as type hinting generics
                     for Python < 3.9 (e.g. `list[int]`).
    """
    include = include or set()
    names = names or {}
    custom = custom or {}
    try:
        p_doc = parse_docstring(func.__doc__ or '')
    except UnsupportedDocstringStyle:
        p_doc = defaultdict(dict)
    try:
        type_hints = get_type_hints(func)
    except TypeError:  # `from __future__ import annotations` with e.g. `list[int]` on Python < 3.9.
        if sys.version_info < (3, 9):
            warnings.warn('This decorator attempts to retrieve type hints via `typing.get_type_hints`. '
                          'This however is not compatible with `from __future__ import annotations` '
                          'and standard collections as type hinting generics (e.g. `list[int]`). '
                          'Please use the typing collections instead (e.g. `typing.List[int]`). '
                          'This decorator continues to work however no type information from '
                          'annotations will be used. This might lead to unexpected results.')
        else:
            raise  # pragma: no cover
        type_hints = {}
    all_parameters = inspect.signature(func).parameters
    to_be_used = (include or all_parameters.keys()) - (exclude or set())
    parameters = [(name, parameter) for name, parameter in all_parameters.items()
                  if name in to_be_used]

    def _decorator(f):
        for name, parameter in reversed(parameters):
            has_default = parameter.default is not EMPTY
            condition = (  # Whether to use this parameter or not.
                name in include
                or parameter.kind is KEYWORD_ONLY
                or parameter.kind is POSITIONAL_OR_KEYWORD and has_default
            )
            if not condition:
                continue

            kwargs = {}
            if 'help' in p_doc[name]:
                kwargs['help'] = p_doc[name]['help']

            if has_default:
                kwargs['default'] = parameter.default
            else:
                kwargs['required'] = True

            try:
                kwargs['type'] = custom[name]['type']
            except KeyError:
                try:
                    tp_hint = type_hints[name]
                except KeyError:
                    try:
                        tp_hint = p_doc[name]['type']
                    except KeyError:
                        tp_hint = None
                        if parameter.default is EMPTY:
                            warnings.warn(f'No type hint for parameter {name!r}')
                if tp_hint is not None:
                    kwargs.update(_parse_type_hint_into_kwargs(tp_hint))

            kwargs.update(custom.get(name, {}))

            try:
                opt_names = names[name]
            except KeyError:
                opt_name = name.replace("_", "-")
                if kwargs.get('is_flag', False):
                    opt_names = [f'--{opt_name}/--no-{opt_name}']
                else:
                    opt_names = [f'--{opt_name}']

            click.option(*opt_names, **kwargs)(f)
        return f

    return _decorator


def _parse_type_hint_into_kwargs(tp_hint):
    args, origin = get_args(tp_hint), get_origin(tp_hint)
    if tp_hint is bool:
        return dict(is_flag=True, type=bool)
    elif origin in (list, collections.abc.Sequence):
        return dict(multiple=True, type=_parse_type_hint_into_kwargs(args[0])['type'])
    elif origin is tuple:
        return dict(type=tuple(_parse_type_hint_into_kwargs(x)['type'] for x in args))
    elif origin is Union:
        return _parse_type_hint_into_kwargs(args[0])
    return dict(type=(origin or tp_hint))
