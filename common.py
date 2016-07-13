# -*- coding: utf-8 -*-
from functools import reduce
from itertools import tee, islice, izip_longest
from collections import namedtuple, Mapping


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
    return frozenset(
        (k, transform(v))
        for k, v in dct.iteritems()
    )

transformers = {
    (Mapping, dict_to_set),
    (list, tuple),
    (set, frozenset),
}


def transform(obj):
    transformer =  next(
        (f for cls, f in transformers if isinstance(obj, cls)),
        lambda x: x
    )
    return transformer(obj)


def dict_structure(dct):
    return {
        k: (type(v),) + ((dict_structure(v),) if isinstance(v, Mapping) else ())
        for k, v in dct.iteritems()
    }


def set_to_dict(s, structure):
    return {
        k: set_to_dict(v, struct[0]) if initial_type == dict else initial_type(v)
        for k, v, initial_type, struct in (
            (k, v, structure[k][0], structure[k][1:])
            for k, v in s
        )
    }


def dmap(f, d, *path):
    if path:
        key, path_tail = path[0], path[1:]
        if key is None:
            func = lambda k, v: dmap(f, v, *path_tail)
        else:
            func = lambda k, v: dmap(f, v, *path_tail) if k == key else v
    else:
        func = lambda k, v: f(v)
    return {k: func(k, v) for k, v in d.iteritems()}
