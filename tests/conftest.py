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
