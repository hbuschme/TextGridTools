#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2011 Hendrik Buschmeier, Marcin Włodarczak
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
import bisect
import codecs
import collections
import copy
import datetime
import math
import operator
import re

__all__ = [
    # Classes
    'TextGrid', 'IntervalTier', 'Interval', 'PointTier', 'Point', 'Time',
    # Functions
    'read_textgrid', #'read_short_textgrid', 'read_long_textgrid',
    'export_to_short_textgrid', 'export_to_long_textgrid', 'export_to_elan',
    'export_to_table', 'write_to_file',
    'get_overlapping_intervals', 'merge_textgrids', 'concatenate_textgrids'
]


class TextGrid(object):
    '''A TextGrid.'''

    def __init__(self, filename=''):
        super(TextGrid, self).__init__()
        self._tiers = []
        self.filename = filename

    tiers = property(fget=lambda self: self._tiers,
                     doc='Tiers in this TextGrid object.')

    def add_tier(self, tier):
        """Add a tier."""
        self._tiers.append(tier)

    def add_tiers(self, tiers):
        """Add a list of tiers."""
        for tier in tiers:
            self.add_tier(tier)

    def insert_tier(self, tier, position):
        """Insert a tier at the specified position."""
        self._tiers.insert(position, tier)

    def delete_tier(self, tier_name):
        '''Delete a tier.'''
        tier = self.get_tier_by_name(tier_name)
        self.tiers.remove(tier)

    def delete_tiers(self, tier_names, complement=False):
        '''Delete a list of tiers.

        If complement is False, delete tiers with the specified names.
        If complement is True, delete tiers not specified.
        '''
        if not complement:
            self._tiers = [tier for tier in self._tiers 
                if tier.name not in tier_names]
        else:
            self._tiers = [tier for tier in self._tiers
                if tier.name in tier_names]

    def get_tier_names(self):
        '''Get names of all tiers.'''
        return [tier.name for tier in self._tiers]

    def has_tier(self, name):
        '''Check whether TextGrid has a tier of the specified name.'''
        return name in self.get_tier_names()

    def get_tier_by_name(self, name):
        '''Get tier of specified name.'''
        for tier in self._tiers:
            if tier.name == name:
                return tier
        raise ValueError('Textgrid ' + self.filename +
                    ' does not have a tier called "' + name + '".')

    def _get_earliest_start_time(self):
        '''Return the earliest start time among all tiers.'''
        return min([tier.start_time for tier in self])

    start_time = property(fget=_get_earliest_start_time,
                          doc='TextGrid start time.')

    def _get_latest_end_time(self):
        '''Return the latest end time among all tiers.'''
        return max([tier.end_time for tier in self])

    end_time = property(fget=_get_latest_end_time,
                        doc='TextGrid end time.')

    def __contains__(self, name):
        return self.has_tier(name)

    def __iter__(self):
        '''Return an iterator over the tiers of this TextGrid.'''
        return iter(self._tiers)

    def __len__(self):
        '''Return the number of tiers.'''
        return len(self._tiers)


