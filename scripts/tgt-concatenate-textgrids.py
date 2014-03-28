#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Concatenate Praat TextGrid files.
# Copyright (C) 2011 Marcin Włodarczak
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

import argparse

import tgt

def parse_arguments():
    """Parse the command-line arguments."""
    argparser = argparse.ArgumentParser(description='Concatenate Praat TextGrid files.')
    argparser.add_argument('-i', type=str, nargs='+', required=True, dest='input_files',
                        help='Space-separated list of paths to TextGrid files in the\
                              order they should be concatenated.')
    argparser.add_argument('-o', type=str, nargs=1, required=True, dest='output_file',
                        help='Path to the resulting file.')
    argparser.add_argument('-e', type=str, nargs=1, dest='encoding', default='utf-8',
                        help='File encoding (defaults to UTF-8).')
    argparser.add_argument('-t', type=str, nargs=1, dest='type', default='short',
                        help='TextGrid format: short, long (defaults to short)')
    return vars(argparser.parse_args())

def main():
    # Parse the command-line arguments.
    args = parse_arguments()
    # Read all TextGrids into a list.
    textgrids = [tgt.io.read_textgrid(path, args['encoding']) for path in args['input_files']]
    textgrid_concatenated = tgt.util.concatenate_textgrids(textgrids)
    # Write the concatenated TextGrid to a file.
    tgt.io.write_to_file(textgrid=textgrid_concatenated, filename=args['output_file'][0], format='short', encoding=args['encoding'])


if __name__ == '__main__':
    main()


