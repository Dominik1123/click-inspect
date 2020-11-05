[![Tests](https://github.com/Dominik1123/click-inspect/workflows/Tests/badge.svg)](https://github.com/Dominik1123/click-inspect/actions?workflow=Tests)
[![Codecov](https://codecov.io/gh/Dominik1123/click-inspect/branch/main/graph/badge.svg)](https://codecov.io/gh/Dominik1123/click-inspect)
[![PyPI](https://img.shields.io/pypi/v/click-inspect.svg)](https://pypi.org/project/click-inspect/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/click-inspect.svg?style=flat-square)](https://pypi.org/pypi/click-inspect/)

# click-inspect

*Add options to click commands based on inspecting functions*

## Installation

[`pip install click-inspect`](https://pypi.org/project/click-inspect/)

## Usage

Suppose we have an application containing an API function for which we would like to expose a command line interface. That function expects one or two arguments with internal data types and a bunch of configuration options. For example:

```python
def display_data(data: List[Tuple[int, int]], *, size: int, symbol: str = 'x', empty: str = ' ') -> str:
    """Display the given data points in a 2D ASCII grid.

    Args:
        data (list of (int, int)): The data points as x- and y-tuples.
        size (int): Size of the grid in both dimensions.
        symbol (str): Symbol for displaying data points.
        empty (str): Symbol for displaying empty space.

    Returns:
        str: The string containing the grid.
    """
    grid = [[empty]*size for _ in range(size)]
    for x, y in data:
        grid[y][x] = symbol
    top = bottom = ('+', *'-'*size, '+')
    grid = (top, *(('|', *row, '|') for row in grid), bottom)
    return '\n'.join(map(''.join, grid))
```

Here the type of the first argument, ``data``, is an internal aspect of the application, but the remaining arguments are generic options.

Now we want to create a [click](https://pypi.org/project/click/) interface for using this function from the command line. Specifically we want it to work on JSON files of the following format:

```json
{"data": [[1, 1], [2, 4], [3, 3]]}
```

So the only thing our command needs to do is to read the JSON file and convert the content in a way that it is compatible with what `display_data` expects:

```python
import json
import click


@click.command()
@click.argument('file')
def display(file):
    with open(file) as fh:
        data = json.load(fh)['data']
    data = [[int(x) for x in row] for row in data]
    print(display_data(data))


if __name__ == '__main__':
    display()
```

Then we can run the program in the following way:

```text
$ python example.py test.json 
+-----+
|     |
| x   |
|     |
|   x |
|  x  |
+-----+
```

Now this only uses the default configuration of the `display_data` function and we also want to expose these optional arguments to the command line interface. We can do so by adding a few options:

```python
@click.command()
@click.argument('file')
@click.option('--size', default=5, help='Size of the grid in both dimensions.')
@click.option('--symbol', default='x', help='Symbol for displaying data points.')
@click.option('--empty', default=' ', help='Symbol for displaying empty space.')
def display(file, size, symbol, empty):
    with open(file) as fh:
        data = json.load(fh)['data']
    data = [[int(x) for x in row] for row in data]
    print(display_data(data, size=size, symbol=symbol, empty=empty))
```

But that's a lot of code duplication. We duplicated the parameter names, the default values and the help text from the docstring.
Also if we decide to add a new parameter to `display_data` we need to update the command as well.

This is where `click-inspect` comes in handy. Using the `add_options_from` decorator we can simply add all optional arguments from `display_data` to the `display` command without code duplication:

```python
@click.command()
@click.argument('file')
@add_options_from(display_data)
def display(file, **kwargs):
    with open(file) as fh:
        data = json.load(fh)['data']
    data = [[int(x) for x in row] for row in data]
    print(display_data(data, **kwargs))
```

### Docstring styles

`click-inspect` supports inspecting [reST-style](https://www.python.org/dev/peps/pep-0287/) docstrings, as well as [Google-](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) and [Numpy-style](https://numpydoc.readthedocs.io/en/latest/format.html) docstrings via [`napoleon`](https://pypi.org/project/sphinxcontrib-napoleon/).