class Tier(object):
    "An abstract tier."

    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(Tier, self).__init__()
        self._specd_start_time = Time(start_time)
        self._specd_end_time = Time(end_time)
        self.name = name
        self._objects = []
        if objects is not None and objects != []:
            self._add_objects(objects)

    def _get_start_time(self):
        '''Get start time of this tier.'''
        if len(self._objects) > 0:
            return min([self._objects[0].start_time, self._specd_start_time])
        else:
            return self._specd_start_time

    start_time = property(fget=_get_start_time, doc='Start time.')

    def _get_end_time(self):
        '''Get end time of this tier.'''
        if len(self._objects) > 0:
            return max([self._objects[-1].end_time, self._specd_end_time])
        else:
            return self._specd_end_time

    end_time = property(fget=_get_end_time, doc='End time.')

    def _add_object(self, obj):
        '''Adds an annotation object to this tier.

        The annotation object is inserted at the correct position within the
        tier. If the space is already (partially) occupied by a different
        annotation object, a ValueError is raised.
        '''
        if ((len(self._objects) > 0 and obj.start_time >= self._objects[-1].end_time) 
                or len(self._objects) == 0): # can we simply append obj?
            self._objects.append(obj)
        else: # no, we need to insert it
            overlapping_objects = self._get_objects_between_timepoints(
                obj.start_time, obj.end_time, 
                left_overlap=True, right_overlap=True)
            if overlapping_objects == []:
                start_timepoints = [interval.start_time for interval in self._objects]
                position = bisect.bisect_left(start_timepoints, obj.start_time)
                self._objects.insert(position, obj)
            else:
                raise ValueError(
                    'Could not add object {0} to this tier: Overlap.'.format(
                        repr(object)))

    def _add_objects(self, objects):
        """Add a sequence of annotation objects."""
        for obj in objects:
            self._add_object(obj)

    def _get_object_by_start_time(self, time):
        '''Get the annotation object that starts at time.'''
        idx = bisect.bisect_left([obj.start_time for obj in self], time)
        if (idx < len(self) and self._objects[idx].start_time == time):
            return self._objects[idx]
        else:
            return None

    def _get_object_by_end_time(self, time):
        '''Get the annotation object that ends at time.'''
        idx = bisect.bisect_left([obj.end_time for obj in self], time)
        if (idx < len(self) and self._objects[idx].end_time == time):
            return self._objects[idx]
        else:
            return None

    def _get_objects_by_time(self, time):
        '''Get annotation objects at the specified time.'''
        idx = bisect.bisect_left([obj.end_time for obj in self], time)
        if (idx < len(self._objects) and 
            time >= self._objects[idx].start_time):
            if (len(self._objects) > idx+1
                and self._objects[idx+1].start_time == time):
                return [self._objects[idx], self._objects[idx+1]]
            else:
                return [self._objects[idx]]
        else:
            return []

    def _get_objects_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        '''Get annotation objects between start and end.

        If left_overlap or right_overlap is False annotation objects
        overlapping with start or end are excluded.
        '''
        start_timepoints = [interval.start_time for interval in self._objects]
        end_timepoints = [interval.end_time for interval in self._objects]
        if left_overlap:
            index_lo = bisect.bisect_right(end_timepoints, start)
        else:
            index_lo = bisect.bisect_left(start_timepoints, start)
        if right_overlap:
            index_hi = bisect.bisect_left(start_timepoints, end)
        else:
            index_hi = bisect.bisect_right(end_timepoints, end)
        return self._objects[index_lo:index_hi]

    def _get_nearest_objects(self, time, regex=r'.*', boundary='both',
                             direction='both', exclude_overlapped=False):
        '''Get the annotation object(s) nearest to time.

        Boundary specifies whether the distance to an annotation object
        is calculated based on its start time ('start'), end time
        ('end') or both ('both'). Direction specifies whether it is
        looked to the left hand side of time ('left'), to the right
        hand side of time ('right') or to both sides ('both').
        Annotation objects overlapping with time can be excluded.
        '''
        # Filter for specified regular expression
        matching_objects = self._get_objects_with_matching_text(pattern=regex, regex=True)
        # Exclude overlapping intervals from search
        if exclude_overlapped:
            overlapping_objects = self._get_objects_by_time(time)
            for oo in overlapping_objects:
                if oo in matching_objects:
                    matching_objects.remove(oo)
        # Extract start and end boundary times and calculate their
        # distance to the reference point, this gives a list of tuples
        # (boundary time, distance, start/end)
        if boundary in ['start', 'both']:
            start_boundaries = [(obj.start_time, time - obj.start_time,
                'start') for obj in matching_objects]
        if boundary in ['end', 'both']:
            end_boundaries = [(obj.end_time, time - obj.end_time,
                'end') for obj in matching_objects]
        # Depending on search direction and boundary type, compute the
        # candidate boundary times with minimum distance to the
        # reference point. Candidates are still tuples
        candidates = []
        if direction in ['left', 'both']:
            if boundary in ['start', 'both']:
                # Filter for left hand side
                sl = [x for x in start_boundaries if x[1] >= 0]
                if len(sl) > 0:
                    candidates.append(min(sl, key=operator.itemgetter(1)))
            if boundary in ['end', 'both']:
                # Filter for left hand side
                el = [x for x in end_boundaries if x[1] >= 0]
                if len(el) > 0:
                    candidates.append(min(el, key=operator.itemgetter(1)))
        if direction in ['right', 'both']:
            if boundary in ['start', 'both']:
                # Filter for right hand side, make distance positive
                sr = [(x[0], x[1]*-1, x[2]) for x in start_boundaries if x[1] <= 0]
                if len(sr) > 0:
                    candidates.append(min(sr, key=operator.itemgetter(1)))
            if boundary in ['end', 'both']:
                # Filter for right hand side, make distance positive
                er = [(x[0], x[1]*-1, x[2]) for x in end_boundaries if x[1] <= 0]
                if len(er) > 0:
                    candidates.append(min(er, key=operator.itemgetter(1)))
        #print('Candidates: ' + str(candidates)) # DEBUG
        # Compute corresponding annotation objects for all candidates
        # that have the minimum distance to the reference point and
        # collect the unique ones
        if len(candidates) > 0:
            min_distance = min(candidates, key=operator.itemgetter(1))[1]
            results = set()
            for candidate in candidates:
                if candidate[1] == min_distance:
                    if candidate[2] == 'start':
                        results.add(self._get_object_by_start_time(candidate[0]))
                    elif candidate[2] == 'end':
                        results.add(self._get_object_by_end_time(candidate[0]))
            #print('Result: ' + str(results) # DEBUG
            return list(results)
        else:
            return []

    def _get_objects_with_matching_text(self, pattern='', n=0, regex=False):
        '''Get annotation objects with text matching the pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned. The 
        pattern is treated as a regular expression, if regex is True.
        '''
        if regex:
            result = [obj for obj in self if re.search(pattern, obj.text)]
        else:
            result = [obj for obj in self if obj.text == pattern]
        if n == 0:
            return result  # Return all matching intervals
        elif n > 0:
            return result[:n]  # Return the first n matching intervals
        else:  # i.e., n < 0
            return result[n:]  # Return the last n matching intervals
       
    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        '''Return number of annotation objects in this tier.'''
        return len(self._objects)

    def __repr__(self):
        return '{0}(start_time={1}, end_time={2}, name="{3}", objects={4})'.format(self.__class__.__name__,
            self.start_time, self.end_time, self.name, self._objects)


