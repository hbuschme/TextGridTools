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
import copy
import math
import re

__all__ = [
    'TextGrid', 'IntervalTier', 'Interval', 'PointTier', 'Point',
    'read_textgrid', 'read_short_textgrid', 'read_long_textgrid', 'write_short_textgrid'
]


class TextGrid(object):
    '''A TextGrid.'''
    
    def __init__(self, filename=''):
        super(TextGrid, self).__init__()
        self.tiers = []
        self.filename = filename
    
    def add_tiers(self, tiers):
        """Add a list of tiers."""
        for tier in tiers:
            self.add_tier(tier)
        
    def add_tier(self, tier):
        """Add a tier."""
        self.tiers.append(tier)

    def insert_tier(self, tier, position):
        """Insert a tier at the specified position."""
        self.tiers.insert(position, tier)
        
    def get_tier_names(self):
        """Get names of all tiers."""
        return map(lambda tier: tier.name, self.tiers)
        
    def has_tier(self, name):
        """Check whether TextGrid has a tier of the specified name."""
        return name in self.get_tier_names()
    
    def get_tier_by_name(self, name):
        """Get tier of specified name name."""
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise ValueError('Textgrid ' + self. filename +
                    ' does not have a tier called "' + name + '".')
        
    def _earliest_start_time(self):
        '''Return the earliest start time among all tiers.'''
        return min(map(lambda t: t.start_time, self.tiers))
    start_time = property(fget=_earliest_start_time,
                          doc='TextGrid start time.')
        
    def _latest_end_time(self):
        '''Return the latest end time among all tiers.'''
        return max(map(lambda t: t.end_time, self.tiers))
    end_time = property(fget=_latest_end_time,
                        doc='TextGrid end time.')

    def write_to_file(self, filename, encoding='utf-8'):
        '''Writes textgrid to a Praat short TextGrid file.'''
        f = codecs.open(filename, 'w', encoding)
        f.write(unicode(self))
        f.close()

    def __len__(self):
        '''Return the number of tiers.'''
        return len(self.tiers)

    def _update_end_times(self):
        """Modify the end times of Intervals to self.end_time and (for interval tiers)
        add the final empty intervals if necessary."""
        for tier in self.tiers:
            if isinstance(tier, IntervalTier) and tier.end_time < self.end_time:
                # For interval tiers insert the final empty interval
                # if necessary.
                empty_interval = Interval(tier.end_time, self.end_time, '')
                tier._add_object(empty_interval, Interval)
            tier.end_time = self.end_time
    
    def __str__(self):
        '''Return string representation of this TextGrid (in short format).'''
        header =  [
            'File type = "ooTextFile"',
            'Object class = "TextGrid"',
            '',
            self.start_time,
            self.end_time,
            '<exists>',
            len(self.tiers)
        ]
        # Make a copy of the textgrid, update tiers' end times and
        # (for interval tiers) insert the final empty interval if
        # necessary.
        textgrid_copy = copy.deepcopy(self)
        textgrid_copy._update_end_times()
        return '\n'.join(map(unicode, header + textgrid_copy.tiers))
    

class Tier(object):
    "A general tier."
    
    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(Tier, self).__init__()
        self._objects = []
        self.start_time = Time(start_time)
        self.end_time = Time(end_time)
        self.name = name
        if objects is not None and objects != []:
            self._add_objects(objects, type=type(objects[0]))
    
    def _add_objects(self, objects, type=None):
        """Add a list of intervals or a list of points to this tier."""
        for obj in objects:
            self._add_object(obj, type)
    
    def _add_object(self, object, type):
        """Add an interval or point to this tier. For intervals tiers
        insert an empty interval if necessary."""
        if isinstance(object, type):
            if isinstance(object, Interval):
                if self.end_time < object.start_time:
                    # Add an empty interval (if necessary).
                    empty_interval = Interval(self.end_time, object.start_time, '')
                    self._objects.append(empty_interval)
                self.end_time = object.end_time
            elif isinstance(object, Point):
                self.end_time = object.time
            self._objects.append(object)
        else:
            raise Exception('Could not add object ' + repr(object) + ' to this '
                + self.__class__.__name__ + '.')
    
    def __len__(self):
        """Return number of intervals/points in this tier."""
        return len(self._objects)

    def __repr__(self):
        return '%s(start_time=%s, end_time=%s, name="%s", objects=%s)' % (self.__class__.__name__,
                                                                          self.start_time,
                                                                          self.end_time,
                                                                          self.name,
                                                                          self._objects)

    def __str__(self):
        """Return string representation of this tier (in short format)."""
        w = lambda x: '"' + unicode(x) + '"'
        tier_header = [w(self.__class__.__name__), w(self.name),
                    self.start_time, self.end_time, len(self)]
        return '\n'.join(map(unicode, tier_header + self._objects))
    

