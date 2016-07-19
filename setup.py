# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='more_functools',
    version='0.1',
    install_requires=[
        'sqlalchemy',
        'MySQL-python',
        'cached_property',
        'backports.functools_lru_cache',
    ],
    author='michael',
    py_modules=['more_functools'],
    author_email='warrior2031@mail.ru',
    description='sqlalchemy based models for ISS'
)