class IntervalTier(Tier):
    '''An IntervalTier.'''

    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(IntervalTier, self).__init__(Time(start_time), Time(end_time),
            name, objects)

    def add_interval(self, interval):
        '''Add an interval to this tier.'''
        self._add_object(interval, Interval)

    def add_intervals(self, intervals):
        '''Add a sequence of intervals to this tier.'''
        self._add_objects(intervals, Interval)

    def _get_intervals(self):
        """Get all intervals of this tier."""
        return self._objects

    intervals = property(fget=_get_intervals,
                doc='The list of intervals of this tier.')

    def get_interval_by_start_time(self, start_time):
        '''Get the interval that starts at time.'''
        self._get_object_by_start_time(start_time)

    def get_interval_by_end_time(self, end_time):
        '''Get the interval that ends at time.'''
        self._get_object_by_end_time(end_time)

    def get_intervals_by_time(self, time):
        """Get intervals at the specified time."""
        return self._get_objects_by_time(time)

    def get_intervals_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        '''Get intervals between start and end.

        If left_overlap or right_overlap is False intervals overlapping
        with start or end are excluded.
        '''
        return self._get_objects_between_timepoints(start, end, left_overlap, right_overlap)

    def get_nearest_interval(self, time, direction='both', regex=r'[^\s]+', exclude_overlapped=False):
        pass

    def get_intervals_with_regex(self, regex=r'[^\s]+', n=0):
        '''Get intervals with text matching the regex pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned.
        '''
        return self._get_objects_with_matching_text(regex, n, regex=True)

    def get_intervals_with_text(self, text, n=0):
        '''Get intervals with text matching the pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned.
        '''
        return self._get_objects_with_text(text, n, regex=False)