class IntervalTier(Tier):
    '''An IntervalTier.'''
    
    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(IntervalTier, self).__init__(Time(start_time), Time(end_time), name, objects)
    
    def add_intervals(self, intervals):
        """Add a list of intervals to this tier."""
        self._add_objects(intervals, Interval)
        
    def add_interval(self, interval):
        """Add an interval to this tier. Insert an empty interval if
        necessary."""
        self._add_object(interval, Interval)
    
    def get_intervals(self):
        """Get all intervals of this tier. Insert empty intervals if
        necessary."""
        return self._objects
    intervals = property(fget=get_intervals,
                doc='The list of intervals of this tier.')

    def get_intervals_with_text(self, text, n=1):
        """Get the n first intervals with the specified text."""
        return [x for x in self.intervals if x.text == text][:n]
        
    
    def get_interval_by_start_time(self, start_time):
        """Get interval with the specified left bound (or None)."""
        index = bisect.bisect_left(map(lambda x: x.start_time,
                    self._objects), start_time)
        if (index != len(self._objects) and 
                    self._objects[index].start_time == start_time):
            return self._objects[index]
        else:
            return None
    
    def get_interval_by_end_time(self, end_time):
        """Get interval with the specified right bound (or None)."""
        index = bisect.bisect_left(map(lambda x: x.end_time,
                    self._objects), end_time)
        if (index != len(self._objects) 
                    and self._objects[index].end_time == end_time):
            return self._objects[index]
        else:
            return None

    def get_interval_at_time(self, time):
        """Get interval at the specified time (or None)."""
        index = bisect.bisect_right(map(lambda x: x.end_time,
                                        self._objects), time)
        
        if (index != len(self._objects) and time >= self._objects[index].start_time):
            return self._objects[index]
        else:
            return None

    def get_intervals_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        """Get intervals between start and end. If left_overlap or
        right_overlap is False (the default) intervals overlapping
        with start or end are excluded."""

        if left_overlap:
            index_lo = bisect.bisect_right(map(lambda x: x.end_time,
                                               self._objects), start)
        else:
            index_lo = bisect.bisect_left(map(lambda x: x.start_time,
                                              self._objects), start)

        if right_overlap:
            index_hi = bisect.bisect_left(map(lambda x: x.start_time,
                                              self._objects), end)
        else:
            index_hi = bisect.bisect_right(map(lambda x: x.end_time,
                                               self._objects), end)
        
        return self._objects[index_lo:index_hi]

    def get_overlapping_intervals(self, other, regex=r'[^\s]+', overlap_label='overlap'):
        """Return a list of overlaps between intervals of self and
        other matching the regular expression. All nonempty intervals
        are included in the search by default."""

        if not isinstance(other, IntervalTier):
            raise TypeError('Argument is not an IntervalTier')
        intervals1 = self.intervals
        intervals2 = other.intervals
        overlaps = []
        i, j = 0, 0
        while i < len(self) and j < len(other):
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
                
    
    def add_empty_intervals(self, end_time=None):
        """Return a copy of this tier with empty intervals inserted."""
        
        # Make end_time default to self.end_time
        end_time = self.end_time if end_time is None else Time(end_time)
        result = IntervalTier(self.start_time, end_time, self.name)
        last_end_time = self.start_time
        additional_intervals = 0 
        for obj in self._objects:
            if obj.start_time > last_end_time:
                # insert empty interval
                empty_interval = Interval(last_end_time, obj.start_time)
                result.add_interval(empty_interval)
            result.add_interval(obj)
            last_end_time = obj.end_time
        if not times_equal_with_precision(end_time, last_end_time) and end_time > last_end_time:
            # insert empty interval at the end (if necessary)
            empty_interval = Interval(last_end_time, end_time)
            result.add_interval(empty_interval)
        return result

    

class PointTier(Tier):
    '''A PointTier (also "TextTier").'''
    
    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(PointTier, self).__init__(Time(start_time), Time(end_time), name, objects)
    
    def add_points(self, points):
        """Adds a list of points to this tier."""
        self._add_objects(points, Point)
    
    def add_point(self, point):
        """Add a point to this tier."""
        self._add_object(point, Point)
        
    def get_points(self):
        """Get all points of this tier."""
        return self._objects
    points = property(fget=get_points,
                doc='The list of points of this tier.')
    
    def get_point(self, time):
        """Get point at specified point of time."""
        index = bisect_left(map(lambda x: x.time, self._objects), time)
        if index != len(self._objects) and self._objects[index].time == time:
            return self._objects[index]
        else:
            return None
    

class Interval(object):
    '''An interval of two points of time with an attached text label.'''
    
    def __init__(self, start_time, end_time, text=''):
        super(Interval, self).__init__()
        self.start_time = Time(start_time)
        self.end_time = Time(end_time)
        self.text = text.strip()
    
    def duration(self):
        """Get duration of this interval."""
        return self.end_time - self.start_time
    
    def __eq__(self, other):
        return (self.start_time == other.start_time
                    and self.end_time == other.end_time
                    and self.text == other.text)
    
    def __repr__(self):
        return u'Interval({0}, {1}, "{2}")'.format(self.start_time, self.end_time, self.text)
    
    def __str__(self):
        return u'{0}\n{1}\n"{2}"'.format(self.start_time, self.end_time, self.text)
    

