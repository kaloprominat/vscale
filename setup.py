#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from vscale import __version__

setup(
    name='vscale',
    version=__version__,
    packages = ['vscale'],
    entry_points={
        'console_scripts': [
            'vscalectl=vscale.__main__:main'
        ]
    }
)