class PointTier(Tier):
    '''A PointTier (also "TextTier").'''

    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(PointTier, self).__init__(Time(start_time), Time(end_time),
            name, objects)

    def add_points(self, points):
        """Adds a list of points to this tier."""
        self._add_objects(points, Point)

    def add_point(self, point):
        """Add a point to this tier."""
        self._add_object(point, Point)

    def _get_points(self):
        """Get all points of this tier."""
        return self._objects

    points = property(fget=_get_points,
                doc='The list of points of this tier.')

    def get_point_at_time(self, time):
        '''Get the point at time.'''
        return self._get_object_by_start_time(time)

    def get_points_between_timepoints(self, start, end, left_inclusive=False, right_inclusive=False):
        '''Get points between start and end.

        If left_overlap or right_overlap is False points overlapping
        with start or end are excluded.
        '''
        return self._get_objects_between_timepoints(start, end, 
            left_inclusive, right_inclusive)

    def get_points_with_regex(self, regex=r'[^\s]+', n=0):
        '''Get points with text matching the regex pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned.
        '''
        return self._get_objects_with_matching_text(regex, n, regex=True)

    def get_points_with_text(self, text, n=0):
        '''Get points with text matching the pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned.
        '''
        return self._get_objects_with_text(text, n, regex=False)


class AnnotationObject(object):

    def __init__(self, start_time, end_time, text=''):
        '''Initialise the AnnotationObject.'''
        super(AnnotationObject, self).__init__()
        if start_time > end_time:
            raise ValueError('Start time after end time.')
        self._start_time = Time(start_time)
        self._end_time = Time(end_time)
        self.text = text.strip()

    def _get_start_time(self):
        return self._start_time

    def _set_start_time(self, start_time):
        if start_time > self.end_time:
            raise ValueError('Start time after end time.')
        self._start_time = Time(start_time)

    start_time = property(fget=_get_start_time, fset=_set_start_time,
        doc='The start time.')

    def _get_end_time(self):
        return self._end_time

    def _set_end_time(self, end_time):
        if end_time < self.start_time:
            raise ValueError('End time before start time.')
        self._end_time = Time(end_time)

    end_time = property(fget=_get_end_time, fset=_set_end_time,
        doc='The end time.')

    def duration(self):
        """Get duration of this interval."""
        return self.end_time - self.start_time

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.start_time == other.start_time
                and self.end_time == other.end_time
                and self.text == other.text)

    def __repr__(self):
        return u'AnnotationObject({0}, {1}, "{2}")'.format(self.start_time,
            self.end_time, self.text)


class Interval(AnnotationObject):
    '''An interval of two points of time with a text label.'''

    def __init__(self, start_time, end_time, text=''):
        '''Initialise this Interval.'''
        super(Interval, self).__init__(start_time, end_time, text)

    def __repr__(self):
        return u'Interval({0}, {1}, "{2}")'.format(self.start_time, self.end_time, self.text)


class Point(AnnotationObject):
    '''A point of time with a text label.

    Internally an AnnotationObject where start time equals end time.
    '''

    def __init__(self, time, text=''):
        '''Initialise this Point.'''
        super(Point, self).__init__(time, time, text)

    def _get_time(self):
        '''Return time, i.e., start_time.'''
        return self._start_time

    def _set_time(self, time):
        '''Set time, i.e., start time and end time.'''
        self._start_time = self._end_time = Time(time)

    time = start_time = end_time = property(fget=_get_time, fset=_set_time,
        doc='The point of time.')

    def __repr__(self):
        return u'Point({0}, "{1}")'.format(self.time, self.text)


