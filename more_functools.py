# -*- coding: utf-8 -*-
from collections import Mapping, defaultdict, deque, namedtuple
from functools import partial, reduce, wraps
from inspect import signature
from itertools import chain, islice, permutations, tee
from operator import itemgetter

from six import iteritems as items, iterkeys as keys
from six.moves import zip_longest


class EqualByValue(object):
    def __eq__(self, other):
        return type(other) is type(self) and vars(self) == vars(other)


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def unpack(f):
    """
        Takes function that takes one or more positional arguments
        and return function that takes one iterable argument.
        Usefull in py3 because you can't do things like that
        >> a = [(1, 2), (3, 4)]
        >> map(lambda (x, y): x + y, a)
        or
        >> def sum_vector((x1, y1), (x2, y2)):
        >>     return (x1 + x2, y1 + y2)
        >> sum_vector((1, 2), (3, 4))
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


def curry(func=None, *required):
    if not func:
        return partial(curry, *required)
    sig = signature(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            bounded_args = sig.bind(*args, **kwargs)
            if any(param not in bounded_args for param in required):
                raise TypeError()
        except TypeError:
            return partial(wrapper, *args, **kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper


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
                d() if callable(d) else d
                for ex_type, d in items(defaults) if isinstance(e, ex_type)
            )
    return wrapper


def concat(sequence, *sequences):
    return chain(sequence, *sequences) if sequences else chain.from_iterable(sequence)


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


def last(sequence):
    return deque(sequence, maxlen=1).pop()
