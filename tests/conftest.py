from typing import List, Tuple, Union

import pytest


@pytest.fixture(scope='function')
def base_function():
    def _f(a, b: int = 1, *, c: int, d: str = 'test', e: bool = True):
        """Short description.

        Long
        description.

        Args:
            a (str): This parameter should be skipped.
            b (int): This one should be added.
            c (int): This one should be added too.
            d (str): And so should this one.
            e (bool): Boolean flag.

        Returns:
            str: This is just a test.
        """
    return _f


@pytest.fixture()
def readme_example_function():
    def display_data(data: List[Tuple[int, int]],
                     *, size: int, symbol: str = 'x', empty: str = ' ') -> str:
        """Display the given data points in a 2D ASCII grid.

        Args:
            data (list of (int, int)): The data points as x- and y-tuples.
            size (int): Size of the grid in both dimensions.
            symbol (str): Symbol for displaying data points.
            empty (str): Symbol for displaying empty space.

        Returns:
            str: The string containing the grid.
        """
    return display_data


@pytest.fixture(scope='function')
def list_type_hint_function():
    def _f(*, x: List[int]):
        """Short description.

        Long
        description.

        Args:
            x (list of int): ...
        """
    return _f


@pytest.fixture(scope='function')
def tuple_type_hint_function():
    def _f(*, x: Tuple[int, str]):
        """Short description.

        Long
        description.

        Args:
            x ((int, str)): ...
        """
    return _f


@pytest.fixture(scope='function')
def union_type_hint_function():
    def _f(*, x: Union[int, str]):
        """Short description.

        Long
        description.

        Args:
            x (int or str): ...
        """
    return _f