class Time(float):
    '''A representation of point in time with a predefined precision.'''

    _precision = 0.0001

    def __eq__(self, other):
        return math.fabs(self - other) < self._precision

    def __ne__(self, other):
        return math.fabs(self - other) > self._precision

    def __gt__(self, other):
        return self != other and self - other > 0

    def __lt__(self, other):
        return self != other and self - other < 0

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other


##  Functions for reading TextGrid files
##----------------------------------------------------------------------------


def read_textgrid(filename, encoding='utf-8'):
    '''Read a Praat TextGrid file and returns a TextGrid object.'''
    with codecs.open(filename, 'r', encoding) as f:
        # Read whole file into memory ignoring empty lines and lines consisting
        # solely of a single pair of double quotes.
        stg = filter(lambda s: s not in ['', '"'],
                     map(lambda s: s.strip(), f.readlines()))
    if stg[0] != 'File type = "ooTextFile"':
        raise Exception(filename)
    if stg[1] != 'Object class = "TextGrid"':
        raise Exception(filename)
    # Determine the TextGrid format.
    if stg[2].startswith('xmin'):
        return read_long_textgrid(filename, stg)
    else:
        return read_short_textgrid(filename, stg)


def read_short_textgrid(filename, stg):
    '''Read a Praat short TextGrid file and return a TextGrid object.'''

    def read_interval_tier(stg_extract):
        '''Read and return an IntervalTier from a short TextGrid.'''
        name = stg_extract[1].strip('"')  # name w/o quotes
        start_time = Time(stg_extract[2])
        end_time = Time(stg_extract[3])
        it = IntervalTier(start_time, end_time, name)
        i = 5
        while i < len(stg_extract):
            it.add_interval(Interval(Time(stg_extract[i]),  # left bound
                Time(stg_extract[i + 1]),                     # right bound
                stg_extract[i + 2].strip('"')))               # text w/o quotes
            i += 3
        return it

    def read_point_tier(stg_extract):
        '''Read and return a PointTier (called TextTier) from a short TextGrid.'''
        name = stg_extract[1].strip('"')  # name w/o quotes
        start_time = stg_extract[2]
        end_time = stg_extract[3]
        pt = PointTier(start_time, end_time, name)
        i = 5
        while i < len(stg_extract):
            pt.add_point(Point(stg_extract[i],  # time
                stg_extract[i + 1].strip('"')))   # text w/o quotes
            i += 2
        return pt

    tg = TextGrid(filename)
    read_start_time = stg[2]
    read_end_time = stg[3]
    if stg[4] != '<exists>':
        raise Exception(filename)
    read_no_of_tiers = stg[5]
    index = 6
    while index < len(stg):
        num_obj = int(stg[index + 4])
        if stg[index] == '"IntervalTier"':
            tg.add_tier(read_interval_tier(stg[index:index + 5 + num_obj * 3]))
            index += 5 + (num_obj * 3)
        elif stg[index] == '"TextTier"':
            tg.add_tier(read_point_tier(stg[index:index + 5 + num_obj * 2]))
            index += 5 + (num_obj * 2)
        else:
            raise Exception('Unknown tier type: {0}'.format(stg[index]))
    return tg


