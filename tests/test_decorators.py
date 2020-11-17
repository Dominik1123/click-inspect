from __future__ import annotations

import sys
from typing import List, Sequence, Tuple, Union

import click
import pytest

from click_inspect.decorators import add_options_from, _parse_type_hint_into_kwargs


def test_add_options_from(base_function):
    @click.command()
    @add_options_from(base_function)
    def test(): pass

    assert len(test.params) == 4

    assert test.params[0].name == 'b'
    assert test.params[0].opts == ['--b']
    assert test.params[0].secondary_opts == []
    assert test.params[0].type is click.INT
    assert test.params[0].default == 1
    assert test.params[0].required is False
    assert test.params[0].help == 'This one should be added.'

    assert test.params[1].name == 'c'
    assert test.params[1].opts == ['--c']
    assert test.params[1].secondary_opts == []
    assert test.params[1].type is click.INT
    assert test.params[1].required is True
    assert test.params[1].help == 'This one should be added too.'

    assert test.params[2].name == 'd'
    assert test.params[2].opts == ['--d']
    assert test.params[2].secondary_opts == []
    assert test.params[2].type is click.STRING
    assert test.params[2].default == 'test'
    assert test.params[2].required is False
    assert test.params[2].help == 'And so should this one.'

    assert test.params[3].name == 'e'
    assert test.params[3].opts == ['--e']
    assert test.params[3].secondary_opts == ['--no-e']
    assert test.params[3].type is click.BOOL
    assert test.params[3].is_flag is True
    assert test.params[3].default is True
    assert test.params[3].required is False
    assert test.params[3].help == 'Boolean flag.'


def test_add_options_from_infer_types_from_docstring(base_function):
    base_function.__annotations__ = {}
    test_add_options_from(base_function)


def test_add_options_from_include(base_function):
    @click.command()
    @add_options_from(base_function, include={'a', 'b'})
    def test(): pass

    assert len(test.params) == 2

    assert test.params[0].name == 'a'
    assert test.params[0].opts == ['--a']
    assert test.params[0].secondary_opts == []
    assert test.params[0].type is click.STRING
    assert test.params[0].required is True
    assert test.params[0].help == 'This parameter should be skipped.'

    assert test.params[1].name == 'b'
    assert test.params[1].opts == ['--b']
    assert test.params[1].secondary_opts == []
    assert test.params[1].type is click.INT
    assert test.params[1].default == 1
    assert test.params[1].required is False
    assert test.params[1].help == 'This one should be added.'


def test_add_options_from_include_via_names_and_custom():
    def func(a: int, b: int, c: int): pass

    @click.command()
    @add_options_from(func, names={'a': ['-a']}, custom={'c': {'default': 1}})
    def test(): pass

    assert len(test.params) == 2
    assert test.params[0].name == 'a'
    assert test.params[1].name == 'c'


def test_add_options_from_exclude(base_function):
    @click.command()
    @add_options_from(base_function, exclude={'b', 'c'})
    def test(): pass

    assert len(test.params) == 2

    assert test.params[0].name == 'd'
    assert test.params[0].opts == ['--d']
    assert test.params[0].secondary_opts == []
    assert test.params[0].type is click.STRING
    assert test.params[0].default == 'test'
    assert test.params[0].required is False
    assert test.params[0].help == 'And so should this one.'

    assert test.params[1].name == 'e'
    assert test.params[1].opts == ['--e']
    assert test.params[1].secondary_opts == ['--no-e']
    assert test.params[1].type is click.BOOL
    assert test.params[1].is_flag is True
    assert test.params[1].default is True
    assert test.params[1].required is False
    assert test.params[1].help == 'Boolean flag.'


