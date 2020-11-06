import click

from click_inspect import add_options_from


def test_add_options_from(base_function):
    @click.command()
    @add_options_from(base_function)
    def test():
        pass

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
