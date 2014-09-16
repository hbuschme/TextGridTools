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

import bisect
import warnings
import copy
import math
import operator
import re


__all__ = [
    'TextGrid',
    'Tier', 'IntervalTier', 'PointTier',
    'Annotation', 'Interval', 'Point',
    'Time'
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
        '''Add a tier.'''
        self._tiers.append(tier)

    def add_tiers(self, tiers):
        '''Add a list of tiers.'''
        for tier in tiers:
            self.add_tier(tier)

    def insert_tier(self, tier, position):
        '''Insert a tier at the specified position.'''
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
            self.add_annotations(objects)

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

    def add_annotation(self, obj):
        '''Adds an annotation object to this tier.

        The annotation object is inserted at the correct position within the
        tier. If the space is already (partially) occupied by a different
        annotation object, a ValueError is raised.
        '''
        if ((len(self._objects) > 0 and obj.start_time >= self._objects[-1].end_time) 
                or len(self._objects) == 0): # can we simply append obj?
            self._objects.append(obj)
        else: # no, we need to insert it
            overlapping_objects = self.get_annotations_between_timepoints(
                obj.start_time, obj.end_time, 
                left_overlap=True, right_overlap=True)
            if overlapping_objects == []:
                start_timepoints = [interval.start_time for interval in self._objects]
                position = bisect.bisect_left(start_timepoints, obj.start_time)
                self._objects.insert(position, obj)
            else:
                raise ValueError(
                    'Could not add object {0} to this tier: Overlap.'.format(
                        repr(obj)))

    def add_annotations(self, objects):
        '''Add a sequence of annotation objects.'''
        for obj in objects:
            self.add_annotation(obj)

    def _get_annotations(self):
        '''Get all intervals of this tier.'''
        return self._objects

    annotations = property(fget=_get_annotations,
                doc='The list of annotations of this tier.')

    def _get_annotation_index_by_start_time(self, time):
        '''Get annotation index of the object that starts at time.'''
        idx = bisect.bisect_left([obj.start_time for obj in self], time)
        if (idx < len(self) and self._objects[idx].start_time == time):
            return idx
        else:
            return None

    def _get_annotation_index_by_end_time(self, time):
        '''Get the annotation index of the object that ends at time.'''
        idx = bisect.bisect_left([obj.end_time for obj in self], time)
        if (idx < len(self) and self._objects[idx].end_time == time):
            return idx
        else:
            return None

    def _get_annotation_indices_by_time(self, time):
        '''Get annotation indices at the specified time.'''
        idx = bisect.bisect_left([obj.end_time for obj in self], time)
        if (idx < len(self._objects) and 
            time >= self._objects[idx].start_time):
            if (len(self._objects) > idx+1
                and self._objects[idx+1].start_time == time):
                return [idx, idx+1]
            else:
                return [idx]
        else:
            return []

    def _get_annotation_index_range_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        '''Get annotation index range for objects between start and end.

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
        return (index_lo, index_hi)

    def get_annotation_by_start_time(self, time):
        '''Get the annotation object that starts at time.'''
        idx = self._get_annotation_index_by_start_time(time)
        return idx if idx is None else self._objects[idx]

    def get_annotation_by_end_time(self, time):
        '''Get the annotation object that ends at time.'''
        idx = self._get_annotation_index_by_end_time(time)
        return idx if idx is None else self._objects[idx]

    def get_annotations_by_time(self, time):
        '''Get annotation objects at the specified time.'''
        indices = self._get_annotation_indices_by_time(time)
        return [self._objects[idx] for idx in indices]

    def get_annotations_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        '''Get annotation objects between start and end.

        If left_overlap or right_overlap is False annotation objects
        overlapping with start or end are excluded.
        '''
        idx_lo, idx_hi = self._get_annotation_index_range_between_timepoints(start, end, left_overlap, right_overlap)
        return self._objects[idx_lo:idx_hi]

    def get_nearest_annotation(self, time, pattern=r'.*', boundary='both',
                               direction='both', exclude_overlapped=False):
        '''Get a list of the annotation object(s) nearest to time.

        Boundary specifies whether the distance to an annotation object
        is calculated based on its start time ('start'), end time
        ('end') or both ('both'). Direction specifies whether it is
        looked to the left hand side of time ('left'), to the right
        hand side of time ('right') or to both sides ('both').
        Annotations overlapping with time can be excluded.

        Note: When time lies exactly on a boundary, this boundary is
        both to the left and to the right of time.
        '''
        # Filter for specified regular expression
        matching_objects = self.get_annotations_with_matching_text(
            pattern=pattern, regex=True)
        # Exclude overlapping intervals from search
        if exclude_overlapped:
            overlapping_objects = self.get_annotations_by_time(time)
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
        # Compute corresponding annotation objects for all candidates
        # that have the minimum distance to the reference point and
        # collect the unique ones
        if len(candidates) > 0:
            min_distance = min(candidates, key=operator.itemgetter(1))[1]
            results = set()
            for candidate in candidates:
                if candidate[1] == min_distance:
                    if candidate[2] == 'start':
                        results.add(self.get_annotation_by_start_time(candidate[0]))
                    elif candidate[2] == 'end':
                        results.add(self.get_annotation_by_end_time(candidate[0]))
            return sorted(list(results), key=lambda x: x.start_time)
        else:
            return list()

    def get_annotations_with_text(self, pattern='', n=0, regex=False):
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

    def get_annotations_with_matching_text(self, pattern='', n=0, regex=False):
        '''Get annotation objects with text matching the pattern.

        If n > 0 the first n matches are returned, if n < 0, the last
        n matches are returned, if n = 0 all matches are returned. The 
        pattern is treated as a regular expression, if regex is True.

        Note: get_annotations_with_matching_text is deprecated. Use
        get_annotations_with_text instead.
        '''
        warnings.warn('get_annotations_with_matching_text is deprecated. '\
                      'Use get_annotations_with_text instead.',DeprecationWarning)
        return self.get_annotations_with_text(pattern, n, regex)

    def delete_annotation_by_start_time(self, time):
        '''Delete the annotation object that starts at time.'''
        idx = self._get_annotation_index_by_start_time(time)
        if idx is not None:
            del self._objects[idx]

    def delete_annotation_by_end_time(self, time):
        '''Delete the annotation object that ends at time.'''
        idx = self._get_annotation_index_by_end_time(time)
        if idx is not None:
            del self._objects[idx]

    def delete_annotations_by_time(self, time):
        '''Delete annotation objects at the specified time.'''
        indices = self._get_annotation_indices_by_time(time)
        for idx in reversed(indices): # Needs to be done in reverse order
            del self._objects[idx]

    def delete_annotations_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        '''Delete annotation objects between start and end.

        If left_overlap or right_overlap is False annotation objects
        overlapping with start or end are excluded.
        '''
        idx_lo, idx_hi = self._get_annotation_index_range_between_timepoints(start, end, left_overlap, right_overlap)
        r = range(idx_hi-1,idx_lo-1,-1)
        for idx in r: # Needs to be done in reverse order
            del self._objects[idx]

    def delete_annotations_with_text(self, pattern='', n=0, regex=False):
        '''Delete annotation objects with text matching the pattern.

        If n > 0 the first n matches are deleted, if n < 0, the last
        n matches are deleted, if n = 0 all matches are deleted. The 
        pattern is treated as a regular expression, if regex is True.
        '''
        # Inefficient implementation, but works
        annotations = self.get_annotations_with_text(pattern, n, regex)
        for annotation in annotations:
            self.delete_annotation_by_start_time(annotation.start_time)

    def delete_empty_annotations(self):
        '''Delete annotation object with empty or whitespace-only text.
        '''
        self.delete_annotations_with_text(pattern=r'^\s*$', regex=True)

    def tier_type(self):
        '''Return the type of the tier as a string.'''
        return self.__class__.__name__
       
    def __iter__(self):
        return iter(self._objects)

    def __getitem__(self, key):
        return self._objects[key]

    def __delitem__(self, key):
        del self._objects[key]

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
        self.add_annotation(interval)

    def add_intervals(self, intervals):
        '''Add a sequence of intervals to this tier.'''
        self.add_annotations    (intervals)

    def _get_intervals(self):
        '''Get all intervals of this tier.'''
        return self._objects

    intervals = property(fget=_get_intervals,
                doc='The list of intervals of this tier.')

    def get_copy_with_gaps_filled(self, start_time=None, end_time=None, empty_string=''):
        '''Returns a copy where gaps are filled with empty intervals.'''
        tier_copy = copy.deepcopy(self)
        if start_time is not None:
            tier_copy._specd_start_time = Time(start_time)
        if end_time is not None:
            tier_copy._specd_end_time = Time(end_time)
        # If no intervals exist, add one interval from start to end
        if len(self) == 0:
            empty = Interval(self.start_time, self.end_time, empty_string)
            tier_copy.add_annotation(empty)
        else:
            # If necessary, add empty interval at start of tier
            if self.intervals[0].start_time > tier_copy.start_time:
                empty = Interval(tier_copy.start_time, self.intervals[0].start_time, empty_string)
                tier_copy.add_annotation(empty)
            # If necessary, add empty interval at end of tier
            if self.intervals[-1].end_time < tier_copy.end_time:
                empty = Interval(self.intervals[-1].end_time, tier_copy.end_time, empty_string)
                tier_copy.add_annotation(empty)
            # Insert empty intervals in between non-meeting intervals
            for i in range(len(self) - 1):
                if self.intervals[i].end_time < self.intervals[i+1].start_time:
                    empty = Interval(self.intervals[i].end_time, self.intervals[i+1].start_time, empty_string)
                    tier_copy.add_annotation(empty)
        return tier_copy

    def get_copy_with_same_intervals_merged(self):
        '''Returns a copy of TIER in which consecutive intervals
        with identical labels are merged.'''

        res = IntervalTier(name=self.name)
        prev_intr = None

        for intr in self:
            if prev_intr is None:
                prev_intr = copy.copy(intr)
            elif prev_intr.text != intr.text or prev_intr.end_time != intr.start_time:
                res.add_interval(prev_intr)
                prev_intr = copy.copy(intr)
            else:
                prev_intr.end_time = intr.end_time
        else:
            if prev_intr is not None:
                res.add_interval(prev_intr)
        return res


class PointTier(Tier):
    '''A PointTier (also "TextTier").'''

    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(PointTier, self).__init__(Time(start_time), Time(end_time),
            name, objects)

    def add_point(self, point):
        '''Add a point to this tier.'''
        self.add_annotation(point)

    def add_points(self, points):
        '''Adds a list of points to this tier.'''
        self.add_annotations(points)

    def _get_points(self):
        '''Get all points of this tier.'''
        return self._objects

    points = property(fget=_get_points,
                doc='The list of points of this tier.')

    def tier_type(self):
        '''Return the type of the tier as a string. 

        As Praat's point tiers are for some reason called "TextTier" in the 
        TextGrid file format we simply return a string literal here.
        '''
        return 'TextTier'


class Annotation(object):

    def __init__(self, start_time, end_time, text=''):
        '''Initialise the Annotation.'''
        super(Annotation, self).__init__()
        self._start_time = Time(start_time)
        self._end_time = Time(end_time)
        if start_time > end_time:
            raise ValueError('Start time {0} after end time {1}.'.format(start_time, end_time))
        self.text = text.strip()

    def _get_start_time(self):
        return self._start_time

    def _set_start_time(self, start_time):
        if start_time > self.end_time:
            raise ValueError('Start time {0} after end time {1}.'.format(start_time, self.end_time))
        self._start_time = Time(start_time)

    start_time = property(fget=_get_start_time, fset=_set_start_time,
        doc='The start time.')

    def _get_end_time(self):
        return self._end_time

    def _set_end_time(self, end_time):
        if end_time < self.start_time:
            raise ValueError('Start time {0} after end time {1}.'.format(self.start_time, end_time))
        self._end_time = Time(end_time)

    end_time = property(fget=_get_end_time, fset=_set_end_time,
        doc='The end time.')

    def duration(self):
        '''Get duration of this annotation.'''
        return self.end_time - self.start_time

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.start_time == other.start_time
                and self.end_time == other.end_time
                and self.text == other.text)

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = object.__hash__

    def __repr__(self):
        return u'Annotation({0}, {1}, "{2}")'.format(self.start_time,
            self.end_time, self.text)


class Interval(Annotation):
    '''An interval of two points of time with a text label.'''

    def __init__(self, start_time, end_time, text=''):
        '''Initialise this Interval.'''
        super(Interval, self).__init__(start_time, end_time, text)

    def __repr__(self):
        return u'Interval({0}, {1}, "{2}")'.format(self.start_time, self.end_time, self.text)


class Point(Annotation):
    '''A point of time with a text label.

    Internally an Annotation where start time equals end time.
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
        return math.fabs(self - other) >= self._precision

    __hash__ = float.__hash__

    def __gt__(self, other):
        return self != other and self - other > 0

    def __lt__(self, other):
        return self != other and self - other < 0

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other