def test_add_options_from_names(base_function):
    @click.command()
    @add_options_from(base_function, names={'b': ['-b'], 'd': ['-test', '--d']})
    def test(): pass

    assert len(test.params) == 4

    assert test.params[0].name == 'b'
    assert test.params[0].opts == ['-b']
    assert test.params[0].secondary_opts == []

    assert test.params[1].name == 'c'
    assert test.params[1].opts == ['--c']
    assert test.params[1].secondary_opts == []

    assert test.params[2].name == 'd'
    assert test.params[2].opts == ['-test', '--d']
    assert test.params[2].secondary_opts == []

    assert test.params[3].name == 'e'
    assert test.params[3].opts == ['--e']
    assert test.params[3].secondary_opts == ['--no-e']


def test_add_options_from_custom(base_function):
    @click.command()
    @add_options_from(base_function, custom={'d': dict(default='custom_default')})
    def test(): pass

    assert len(test.params) == 4
    assert test.params[2].default == 'custom_default'


def test_add_options_from_single_switch_boolean_flag(base_function):
    @click.command()
    @add_options_from(base_function, names={'e': ['--e']})
    def test(): pass

    assert len(test.params) == 4
    assert test.params[3].name == 'e'
    assert test.params[3].opts == ['--e']
    assert test.params[3].secondary_opts == []
    assert test.params[3].type is click.BOOL
    assert test.params[3].is_flag is True
    assert test.params[3].default is True
    assert test.params[3].required is False
    assert test.params[3].help == 'Boolean flag.'


def test_add_options_from_warn_if_no_type():
    def func(*, a):
        """Test func.

        Args:
            a: Test parameter
        """

    with pytest.warns(UserWarning) as warninfo:
        @add_options_from(func)
        def test(): pass

    assert len(warninfo) == 1
    assert str(warninfo[0].message.args[0]) == "No type hint for parameter 'a'"


def test_add_options_from_no_warn_if_no_type_but_default():
    def func(*, a = 1):
        """Test func.

        Args:
            a: Test parameter
        """

    @click.command()
    @add_options_from(func)
    def test(): pass

    assert len(test.params) == 1
    assert test.params[0].type is click.INT
    assert test.params[0].default == 1


def test_add_options_from_unsupported_docstring_style():
    def func(*, a: int):
        """Test func.

        Params:
            a: This is the only parameter.
        """

    @click.command()
    @add_options_from(func)
    def test(): pass

    assert len(test.params) == 1
    assert test.params[0].help is None


def test_add_options_from_readme_example_func(readme_example_function):
    @click.command()
    @add_options_from(readme_example_function)
    def test(): pass

    assert len(test.params) == 3

    assert test.params[0].name == 'size'
    assert test.params[0].opts == ['--size']
    assert test.params[0].type is click.INT
    assert test.params[0].required is True
    assert test.params[0].help == 'Size of the grid in both dimensions.'

    assert test.params[1].name == 'symbol'
    assert test.params[1].opts == ['--symbol']
    assert test.params[1].type is click.STRING
    assert test.params[1].default == 'x'
    assert test.params[1].required is False
    assert test.params[1].help == 'Symbol for displaying data points.'

    assert test.params[2].name == 'empty'
    assert test.params[2].opts == ['--empty']
    assert test.params[2].type is click.STRING
    assert test.params[2].default == ' '
    assert test.params[2].required is False
    assert test.params[2].help == 'Symbol for displaying empty space.'


def test_add_options_from_list_type_hint(list_type_hint_function):
    @click.command()
    @add_options_from(list_type_hint_function)
    def test(): pass

    assert len(test.params) == 1

    assert test.params[0].name == 'x'
    assert test.params[0].opts == ['--x']
    assert test.params[0].type is click.INT
    assert test.params[0].required is True
    assert test.params[0].multiple is True
    assert test.params[0].help == '...'


def test_add_options_from_list_type_hint_via_docstring(list_type_hint_function):
    list_type_hint_function.__annotations__ = {}
    test_add_options_from_list_type_hint(list_type_hint_function)


