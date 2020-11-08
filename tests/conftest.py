from typing import List, Tuple

import pytest


@pytest.fixture(scope='function')
def base_function():
    def _f(a, b: int = 1, *, c: int, d: str = 'test'):
        """Short description.

        Long
        description.

        Args:
            a (str): This parameter should be skipped.
            b (int): This one should be added.
            c (int): This one should be added too.
            d (str): And so should this one.

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
