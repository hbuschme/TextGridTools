#!/usr/bin/env python
# -*- coding: utf-8 -*-

# tgt-extract-part.py - Extract part of a TextGrid.
# Copyright (C) 2015 Marcin Włodarczak
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
import os

import tgt

def parse_arguments():
    """Parse the command-line arguments."""
    argparser = argparse.ArgumentParser(description='Concatenate Praat TextGrid files.')
    argparser.add_argument('tg_path', type=str,
                           help='Path to the input TextGrid')
    argparser.add_argument('-s', type=float, dest='offset_start',
                           help='Start time of the interval to be extracted.')
    argparser.add_argument('-e', type=float, dest='offset_end',
                           help='End time of the interval to be extracted.')
    argparser.add_argument('-o', type=str, nargs=1, dest='outpath', 
                           help='Path to the output file. Defaults to the original path with _part appended to the filename.')
    return vars(argparser.parse_args())

def main():

    # Parse the command-line arguments.
    args = parse_arguments()
    tg_path = args['tg_path']
    offset_start = args['offset_start']
    offset_end = args['offset_end']
    outpath = args['outpath']

    # Read the TextGrid
    tg = tgt.read_textgrid(tg_path)
    tg_part = tgt.TextGrid()

    if offset_start is None and offset_end is None:
        raise Exception('At least one of offset_start and offset_end must be specified.')
    elif offset_start is None:
        offset_start = tg.start_time
    elif offset_end is None:
        offset_end = tg.end_time

    for tr in tg:
        intr_part = tr.get_annotations_between_timepoints(
            offset_start, offset_end)
        tier_part = tgt.IntervalTier(
            name=tr.name,
            start_time=tr.start_time,
            end_time=tr.end_time,
            objects=intr_part)
        tg_part.add_tier(tier_part)


    if outpath is None:
        tg_dirname, tg_filename = os.path.split(tg_path)
        outpath = os.path.splitext(tg_filename)[0] + '_part.TextGrid'

    tgt.write_to_file(tg_part, outpath)

if __name__ == '__main__':
    main()