def read_long_textgrid(filename, stg):
    '''Read a Praat long TextGrid file and return a TextGrid object.'''

    def get_attr_val(x):
        """Extract the attribute value from a long TextGrid line."""
        return x.split(' = ')[1]

    def read_interval_tier(stg_extract):
        '''Read and return an IntervalTier from a long TextGrid.'''
        name = get_attr_val(stg_extract[2])[1:-1]  # name w/o quotes
        start_time = get_attr_val(stg_extract[3])
        end_time = get_attr_val(stg_extract[4])
        it = IntervalTier(start_time, end_time, name)
        i = 7
        while i < len(stg_extract):
            it.add_interval(Interval(get_attr_val(stg_extract[i]),  # left bound
                get_attr_val(stg_extract[i + 1]),                     # right bound
                get_attr_val(stg_extract[i + 2])[1:-1]))              # text w/o quotes
            i += 4
        return it

    def read_point_tier(stg_extract):
        '''Read and return a PointTier (called TextTier) from a long TextGrid.'''
        name = get_attr_val(stg_extract[2])[1:-1]  # name w/o quotes
        start_time = get_attr_val(stg_extract[3])
        end_time = get_attr_val(stg_extract[4])
        pt = PointTier(start_time, end_time, name)
        i = 7
        while i < len(stg_extract):
            pt.add_point(Point(get_attr_val(stg_extract[i]),  # time
                get_attr_val(stg_extract[i + 1])[1:-1]))      # text w/o quotes
            i += 3
        return pt

    tg = TextGrid(filename)
    read_start_time = get_attr_val(stg[2])
    read_end_time = get_attr_val(stg[3])
    if stg[4].split()[1] != '<exists>':
        raise Exception(filename)
    read_no_of_tiers = get_attr_val(stg[5])
    index = 7
    while index < len(stg):
        num_obj = int(get_attr_val(stg[index + 5]))
        if get_attr_val(stg[index + 1]) == '"IntervalTier"':
            tg.add_tier(read_interval_tier(stg[index:index + 6 + num_obj * 4]))
            index += 6 + (num_obj * 4)
        elif get_attr_val(stg[index + 1]) == '"TextTier"':
            tg.add_tier(read_point_tier(stg[index:index + 6 + num_obj * 3]))
            index += 6 + (num_obj * 3)
        else:
            raise Exception('Unknown tier type: {0}'.format(stg[index]))
    return tg


##  Functions for writing TextGrid files
##----------------------------------------------------------------------------

def correct_end_times(textgrid):
    """Correct the end times of all Tiers of a Textgrid object.

    Modifies the end times of all tiers to textgrid.end_time and (for
    IntervalTiers) adds the final empty intervals if necessary.
    """
    textgrid_copy = copy.deepcopy(textgrid)
    for tier in textgrid_copy:
        if isinstance(tier, IntervalTier) and tier.end_time < textgrid_copy.end_time:
            # For interval tiers insert the final empty interval
            # if necessary.
            empty_interval = Interval(tier.end_time, textgrid_copy.end_time, '')
            tier._add_object(empty_interval, Interval)
        tier.end_time = textgrid_copy.end_time
    return textgrid_copy


def export_to_short_textgrid(textgrid):
    '''Convert a TextGrid object into a string of Praat short TextGrid format.'''
    result = ['File type = "ooTextFile"',
               'Object class = "TextGrid"',
               '',
               textgrid.start_time,
               textgrid.end_time,
               '<exists>',
               len(textgrid)]
    textgrid_corrected = correct_end_times(textgrid)
    for tier in textgrid_corrected:
        result += ['"' + tier.__class__.__name__ + '"',
                   '"' + tier.name + '"',
                   tier.start_time, tier.end_time, len(tier)]
        if isinstance(tier, IntervalTier):
            result += [u'{0}\n{1}\n"{2}"'.format(obj.start_time, obj.end_time, obj.text)
                       for obj in tier]
        elif isinstance(tier, PointTier):
            result += [u'{0}\n"{1}"'.format(obj.time, obj.text)
                       for obj in tier]
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(map(unicode, result))


