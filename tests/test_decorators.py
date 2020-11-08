import click
import pytest

from click_inspect import add_options_from
from click_inspect.errors import UnsupportedTypeHint


def test_add_options_from(base_function):
    @click.command()
    @add_options_from(base_function)
    def test(): pass

    assert len(test.params) == 3

    assert test.params[0].name == 'b'
    assert test.params[0].opts == ['--b']
    assert test.params[0].type is click.INT
    assert test.params[0].default == 1
    assert test.params[0].required is False
    assert test.params[0].help == 'This one should be added.'

    assert test.params[1].name == 'c'
    assert test.params[1].opts == ['--c']
    assert test.params[1].type is click.INT
    assert test.params[1].required is True
    assert test.params[1].help == 'This one should be added too.'

    assert test.params[2].name == 'd'
    assert test.params[2].opts == ['--d']
    assert test.params[2].type is click.STRING
    assert test.params[2].default == 'test'
    assert test.params[2].required is False
    assert test.params[2].help == 'And so should this one.'


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
    assert test.params[0].type is click.STRING
    assert test.params[0].required is True
    assert test.params[0].help == 'This parameter should be skipped.'

    assert test.params[1].name == 'b'
    assert test.params[1].opts == ['--b']
    assert test.params[1].type is click.INT
    assert test.params[1].default == 1
    assert test.params[1].required is False
    assert test.params[1].help == 'This one should be added.'


def test_add_options_from_exclude(base_function):
    @click.command()
    @add_options_from(base_function, exclude={'b', 'c'})
    def test(): pass

    assert len(test.params) == 1

    assert test.params[0].name == 'd'
    assert test.params[0].opts == ['--d']
    assert test.params[0].type is click.STRING
    assert test.params[0].default == 'test'
    assert test.params[0].required is False
    assert test.params[0].help == 'And so should this one.'


def test_add_options_from_names(base_function):
    @click.command()
    @add_options_from(base_function, names={'b': ['-b'], 'd': ['-test', '--d']})
    def test(): pass

    assert len(test.params) == 3

    assert test.params[0].name == 'b'
    assert test.params[0].opts == ['-b']

    assert test.params[1].name == 'c'
    assert test.params[1].opts == ['--c']

    assert test.params[2].name == 'd'
    assert test.params[2].opts == ['-test', '--d']


def test_add_options_from_custom(base_function):
    @click.command()
    @add_options_from(base_function, custom={'d': dict(default='custom_default')})
    def test(): pass

    assert len(test.params) == 3
    assert test.params[2].default == 'custom_default'


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


def test_add_options_from_raise_if_invalid_type():
    def func(*, a):
        """Test func.

        Args:
            a (SomeType): Test parameter
        """
    
    with pytest.raises(UnsupportedTypeHint) as excinfo:
        @add_options_from(func)
        def test(): pass
    assert str(excinfo.value) == 'SomeType (only builtin types are supported)'


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
