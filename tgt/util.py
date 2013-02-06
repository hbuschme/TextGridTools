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

from __future__ import division

import re

from .core import TextGrid, IntervalTier, Interval

##  High-level functions
##----------------------------------------------------------------------------

def shift_boundaries(tier, left, right):
    """
    Return a copy of the tier with boundaries shifted by the specified
    amount of time (in seconds). Positive values expand the tier and negative values shrink
    it, i.e.:
    * positive value of left shifts the left boundary to the left
    * negative value of left shifts the left boundary to the right
    * positive value of right shifts the right boundary to the right
    * negative value of right shifts the right boundary to the left.
    """

    tier_end_shifted = tier.end_time + left + right
    tier_shifted = IntervalTier(start_time=0,
                                end_time=tier_end_shifted,
                                name=tier.name)

    for i, interval in enumerate(tier.intervals):

        if interval.end_time <= left * -1:
            continue
        elif i > 0 and interval.start_time > left * -1:
            interval_start_shifted = interval.start_time + left
        else:
            interval_start_shifted = 0

        interval_end_shifted = interval.end_time + left
        if (interval_start_shifted >= tier_end_shifted):
            break
        elif i == len(tier.intervals) - 1 or interval_end_shifted > tier_end_shifted:
            interval_end_shifted = tier_end_shifted

        tier_shifted.add_annotation(Interval(interval_start_shifted,
                                           interval_end_shifted,
                                           interval.text))
    return tier_shifted


def get_overlapping_intervals(tier1, tier2, regex=r'[^\s]+', overlap_label=None):
    '''Return a list of overlaps between intervals of tier1 and tier2.
    If no overlap_label is specified, concatenated labels
    of overlapping intervals are used as the resulting label.
    
    All nonempty intervals are included in the search by default.
    '''
    if not isinstance(tier2, IntervalTier):
        raise TypeError('Argument is not an IntervalTier')
    intervals1 = tier1.intervals
    intervals2 = tier2.intervals
    overlaps = []
    i, j = 0, 0
    while i < len(tier1) and j < len(tier2):
        lo = max(intervals1[i].start_time, intervals2[j].start_time)
        hi = min(intervals1[i].end_time, intervals2[j].end_time)
        if (lo < hi and re.search(regex, intervals1[i].text)
            and re.search(regex, intervals2[j].text)):
            if overlap_label is None:
                text = '+'.join([intervals1[i].text, intervals2[j].text])
            else:
                text = overlap_label
            overlaps.append(Interval(lo, hi, text))
        if intervals1[i].end_time < intervals2[j].end_time:
            i += 1
        else:
            j += 1
    return overlaps


def concatenate_textgrids(textgrids, ignore_nonmatching_tiers=False):
    '''Concatenate Tiers with matching names.

    TextGrids are concatenated in the order they are specified. If 
    ignore_nonmatching_tiers is False, an exception is raised if the
    number and the names of tiers differ between TextGrids.
    '''
    tier_names_intersection = set.intersection(
        *[set(tg.get_tier_names()) for tg in textgrids])
    # Check whether the TextGrids have the same number of tiers
    # and whether tier names match. If they don't
    # and if ignore_nonmatching_tiers is False, raise an exception.
    if (not ignore_nonmatching_tiers
        and not all([len(tier_names_intersection) == len(tg) for tg in textgrids])):
        raise Exception('TextGrids have different numbers of tiers or tier names do not match.')
    tot_duration = 0
    tiers = {}  # tier_name : tgt.Tier()
    for textgrid in textgrids:
        for tier in textgrid:
            if tier.name not in tier_names_intersection:
                continue
            intervals = []
            # If this is the first we see this tier, we just make a copy
            # of it as it is.
            if tier.name not in tiers.keys():
                tiers[tier.name] = copy.deepcopy(tier)
            # Otherwise we update the start and end times of intervals
            # and append them to the first part.
            else:
                for interval in tier.intervals:
                    interval.start_time += tot_duration
                    interval.end_time += tot_duration
                    intervals.append(interval)
                tiers[tier.name].add_annotations(intervals)
        tot_duration += textgrid.end_time
    # Create a new TextGrid and add the concatenated tiers
    textgrid_concatenated = TextGrid()
    # Add tiers in the order they're found in the first TextGrid.
    textgrid_concatenated.add_tiers(
        [tiers[x] for x in tier_names_intersection])
    return textgrid_concatenated


def merge_textgrids(textgrids, ignore_duplicates=True):
    '''Return a TextGrid object with tiers in all textgrids.p

    If ignore_duplicates is False, tiers with equal names are renamed
    by adding a path of the textgrid or a unique number incremented
    with each occurrence.
    '''
    tg_merged = TextGrid()
    tier_duplicates_lookup = collections.defaultdict(int)
    for tg in textgrids:
        for tier in tg:
            tier_copy = copy.deepcopy(tier)
            if tg_merged.has_tier(tier.name):
                if not ignore_duplicates:
                    if tg.filename.strip() != '':
                        tier_copy.name += '_' + tg.filename
                    else:
                        tier_duplicates_lookup[tier.name] += 1
                        tier_copy.name += '_' + str(tier_duplicates_lookup[tier.name])
                else:
                    continue
            tg_merged.add_tier(tier_copy)
    return tg_merged
