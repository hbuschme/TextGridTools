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

from __future__ import print_function, division

import copy

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
    return vars(argparser.parse_args())

def concatenate_textgrids(input_files, encoding):
    """Concatenate Tiers with matching names. TextGrids are concatenated
    in the order they are specified. The number and the names of tiers
    must be the same in each TextGrid."""
    
    # Read all TextGrids into a list.
    textgrids = [tgt.read_short_textgrid(path, encoding) for path in input_files]

    # Check whether the TextGrids have the same number of tiers.
    ntiers = [len(x) for x in textgrids]
    assert all([ntiers[0] == x for x in ntiers[1:]]),\
            'TextGrids have different numbers of tiers.'

    # Check whether tiers in the TextGrids have the same names.
    tier_names = [sorted(x.get_tier_names()) for x in textgrids]
    assert all([tier_names[0] == x for x in tier_names[1:]]),\
           'Names of tiers do not match.' 

    tot_duration = 0
    tiers = {} # tier_name : tgt.Tier()

    for textgrid in textgrids:
        for tier in textgrid.tiers:
            intervals = []

            # If this is the first we see this tier, we just make a copy
            # of it as it is.
            if tier.name not in tiers.keys():
                tiers[tier.name] = copy.deepcopy(tier)
            # Otherwise we update the start and end times of intervals
            # and append them to the first part.
            else:
                for interval in tier.intervals:
                    interval.left_bound += tot_duration
                    interval.right_bound += tot_duration
                    intervals.append(interval)
                tiers[tier.name].add_intervals(intervals)
        tot_duration += textgrid.end_time()

    # Create a new TextGrid
    textgrid_concatenated = tgt.TextGrid()
    # Add tiers in the order they're found in the first TextGrid.
    textgrid_concatenated.add_tiers([tiers[x] for x in textgrids[0].get_tier_names()])
    return textgrid_concatenated

def main():
    # Parse the command-line arguments.
    args = parse_arguments()
    textgrid_concatenated = concatenate_textgrids(args['input_files'], args['encoding'][0])
    # Write the concatenated TextGrid to a file.
    textgrid_concatenated.write_to_file(args['output_file'][0], args['encoding'][0])

if __name__ == '__main__':
    main()


