#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2011 Hendrik Buschmeier
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(
    name='tgt',
    description='TextGridTools -- Read, write, and manipulate Praat TextGrid files',
    version='1.0.2',
    packages=['tgt'],
    scripts=[
    	'scripts/tgt-concatenate-textgrids.py',
    	'scripts/tgt-print-tiernames.py',
    ],
    maintainer='Hendrik Buschmeier',
    maintainer_email='hbuschme@uni-bielefeld.de',
    license='GNU General Public License 3',
    download_url='http://github.com/hbuschme/TextGridTools/',
    classifiers=[
    	'Development Status :: 5 - Production/Stable',
    	'Intended Audience :: Science/Research',
    	'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    	'Programming Language :: Python',
    	'Programming Language :: Python :: 2.7',
    	'Programming Language :: Python :: 3',
    	'Programming Language :: Python :: 3.3',
    	'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
