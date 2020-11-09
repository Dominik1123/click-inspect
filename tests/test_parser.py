from typing import Union

import pytest

from click_inspect.errors import UnsupportedDocstringStyle
from click_inspect.parser import parse_docstring


@pytest.fixture
def rest_style_func():
    def _f():
        """Short description.

        This is
        the
        long description.

        :param foo: This is foo.
        :type foo: int
        :param bar: This is bar.
        :param baz: This is baz.
        :type baz: float or str
        :param a_b_c: This is a_b_c.
        :type a_b_c: CustomType
        :returns: The return value.
        :rtype: ReturnType
        """
    return _f


@pytest.fixture
def google_style_func():
    def _f():
        """Short description.

        This is
        the
        long description.

        Args:
            foo (int): This is foo.
            bar: This is bar.
            baz (float or str): This is baz.
            a_b_c (CustomType): This is a_b_c.

        Returns:
            ReturnType: The return value.
        """
    return _f


@pytest.fixture
def numpy_style_func():
    def _f():
        """Short description.

        This is
        the
        long description.

        Parameters
        ----------
        foo : int
            This is foo.
        bar
            This is bar.
        baz : float or str
            This is baz.
        a_b_c : CustomType
            This is a_b_c.

        Returns
        -------
        ReturnType
            The return value.
        """
    return _f


@pytest.fixture(params=['rest_style_func', 'google_style_func', 'numpy_style_func'])
def docfunc(request):
    return request.getfixturevalue(request.param)


@pytest.fixture()
def rest_style_docstring(rest_style_func):
    return rest_style_func.__doc__


@pytest.fixture()
def google_style_docstring(google_style_func):
    return google_style_func.__doc__


@pytest.fixture()
def numpy_style_docstring(numpy_style_func):
    return numpy_style_func.__doc__


@pytest.fixture(params=['rest_style_docstring', 'google_style_docstring', 'numpy_style_docstring'])
def docstring(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(params=[
    'rest_style_func', 'google_style_func', 'numpy_style_func',
    'rest_style_docstring', 'google_style_docstring', 'numpy_style_docstring'
])
def doc_func_or_string(request):
    return request.getfixturevalue(request.param)


def test_parse_docstring(doc_func_or_string):
    with pytest.warns(UserWarning) as warninfo:
        assert parse_docstring(doc_func_or_string) == {
            'foo': {'help': 'This is foo.', 'type': int},
            'bar': {'help': 'This is bar.'},
            'baz': {'help': 'This is baz.', 'type': Union[float, str]},
            'a_b_c': {'help': 'This is a_b_c.'},
        }
    assert len(warninfo) == 1
    assert str(warninfo[0].message.args[0]).startswith("Type hint 'CustomType' cannot be resolved.")


def test_parse_docstring_raises():
    with pytest.raises(UnsupportedDocstringStyle) as excinfo:
        parse_docstring('This docstring contains no parameters')
    assert excinfo.value.args[0] == 'This docstring contains no parameters'


def test_parse_docstring_base_function(base_function):
    assert parse_docstring(base_function.__doc__) == {
        'a': {'help': 'This parameter should be skipped.', 'type': str},
        'b': {'help': 'This one should be added.', 'type': int},
        'c': {'help': 'This one should be added too.', 'type': int},
        'd': {'help': 'And so should this one.', 'type': str},
    }


def test_parse_docstring_pass_on_unsupported_type_string():
    def _f():
        """
        Args:
            x (int and str): Type string is not supported.
        """
    assert parse_docstring(_f) == {'x': {'help': 'Type string is not supported.'}}
