# -*- coding: utf-8 -*-
from functools import reduce
from itertools import tee
from itertools import islice
from itertools import chain
try:
    from itertools import izip_longest
except ImportError:
    from itertools import zip_longest
from collections import namedtuple, Mapping
from six import iteritems as items


class EqualByValue(object):

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def namedtuple_with_defaults(typename, fields, defaults=()):
    T = namedtuple(typename, fields)
    T.__new__.__defaults__ = defaults
    return T


def fst(sequence):
    return sequence[0]


def snd(sequence):
    return sequence[1]


def find(predicate, iterable, default=None):
    return next((e for e in iterable if predicate(e)), default)


def nwise_iter(iterable, n, fillvalue=None):
    iterators = tuple(
        islice(itertor, i, None)
        for i, itertor in enumerate(tee(iterable, n))
    )
    return izip_longest(*iterators, fillvalue=fillvalue)


def dict_to_set(dct):
    def transform(obj):
        transformers = (
            (Mapping, dict_to_set),
            (list, tuple),
            (set, frozenset),
        )
        transformer = next(
            (f for cls, f in transformers if isinstance(obj, cls)), lambda x: x
        )
        return transformer(obj)

    return frozenset((k, transform(v)) for k, v in dct.items())


def dict_structure(dct):
    return {
        k: (type(v), dict_structure(v) if isinstance(v, Mapping) else None)
        for k, v in dct.items()
    }


def set_to_dict(s, structure):
    return {
        k: set_to_dict(v, struct) if initial_type == dict else initial_type(v)
        for k, v, initial_type, struct in (
            (k, v, structure[k][0], structure[k][1])
            for k, v in s
        )
    }


def replace(dct, key, new_value):
    return dict(chain(items(dct), ((key, new_value),)))


def dmap(f, d, *path):
    key, path_tail = path[0], path[1:]
    if path_tail:
        if key is None:
            func = lambda k, v: dmap(f, v, *path_tail)
        else:
            func = lambda k, v: dmap(f, v, *path_tail) if k == key else v
    else:
        func = lambda k, v: f(v) if k == key or key is None else v
    return {k: func(k, v) for k, v in items(d)}


def disjoint_symmetric_diff(s1, s2):
    return s1 - s2, s2 - s1


def or_default(f, defaults, logger=None):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if logger:
                logger.error(e)
            try:
                return defaults[type(e)]
            except KeyError:
                raise e
    return wrapper
