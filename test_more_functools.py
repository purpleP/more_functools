import pytest
from lib.utils.common import dict_structure, dict_to_set, set_to_dict, dmap


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


@pytest.mark.parametrize('input_dict,path,expected_output', (
    (
        {
            '0.0': {
                '1.0': {
                    '2.0': 1
                }
            }
        },
        (None, None),
        {
            '0.0': {
                '1.0': {
                    '2.0': 2
                }
            }
        },
    ),
    (
        {
            '0.0': {
                '1.0': {
                    'k1': {
                        '2.0': 1
                    },
                    'k2': {
                        '2.1': 1
                    }
                }
            }
        },
        (None, None, 'k1',),
        {
            '0.0': {
                '1.0': {
                    'k1': {
                        '2.0': 2
                    },
                    'k2': {
                        '2.1': 1
                    }

                }
            }
        },
    ),
))
def test_dmap(input_dict, path, expected_output):
    assert expected_output == dmap(lambda x: x + 1, input_dict, *path)
