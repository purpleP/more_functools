from functools import partial, wraps
import pytest
from more_functools import dict_structure, dict_to_set, set_to_dict, dmap
from more_functools import or_default
from more_functools import replace
from more_functools import compose
from more_functools import unpack
from more_functools import concat
from more_functools import merge
from more_functools import ManyToMany
from more_functools import decorator_with_arguments


def call(*args, **kwargs):
    return args, kwargs


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


def test_merge():
    defaults = {'a': {'b': 'b'}, 'c': 'c'}
    new = {'a': {'c': 'c'}}
    assert {'a': {'b': 'b', 'c': 'c'}, 'c': 'c'} == merge(defaults, new)


@pytest.fixture
def manytomany():
    return ManyToMany('foo', 'foos', 'bar', 'bars')


def test_manytomany_add(manytomany):
    assert len(manytomany) == 0
    manytomany.add(foo=1, bar=10)
    assert manytomany.foos[1] == {10}
    assert (1, 10) in manytomany
    assert len(manytomany) == 1


def test_manytomany_remove(manytomany):
    manytomany.add(1, 2)
    manytomany.remove(1, 2)
    assert not (1, 2) in manytomany
    assert len(manytomany) == 0


def test_manytomany_iter(manytomany):
    pairs = {(1, 'a'), (1, 'b'), (2, 'c')}
    manytomany.add(pairs=pairs)
    assert pairs == set(manytomany)


def test_manytomany_init():
    m = ManyToMany('foo', 'foos', 'bar', 'bars', 1, 'a')
    assert (1, 'a') in m
    m = ManyToMany('foo', 'foos', 'bar', 'bars', pairs=((1, 'a'),))
    assert (1, 'a') in m
    m = ManyToMany('foo', 'foos', 'bar', 'bars', foo=1, bar='a')
    assert (1, 'a') in m


@decorator_with_arguments
def add_args(a, b, func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(a, b, *args, **kwargs)
    return wrapper



@add_args('a', 'b')
def foo(*args):
    return args


def test_decorator_with_arguments():
    assert 4 == len(foo('c', 'd'))
