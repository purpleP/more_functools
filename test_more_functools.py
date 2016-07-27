from functools import partial
import pytest
from more_functools import dict_structure, dict_to_set, set_to_dict, dmap
from more_functools import or_default
from more_functools import replace


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
        '0.0': (set,),
        '0.1': (
            dict, {
                '1.0': (set,)
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