class Point(object):
    '''A point of time with an attached text label.'''
    
    def __init__(self, time, text):
        super(Point, self).__init__()
        self.time = Time(time)
        self.text = text.strip()
    
    def __eq__(self, other):
        return self.time == other.time and self.text == other.text
    
    def __repr__(self):
        return u'Point({0}, "{1}")'.format(self.time, self.text)
    
    def __str__(self):
        return u'{0}\n"{1}"'.format(self.time, self.text)

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



                 
##  Functions for reading TextGrid files in the 'short' format.
##----------------------------------------------------------------------------

def read_textgrid(filename, encoding='utf-8'):
    '''Reads a Praat TextGrid file and returns a TextGrid object.'''
    f = codecs.open(filename, 'r', encoding)
    # Read whole file into memory ignoring empty lines and lines consisting 
    # solely of a single pair of double quotes.
    stg = filter(lambda s: s not in ['','"'], map(lambda s: s.strip(), f.readlines()))
    f.close()
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
    '''Reads a Praat short TextGrid file and returns a TextGrid object.'''

    def read_interval_tier(stg_extract):
        '''Reads and returns an IntervalTier from a short TextGrid.'''
        name = stg_extract[1].strip('"') # name w/o quotes
        start_time = Time(stg_extract[2])
        end_time = Time(stg_extract[3])
        it = IntervalTier(start_time, end_time, name)
        i = 5
        while i < len(stg_extract):
            it.add_interval(Interval(Time(stg_extract[i]), # left bound
                Time(stg_extract[i+1]),                    # right bound 
                stg_extract[i+2].strip('"')))              # text w/o quotes
            i += 3
        return it

    def read_point_tier(stg_extract):
        '''Reads and returns a PointTier (called TextTier) from a short TextGrid.'''    
        name = stg_extract[1].strip('"') # name w/o quotes
        start_time = stg_extract[2]
        end_time = stg_extract[3]
        pt = PointTier(start_time, end_time, name)
        i = 5
        while i < len(stg_extract):
            pt.add_point(Point(stg_extract[i], # time
                stg_extract[i+1].strip('"')))  # text w/o quotes
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
        num_obj  = int(stg[index+4])
        if stg[index] == '"IntervalTier"':
            tg.add_tier(read_interval_tier(stg[index:index+5+num_obj*3]))
            index += 5 + (num_obj * 3)
        elif stg[index] == '"TextTier"':
            tg.add_tier(read_point_tier(stg[index:index+5+num_obj*2]))
            index += 5 + (num_obj * 2)
        else:
            raise Exception('Unknown tier type: {0}'.format(stg[index]))
    return tg


def read_long_textgrid(filename, stg):
    '''Reads a Praat long TextGrid file and returns a TextGrid object.'''

    def get_attr_val(x):
        """Extracts the attribute value from a long TextGrid line."""
        return x.split(' = ')[1]

    def read_interval_tier(stg_extract):
        '''Reads and returns an IntervalTier from a long TextGrid.'''
        name = get_attr_val(stg_extract[2])[1:-1] # name w/o quotes
        start_time = get_attr_val(stg_extract[3])
        end_time = get_attr_val(stg_extract[4])
        it = IntervalTier(start_time, end_time, name)
        i = 7
        while i < len(stg_extract):
            it.add_interval(Interval(get_attr_val(stg_extract[i]), # left bound
                get_attr_val(stg_extract[i+1]),                    # right bound 
                get_attr_val(stg_extract[i+2])[1:-1]))             # text w/o quotes
            i += 4
        return it

    def read_point_tier(stg_extract):
        '''Reads and returns a PointTier (called TextTier) from a long TextGrid.'''    
        name = get_attr_val(stg_extract[2])[1:-1] # name w/o quotes
        start_time = get_attr_val(stg_extract[3])
        end_time = get_attr_val(stg_extract[4])
        pt = PointTier(start_time, end_time, name)
        i = 7
        while i < len(stg_extract):
            pt.add_point(Point(get_attr_val(stg_extract[i]), # time
                get_attr_val(stg_extract[i+1])[1:-1]))              # text w/o quotes
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
        num_obj  = int(get_attr_val(stg[index+5]))
        if get_attr_val(stg[index+1]) == '"IntervalTier"':
            tg.add_tier(read_interval_tier(stg[index:index+6+num_obj*4]))
            index += 6 + (num_obj * 4)
        elif get_attr_val(stg[index+1]) == '"TextTier"':
            tg.add_tier(read_point_tier(stg[index:index+6+num_obj*3]))
            index += 6 + (num_obj * 3)
        else:
            raise Exception('Unknown tier type: {0}'.format(stg[index]))
    return tg


def write_short_textgrid(textgrid, filename, encoding):
    '''Writes a TextGrid object to a Praat short TextGrid file.'''
    textgrid.write_to_file(filename, encoding)


