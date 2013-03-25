# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2011-2013 Hendrik Buschmeier, Marcin Włodarczak
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

import sys

from .core import TextGrid
from .core import Tier, IntervalTier, PointTier
from .core import Annotation, Interval, Point
from .core import Time

if sys.version_info < (3, 0):
	from . import io
	from .io import read_textgrid, write_to_file
else:
	from . import io3 as io
	from .io3 import read_textgrid, write_to_file

from . import agreement, util

__all__ = [
    'TextGrid',
    'Tier', 'IntervalTier', 'PointTier',
    'Annotation', 'Interval', 'Point',
    'Time',
    'read_textgird,' 'write_to_file',
    'agreement', 'io', 'util',

]