def export_to_long_textgrid(textgrid):
    """Convert a TextGrid object into a string of Praat long TextGrid format."""
    result = ['File type = "ooTextFile"',
              'Object class = "TextGrid"',
              '',
              'xmin = ' + unicode(textgrid.start_time),
              'xmax = ' + unicode(textgrid.end_time),
              'tiers? <exists>',
              'size = ' + unicode(len(textgrid)),
              'item []:']
    textgrid_corrected = correct_end_times(textgrid)
    for i, tier in enumerate(textgrid_corrected):
        result += ['\titem [{0}]:'.format(i + 1),
                   '\t\tclass = "{0}"'.format(tier.__class__.__name__),
                   '\t\tname = "{0}"'.format(tier.name),
                   '\t\txmin = ' + unicode(tier.start_time),
                   '\t\txmax = ' + unicode(tier.end_time),
                   '\t\tintervals: size = ' + unicode(len(tier))]
        if isinstance(tier, IntervalTier):
            for j, obj in enumerate(tier):
                result += ['\t\tintervals [{0}]:'.format(j + 1),
                           '\t\t\txmin = ' + unicode(obj.start_time),
                           '\t\t\txmax = ' + unicode(obj.end_time),
                           '\t\t\ttext = "' + obj.text + '"']
        elif isinstance(tier, PointTier):
            for j, obj in enumerate(tier):
                result += ['\t\tpoints [{0}]:'.format(j + 1),
                           '\t\t\tnumber = ' + obj.time,
                           '\t\t\tmark = "' + obj.text + '"']
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(map(unicode, result))


def export_to_elan(textgrid, encoding='utf-8', include_empty_annotations=False,
                   include_point_tiers=True, point_tier_annotation_duration=0.04):
    """Convert a TextGrid object into a string of ELAN eaf format."""

    time_slots = collections.OrderedDict()

    def get_time_slot_id(time, ts_dict=time_slots):
        """Returns (and possibly creates) the time slot id of time."""
        time_in_ms = int(time * 1000)
        if time_in_ms not in ts_dict:
            ts_id = 'ts' + str(len(ts_dict) + 1)
            ts_dict[time_in_ms] = ts_id
        return ts_dict[time_in_ms]

    # Create ELAN header
    head = [
        u'<?xml version="1.0" encoding="{0}"?>'.format(encoding.upper()),
        u'<ANNOTATION_DOCUMENT AUTHOR="TextGridTools" DATE="{0}" FORMAT="2.7" VERSION="2.7" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv2.7.xsd">'.format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')),
        u'<HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">',
        u'\t<PROPERTY NAME="lastUsedAnnotationId">0</PROPERTY>',
        u'</HEADER>']
    # Create annotations
    annotation_id_count = 1
    annotations = []
    for tier in textgrid:
        annotations.append(u'<TIER DEFAULT_LOCALE="en" LINGUISTIC_TYPE_REF="default-lt" TIER_ID="{0}">'.format(tier.name))
        if isinstance(tier, IntervalTier):
            for interval in tier.intervals:
                if not include_empty_annotations and interval.text == '':
                    continue
                annotations += [
                    u'<ANNOTATION>',
                    u'\t<ALIGNABLE_ANNOTATION ANNOTATION_ID="{0}" TIME_SLOT_REF1="{1}" TIME_SLOT_REF2="{2}">'.format('a' + str(annotation_id_count), get_time_slot_id(interval.start_time), get_time_slot_id(interval.end_time)),
                    u'\t\t<ANNOTATION_VALUE>{0}</ANNOTATION_VALUE>'.format(interval.text),
                    u'\t</ALIGNABLE_ANNOTATION>',
                    u'</ANNOTATION>']
                annotation_id_count += 1
        elif isinstance(tier, PointTier):
            if include_point_tiers:
                for point in tier.points:
                    annotations += [
                        u'<ANNOTATION>',
                        u'\t<ALIGNABLE_ANNOTATION ANNOTATION_ID="{0}" TIME_SLOT_REF1="{1}" TIME_SLOT_REF2="{2}">'.format('a' + str(annotation_id_count), get_time_slot_id(point.time), get_time_slot_id(point.time + point_tier_annotation_duration)),
                        u'\t\t<ANNOTATION_VALUE>{0}</ANNOTATION_VALUE>'.format(point.text),
                        u'\t</ALIGNABLE_ANNOTATION>',
                        u'</ANNOTATION>']
                    annotation_id_count += 1
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
        annotations.append(u'</TIER>')
    # Create time stamp information
    time_info = [u'<TIME_ORDER>']
    for time_value, time_slot_id in time_slots.items():
        time_info.append(u'\t<TIME_SLOT TIME_SLOT_ID="{0}" TIME_VALUE="{1}"/>'.format(time_slot_id, str(time_value)))
    time_info.append(u'</TIME_ORDER>')
    # Create ELAN footer
    foot = [u'<LINGUISTIC_TYPE GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>',
            u'<LOCALE COUNTRY_CODE="US" LANGUAGE_CODE="en"/>',
            u'</ANNOTATION_DOCUMENT>']
    eaf = head + time_info + annotations + foot
    return '\n'.join(map(unicode, eaf))


