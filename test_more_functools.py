from functools import partial
import pytest
from more_functools import dict_structure, dict_to_set, set_to_dict, dmap
from more_functools import or_default
from more_functools import replace
from more_functools import compose
from more_functools import unpack
from more_functools import concat
from more_functools import merge


@pytest.fixture()
def expected_dict():
    return {
        '0.0': {1},
        '0.1': {
            '1.0': {1}
        }
    }


@pytest.fixture()
def expected_set():
    return {
        ('0.0', frozenset((1,))),
        (
            '0.1',
            frozenset(
                (('1.0', frozenset((1,))),)
            )
        )
    }


@pytest.fixture()
def expected_structure():
    return {
        '0.0': (set, None),
        '0.1': (
            dict, {
                '1.0': (set, None)
            }
        )
    }


def test_dict_to_set(expected_dict, expected_set):
    assert expected_set == dict_to_set(expected_dict)


def test_dict_structure(expected_dict, expected_structure):
    assert expected_structure == dict_structure(expected_dict)


def test_set_to_dict(expected_set, expected_structure, expected_dict):
    assert expected_dict == set_to_dict(expected_set, expected_structure)


@pytest.mark.parametrize('func,input_dict,path,expected_output', (
    (
        str,
        {
            '0.0': {
                '1.0': {
                    '2.0': 1
                }
            }
        },
        (None, None, None),
        {
            '0.0': {
                '1.0': {
                    '2.0': '1'
                }
            }
        },
    ),
    (
        str,
        {
            '0.0': {
                '1.0': {
                    'k1': {
                        '2.0': 1,
                        '2.1': 1,
                    },
                    'k2': {
                        '2.1': 1
                    }
                }
            }
        },
        (None, None, 'k1', '2.0'),
        {
            '0.0': {
                '1.0': {
                    'k1': {
                        '2.0': '1',
                        '2.1': 1,
                    },
                    'k2': {
                        '2.1': 1
                    }

                }
            }
        },
    ),
    (
        lambda tup: tuple(map(str, tup)),
        {'key': (1,)},
        ('key',),
        {'key': ('1',)}
    ),
))
def test_dmap(func, input_dict, path, expected_output):
    assert expected_output == dmap(func, input_dict, *path)


def test_or_default():
    def falling(*args, **kwargs):
        raise ValueError()
    f = or_default(falling, {ValueError: 0})
    assert f() == 0


def test_replace():
    assert replace(dict(a='a', b='b'), 'b', 'c') == dict(a='a', b='c')


def test_compose():
    assert compose(str, lambda x: x + 1)(0) == '1'


def test_unpack():
    def f(a, b):
        return a, b
    assert unpack(f)(('x', 'y')) == ('x', 'y')


def test_concat():
    a = (b'a', b'b', b'c')
    assert b'abc' == concat(bytearray, a)


def test_merge():
    defaults = {'a': {'b': 'b'}, 'c': 'c'}
    new = {'a': {'c': 'c'}}
    assert {'a': {'b': 'b', 'c': 'c'}, 'c': 'c'} == merge(defaults, new)
