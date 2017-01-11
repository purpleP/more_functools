# -*- coding: utf-8 -*-
from functools import reduce
from functools import wraps
from itertools import tee
from itertools import islice
from itertools import chain
from collections import namedtuple, Mapping
from six import iteritems as items
from six import iterkeys as keys
from six.moves import zip_longest


class EqualByValue(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def unpack(f):
    """
    takes function that takes one or more positional arguments
    and return function that takes one iterable argument
    """
    @wraps(f)
    def wrapper(args):
        return f(*args)
    return wrapper

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
    return zip_longest(*iterators, fillvalue=fillvalue)


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


def setifnotin(dct, key, callable):
    return dct.get(key) or dct.setdefault(key, callable())


def disjoint_symmetric_diff(s1, s2):
    return s1 - s2, s2 - s1


def or_default(f, defaults, logger=None):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except tuple(keys(defaults)) as e:
            if logger:
                logger.error(e)
            return next(
                d for ex_type, d in items(defaults)
                if isinstance(e, ex_type)
            )
    return wrapper


def concat(desired_type, seq):
    return reduce(lambda acc, elem: acc + elem, seq, desired_type())


def none_to_tuple(value):
    return () if value is None else (value,)


def merge(a, b, *path):
    key_value_triples = ((k, a.get(k), b.get(k)) for k in a.keys() | b.keys())
    def _merge(key, x, y):
        if isinstance(x, Mapping) and isinstance(y, Mapping):
            return merge(x, y, *((path + (key,))))
        else:
            return y
    return {
        k: _merge(k, av, bv) if av and bv else av if av else bv
        for k, av, bv in key_value_triples
    }


def curry(f, *c_args, **c_kwargs):
    @wraps(f)
    def c(*args, **kwargs):
        if args or kwargs:
            return curry(f, *(c_args + args), *{**c_kwargs, **kwargs})
        else:
            return f(*c_args, **c_kwargs)
    return c
