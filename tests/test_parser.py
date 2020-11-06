import pytest

from click_inspect.errors import UnsupportedDocstringStyle
from click_inspect.parser import parse_docstring


@pytest.fixture
def rest_style_docstring():
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
    return _f.__doc__


@pytest.fixture
def google_style_docstring():
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
    return _f.__doc__


@pytest.fixture
def numpy_style_docstring():
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
    return _f.__doc__


@pytest.fixture(params=['rest_style_docstring', 'google_style_docstring', 'numpy_style_docstring'])
def docstring(request):
    return request.getfixturevalue(request.param)


def test_parse_docstring(docstring):
    assert parse_docstring(docstring) == {
        'foo': {'help': 'This is foo.', 'type': ['int']},
        'bar': {'help': 'This is bar.'},
        'baz': {'help': 'This is baz.', 'type': ['float', 'str']},
        'a_b_c': {'help': 'This is a_b_c.', 'type': ['CustomType']},
    }


def test_parse_docstring_raises():
    with pytest.raises(UnsupportedDocstringStyle) as excinfo:
        parse_docstring('This docstring contains no parameters')
    assert excinfo.value.args[0] == 'This docstring contains no parameters'


def test_parse_base_function(base_function):
    assert parse_docstring(base_function.__doc__) == {
        'a': {'help': 'This parameter should be skipped.', 'type': ['str']},
        'b': {'help': 'This one should be added.', 'type': ['int']},
        'c': {'help': 'This one should be added too.', 'type': ['int']},
        'd': {'help': 'And so should this one.', 'type': ['str']},
    }
