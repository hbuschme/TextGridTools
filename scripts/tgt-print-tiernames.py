#!/usr/bin/env python
# -*- coding: utf-8 -*-

# print-tiernames.py - Prints the tier names of a textrid file
# Copyright (C) 2012 Hendrik Buschmeier
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
#
# Prints the name of the tiers of the specified textgrid files.
# If a directory is specified, all tier names of the .TextGrid
# files contained in this directory are printed.

from __future__ import print_function, division

import os
import sys

import tgt

EXTENSION = 'TextGrid'

def print_tiernames(filenames):
	for filename in filenames:
		try:
			tg = tgt.io.read_textgrid(filename)
			print(filename)
			for tiername in tg.get_tier_names():
				print('\t' + tiername)
		except Exception, err:
			print(filename + ' caused a problem.')
			sys.stderr.write('ERROR: %s\n' % str(err))


def main(argv=None):
	if argv is None:
		argv = sys.argv
	if len(argv) < 2:
		print('USAGE: ' + argv[0] + ' <list of TextGrid files or directories>')
	list_of_tg_files = []
	for arg in argv[1:]:
		if os.path.exists(arg):
			if os.path.isdir(arg):
				list_of_tg_files += [arg + '/' + filename for filename in os.listdir(arg) if filename.endswith(EXTENSION)]
			else:
				list_of_tg_files.append(arg)
		else:
			raise FileNotFoundException(arg)
	print_tiernames(list_of_tg_files)

if __name__ == '__main__':
    sys.exit(main())