def export_to_table(textgrid, separator=','):
    """Convert a TextGrid object into a table with fields delimited
    with the specified separator (comma by default)."""
    result = [separator.join(['tier_name', 'tier_type', 'start_time', 'end_time', 'text'])]

    for tier in textgrid:
        if isinstance(tier, IntervalTier):
            for obj in tier:
                if obj.text:
                    result.append(separator.join([unicode(tier.name), unicode(tier.__class__.__name__),
                                                  unicode(obj.start_time), unicode(obj.end_time), obj.text]))
        elif isinstance(tier, PointTier):
            for obj in tier:
                result.append(separator.join([unicode(tier.name), unicode(tier.__class__.__name__),
                                              unicode(obj.time), unicode(obj.time), obj.text]))
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(map(unicode, result))

# Listing of currently supported export formats.
_EXPORT_FORMATS = {
    # Export to Praat TextGrid in short format
    'short': export_to_short_textgrid,
    # Export to Praat TextGrid in long (i.e., standard) format
    'long': export_to_long_textgrid,
    # Export to ELAN .eaf format
    'eaf': export_to_elan,
    # Export to a table
    'table': export_to_table
}


def write_to_file(textgrid, filename, format='short', encoding='utf-8', **kwargs):
    """Write a TextGrid object to a file in the specified format."""
    with codecs.open(filename, 'w', encoding) as f:
        if format in _EXPORT_FORMATS:
            f.write(_EXPORT_FORMATS[format](textgrid, **kwargs))
        else:
            Exception('Unknown output format: {0}'.format(format))


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

        tier_shifted.add_interval(Interval(interval_start_shifted,
                                           interval_end_shifted,
                                           interval.text))
    return tier_shifted

def get_overlapping_intervals(tier1, tier2, regex=r'[^\s]+', overlap_label='overlap'):
    """Return a list of overlaps between intervals of tier1 and
    tier2 matching the regular expression. All nonempty intervals
    are included in the search by default.

    """
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
            overlaps.append(Interval(lo, hi, overlap_label))
        if intervals1[i].end_time < intervals2[j].end_time:
            i += 1
        else:
            j += 1
    return overlaps


def concatenate_textgrids(textgrids, ignore_nonmatching_tiers=False):
    """Concatenate Tiers with matching names. TextGrids are concatenated
    in the order they are specified. If ignore_nonmatching_tiers is False
    (the default), an exception is raised if the number and the names of
     tiers differ between TextGrids."""

    tier_names_intersection = reduce(lambda x, y: x.intersection(y),
                                     map(lambda x: set(x.get_tier_names()),
                                         textgrids))
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
                tiers[tier.name].add_intervals(intervals)
        tot_duration += textgrid.end_time

    # Create a new TextGrid and add the concatenated tiers
    textgrid_concatenated = TextGrid()
    # Add tiers in the order they're found in the first TextGrid.
    textgrid_concatenated.add_tiers([tiers[x] for x in tier_names_intersection])
    return textgrid_concatenated


def merge_textgrids(textgrids, ignore_duplicates=True):
    """Return a TextGrid object with tiers in all textgrids. If ignore_duplicates
    is False, tiers with equal names are renamed by adding a path of the textgrid or
    a unique number incremented with each occurrence."""

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
