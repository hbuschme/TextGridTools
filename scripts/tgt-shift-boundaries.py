#!/usr/bin/env python
# -*- coding: utf-8 -*-

# tgt-shift-boundaries.py - Shift all boundaries in a TextGrid
# Copyright (C) 2016 Hendrik Buschmeier
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

from __future__ import division, print_function

import argparse
import os.path
import sys

import tgt


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument(
		'shift',
		help='offset by which to shift the boundaries (positive or negative)',
		type=float)
	ap.add_argument(
		'file',
		help='the textgrid file',
		type=str)
	ap.add_argument(
		'-e', '--encoding',
		help='file encoding (default "utf-8")',
		default='utf-8',
		type=str)
	ap.add_argument(
		'-f', '--format',
		help='the output format (default "short")',
		default='short',
		type=str)
	ap.add_argument(
		'-o', '--outfile',
		help='the output file (defaults to inputfile.shifted.Extension)',
		type=str)
	arguments = ap.parse_args()

	# Read file
	try:
		tg = tgt.read_textgrid(
				filename=arguments.file,
				encoding=arguments.encoding)
	except IOError:
		print('An error occurred reading file {file}'.
				format(file=arguments.file))
		sys.exit(1)
	# Create new textgrid
	if arguments.outfile is None:
		basename, extension = os.path.splitext(arguments.file)
		output_filename = basename + '.shifted' + extension
	else:
		output_filename = arguments.outfile
	tg_shifted = tgt.TextGrid(filename=output_filename)
	# Shift boundaries
	for tier in tg:
		ts = tgt.util.shift_boundaries(tier, arguments.shift, 0)
		tg_shifted.add_tier(ts)
	# Write file
	tgt.write_to_file(
		textgrid=tg_shifted,
		filename=tg_shifted.filename,
		format=arguments.format,
		encoding=arguments.encoding)


if __name__ == '__main__':
	main()
