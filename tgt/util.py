# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2011-2016 Hendrik Buschmeier, Marcin Włodarczak
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
import collections
import copy

from .core import (TextGrid, IntervalTier, Interval, Point, 
    TextGridToolsException)

##  High-level functions
##----------------------------------------------------------------------------

def shift_boundaries(tier, left, right):
    """
    Return a copy of the tier with boundaries shifted by the specified
    amount of time (in seconds). Positive values expand the tier and negative
    values shrink it, i.e.:
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

        if interval.start_time > left * -1:
            interval_start_shifted = interval.start_time + left
        else:
            interval_start_shifted = 0

        interval_end_shifted = interval.end_time + left
        if (interval_start_shifted >= tier_end_shifted):
            break
        elif interval_end_shifted > tier_end_shifted:
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


def concatenate_tiers(tier1, tier2, offset):
    """Concatenate two tiers and return a new tier.

    Offset is the time added to each interval's boundaries in order to
    put them after the intervals of the preceeding tier. If intervals
    have absolute timing on each tier (i.e., start times of tier > 0 for
    later tiers, an offset of 0 should be used).

    Keyword argument:
    tier1 -- Tier object
    tier2 -- Tier object
    offset -- float (>= 0)
    """
    result = copy.deepcopy(tier1)
    for annotation in tier2:
        if hasattr(tier1, 'intervals') and hasattr(tier2, 'intervals'):
            result.add_annotation(Interval(
                start_time=annotation.start_time + offset,
                end_time=annotation.end_time + offset,
                text=annotation.text))
        elif hasattr(tier1, 'points') and hasattr(tier2, 'points'):
            result.add_annotation(Point(
                time=annotation.time + offset,
                text=annotation.text))
        else:
            raise TextGridToolsException()
        result.end_time = tier2.end_time + offset
    return result


def concatenate_textgrids(
        textgrids,
        ignore_nonmatching_tiers=False,
        use_absolute_time=False):
    """Concatenates TextGrid objects and return a new one.

    If `ignore_nonmatching_tiers` is `False`, an exception is raised
    if the number or names of tiers differ among the TextGrids.

    If `use_absolute_time` is `False`, start and end times of 
    intervals are offset by the end_time of the preceeding tier.
    If `use_absolute_time` is `True`, start and end times of
    intervals are used as is. This is useful if start_time of textgrids
    does not equal 0.

    Keyword argument:
    textgrids -- a list of TextGrid objects
    ignore_nonmatching_tiers -- a boolean (default False)
    use_absolute_time -- a boolean (default False)
    """
    common_tiers = set.intersection(
        *[set(tg.get_tier_names()) for tg in textgrids])
    if (not ignore_nonmatching_tiers and
            not all([len(common_tiers) == len(tg) for tg in textgrids])):
        raise TextGridToolsException(
            'Different numbers of tiers or non-matching tier names.')
    ccd_tiers = {}
    offset = 0
    for textgrid in textgrids:
        for tier in textgrid:
            if tier.name not in common_tiers and ignore_nonmatching_tiers: 
                continue
            if not tier.name in ccd_tiers:
                ccd_tiers[tier.name] = copy.deepcopy(tier)
            else:
                ccd_tiers[tier.name] = concatenate_tiers(
                    tier1=ccd_tiers[tier.name], 
                    tier2=tier, 
                    offset=0 if use_absolute_time else offset)
        offset = max([tier.end_time for tier in ccd_tiers.values()])
    result_tg = TextGrid()
    result_tg.add_tiers([ccd_tiers[x] for x in common_tiers]) #preserve order
    return result_tg


def merge_textgrids(textgrids, ignore_duplicates=True):
    '''Return a TextGrid object with tiers in all textgrids.

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

## Chronogram
## ---------------------------------------------------------------------------

def chronogram(tiers, speech_label=None, silence_label=None):

    '''Construct a chronogram between intervals in input tiers.
    Interval labels are classified as silences or volcalisations
    by matching them against the speech_label and the silence_label
    regular expressions. By default all intervals with empty or
    whitespace-only labels are treated as silences.

    The code is a generalisation of Jaffe and Feldstein's (1970) 
    6-state Markov model to an arbitrary number of speakers. Instances
    of silences and overlaps are classified as within-speaker-overlap
    (wso), between-speaker-overlap (bso), within-speaker-silence (wss)
    or between-speaker-silence (bss).  Individual vocalistions are
    labelled with the the source tier name.
    '''
    

    # Calculate communicatfive states for each tier.
    communicative_states = classify_communicative_state(tiers, speech_label, silence_label)
    
    is_joint_state = lambda st: st == 'none' or st.find(',') > 0
    is_single_state = lambda st: not is_joint_state(st)

    chrono = IntervalTier(name='chronogram-{0}'.format('-'.join(t.name for t in tiers)))
    prev_single = None

    for i in range(len(communicative_states)):

        cur_start = communicative_states[i].start_time
        cur_end = communicative_states[i].end_time
        cur_state = communicative_states[i].text

        # Make sure there are no consecutive same state sequences
        if i > 0:
            prev_state = communicative_states[i - 1].text
            assert  prev_state != cur_state,\
                'Consecutive same states: {0}, {1}'.format(prev_state, cur_state)

        if is_joint_state(cur_state):

            # If we have not seen a single-speaker vocalisation, skip it.
            if  prev_single is None:
                continue

            try:
                next_state = communicative_states[i + 1].text
            except IndexError:
                next_state = None
            
            # Transitions between joint states do not result in speaker change.
            # The same is true for transitions from a joint state to a single state 
            # equal to the previous single state and for file-final joint states.
            if (next_state is None or is_joint_state(next_state)
                or (is_single_state(next_state) and prev_single == next_state)):

                chrono.add_interval(
                    Interval(start_time=cur_start, end_time=cur_end,
                             text='wso:{}'.format(cur_state) if cur_state != 'none' else 'wss'))
            else:
                chrono.add_interval(
                    Interval(start_time=cur_start, end_time=cur_end,
                             text='bso:{}'.format(cur_state) if cur_state != 'none' else 'bss'))
        # Label single vocalisations with the source tier name.
        elif is_single_state(cur_state):
            chrono.add_interval(Interval(start_time=cur_start, end_time=cur_end, text=cur_state))
            prev_single = cur_state
        else:
            raise Exception('Unknown cummunicative state: {0}'.format(cur_state))

    # FIXME: Should a dictionary with communicative labels and the chronogram be 
    # returned instead of the chronogram itself?
    # return {'communicative_labels': communicative_states, 'chronogram': chrono}
    return chrono

def communicative_labels(tiers, voc_re=None, silence_re=None):

    if silence_re is not None:
        speech_tiers = [t.name for t in tiers if re.search(silence_re, t[0].text) is None]
    else:
        if voc_re is None:
            voc_re = r'[^\s]+'
        speech_tiers = [t.name for t in tiers if re.search(voc_re, t[0].text) is not None]

    if not speech_tiers:
        return 'none'
    else:
        return ','.join(speech_tiers)

def classify_communicative_state(tiers, speech_label=None, silence_label=None):

    # Fill all gaps with empty intervals and ensure the tiers have
    # identical start and end times
    start_time_earliest = min(tier.start_time for tier in tiers)
    end_time_latest = max(tier.end_time for tier in tiers)

    tiers_filled = [tier.get_copy_with_gaps_filled(start_time=start_time_earliest,
                                                   end_time=end_time_latest)
                    for tier in tiers]

    communicative_states = IntervalTier(name='communicative_states')


    while all(tiers_filled):
        lo = max(x[0].start_time for x in tiers_filled)
        hi = min(x[0].end_time for x in tiers_filled)
        
        if lo < hi:
            com_state = communicative_labels(tiers_filled, speech_label, silence_label)
            communicative_states.add_annotation(Interval(lo, hi, com_state))

        for t in tiers_filled:
            if t[0].end_time == hi:
                del t[0]

    # Merge consecutive intervals with indentical labels
    communicative_states = communicative_states.get_copy_with_same_intervals_merged()
    return communicative_states

def turns(chrono):

    '''Returns turns (defined as intervals bounded by solo vocalisations
    of two different speakers) given a chronogram.
    '''

    turns = IntervalTier(name = 'turns')
    prev_solo = None

    for intr in chrono:
        if intr.text[:3] in ['wso', 'bso', 'wss', 'bss']:
            continue
        elif prev_solo is None:
            cur_turn = Interval(intr.start_time, intr.end_time, intr.text)
            prev_solo = intr.text
        elif intr.text != prev_solo:
            cur_turn.end_time = intr.start_time
            turns.add_interval(cur_turn)
            cur_turn = Interval(intr.start_time, intr.end_time, intr.text)
            prev_solo = intr.text
    else:
        cur_turn.end_time = intr.end_time
        turns.add_interval(cur_turn)
    return turns