def test_add_options_from_tuple_type_hint(tuple_type_hint_function):
    @click.command()
    @add_options_from(tuple_type_hint_function)
    def test(): pass

    assert len(test.params) == 1

    assert test.params[0].name == 'x'
    assert test.params[0].opts == ['--x']
    assert type(test.params[0].type) is click.Tuple
    assert test.params[0].type.types == [click.INT, click.STRING]
    assert test.params[0].nargs == 2
    assert test.params[0].required is True
    assert test.params[0].help == '...'


def test_add_options_from_tuple_type_hint_via_docstring(tuple_type_hint_function):
    tuple_type_hint_function.__annotations__ = {}
    test_add_options_from_tuple_type_hint(tuple_type_hint_function)



def test_add_options_from_union_type_hint(union_type_hint_function):
    @click.command()
    @add_options_from(union_type_hint_function)
    def test(): pass

    assert len(test.params) == 1

    assert test.params[0].name == 'x'
    assert test.params[0].opts == ['--x']
    assert test.params[0].type is click.INT
    assert test.params[0].required is True
    assert test.params[0].help == '...'


def test_add_options_from_union_type_hint_via_docstring(union_type_hint_function):
    union_type_hint_function.__annotations__ = {}
    test_add_options_from_union_type_hint(union_type_hint_function)


def test_add_options_from_nested_union_and_sequence():
    def func(*, x: Union[List[int], str]): pass

    @click.command()
    @add_options_from(func)
    def test(): pass

    assert len(test.params) == 1
    assert test.params[0].type is click.INT


def test_add_options_from_no_type_warning_for_excluded_parameters():
    def func(*, x: int):  # Use some valid type hint here to prevent further warnings.
        """
        Args:
            x (UnknownType): If 'x' gets excluded, no warning should be issued.
        """

    with pytest.warns(UserWarning) as warninfo:
        @add_options_from(func)
        def test(): pass

    assert len(warninfo) == 1

    @click.command()
    @add_options_from(func, exclude={'x'})
    def test(): pass

    assert len(test.params) == 0


@pytest.mark.skipif(sys.version_info >= (3, 9),
    reason='Starting with Python 3.9 get_type_hints works without raising TypeError.')
def test_add_options_from_warn_on_standard_collections_as_typing_generics():
    def func(*, a: list[str]): pass

    with pytest.warns(UserWarning) as warninfo:
        @add_options_from(func)
        def test(): pass

    assert len(warninfo) == 2  # Warns another time because no type hint is available.


def test_parse_type_hint_into_kwargs_bool():
    assert _parse_type_hint_into_kwargs(bool) == dict(is_flag=True, type=bool)


@pytest.mark.parametrize('tp', [Sequence, List])
def test_parse_type_hint_into_kwargs_list(tp):
    assert _parse_type_hint_into_kwargs(tp[int]) == dict(multiple=True, type=int)
    assert _parse_type_hint_into_kwargs(tp[str]) == dict(multiple=True, type=str)
    assert _parse_type_hint_into_kwargs(tp[bool]) == dict(multiple=True, type=bool)


def test_parse_type_hint_into_kwargs_tuple():
    assert _parse_type_hint_into_kwargs(Tuple[int, str]) == dict(type=(int, str))
    assert _parse_type_hint_into_kwargs(Tuple[int, int, int]) == dict(type=(int, int, int))


def test_parse_type_hint_into_kwargs_union():
    assert _parse_type_hint_into_kwargs(Union[int, str]) == dict(type=int)
    assert _parse_type_hint_into_kwargs(Union[str, int]) == dict(type=str)


def test_parse_type_hint_into_kwargs_list_with_union():
    assert _parse_type_hint_into_kwargs(List[Union[int, str]]) == dict(multiple=True, type=int)
    assert _parse_type_hint_into_kwargs(List[Union[str, float]]) == dict(multiple=True, type=str)


def test_parse_type_hint_into_kwargs_union_with_list():
    assert _parse_type_hint_into_kwargs(Union[List[int], List[str]]) == dict(multiple=True, type=int)
    assert _parse_type_hint_into_kwargs(Union[List[str], List[int]]) == dict(multiple=True, type=str)
