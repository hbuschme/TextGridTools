#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2011 Hendrik Buschmeier
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

__all__ = [
    'TextGrid', 'IntervalTier', 'Interval', 'PointTier', 'Point',
    'read_short_textgrid', 'write_short_textgrid'
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
        
    def has_tier(self, name):
        """Check whether TextGrid has a tier of the specified name."""
        return name in map(lambda tier: tier.name, self.tiers)
        
    def get_tier_by_name(self, name):
        """Get tier of specified name name."""
        for tier in self.tiers:
            if tier.name == name:
                return tier
        raise ValueError('Textgrid ' + self. filename +
                    ' does not have a tier called "' + name + '".')
        
    def start_time(self):
        '''Return the earliest start time among all tiers.'''
        return min(map(lambda t: t.start_time, self.tiers))
        
    def end_time(self):
        '''Return the latest end time among all tiers.'''
        return max(map(lambda t: t.end_time, self.tiers))
    
    def write_to_file(self, filename):
        '''Writes textgrid to a Praat short TextGrid file.'''
        f = open(filename, 'w')
        f.write(str(self))
        f.close()
    
    def __str__(self):
        '''Return string representation of this TextGrid (in short format).'''
        header =  [
            'File type = "ooTextFile"',
            'Object class = "TextGrid"',
            '',
            self.start_time(),
            self.end_time(),
            '<exists>',
            len(self.tiers)
        ]
        return '\n'.join(map(str, header + self.tiers))
    

class Tier(object):
    "A general tier."
    
    def __init__(self, start_time=0, end_time=0, name=''):
        super(Tier, self).__init__()
        self._objects = []
        self.start_time = start_time
        self.end_time = end_time
        self.name = name
        self.type = 'UnknownTier'
    
    def _add_objects(self, objects, type=None):
        """Add a list of intervals or a list of points to this tier."""
        for obj in objects:
            self._add_object(obj, type)
    
    def _add_object(self, object, type):
        """Add an interval or point to this tier."""
        if isinstance(object, type):
            self._objects.append(object)
        else:
            raise Exception('Could not add object ' + `object` + ' to this '
                + self.type + '.')
    
    def __len__(self):
        """Return number of intervals/points in this tier."""
        return len(self._objects)
    
    def __str__(self):
        """Return string representation of this tier (in short format)."""
        w = lambda x: '"' + str(x) + '"'
        tier_header = [w(self.type), w(self.name),
                    self.start_time, self.end_time, len(self)]
        return '\n'.join(map(str, tier_header + self._objects))
    

class IntervalTier(Tier):
    '''An IntervalTier.'''
    
    def __init__(self, start_time=0, end_time=0, name=''):
        super(IntervalTier, self).__init__(start_time, end_time, name)
        self.type = 'IntervalTier'
    
    def add_intervals(self, intervals):
        """Add a list of intervals to this tier."""
        self._add_objects(intervals, Interval)
        
    def add_interval(self, interval):
        """Add an interval to this tier."""
        self._add_object(interval, Interval)
    
    def get_intervals(self):
        """Get all intervals of this tier."""
        return self._objects
    intervals = property(fget=get_intervals,
                doc='The list of intervals of this tier.')

    def get_intervals_with_name(self, text, n=1):
        """Get the n first intervals with the specified text."""
        return [x for x in self.intervals if x.text == text][:n]
        
    
    def get_interval_by_left_bound(self, left_bound):
        """Get interval with the specified left bound (or None)."""
        index = bisect.bisect_left(map(lambda x: x.left_bound,
                    self._objects), left_bound)
        if (index != len(self._objects) and 
                    self._objects[index].left_bound == left_bound):
            return self._objects[index]
        else:
            return None
    
    def get_interval_by_right_bound(self, right_bound):
        """Get interval with the specified right bound (or None)."""
        index = bisect.bisect_left(map(lambda x: x.right_bound,
                    self._objects), right_bound)
        if (index != len(self._objects) 
                    and self._objects[index].right_bound == right_bound):
            return self._objects[index]
        else:
            return None

    def get_interval_at_time(self, time):
        """Get interval at the specified time (or None)."""
        index = bisect.bisect_left(map(lambda x: x.right_bound,
                                       self._objects), time)
        if (index != len(self._objects)):
            return self._objects[index]
        else:
            return None
    
    def __str__(self):
        """Return string representation of this tier (in short format).
        Adds empty intervals if necessary
        """
        result = ''
        last_right_bound = self.start_time
        additional_intervals = 0 
        for obj in self._objects:
            if obj.left_bound > last_right_bound:
                # insert empty interval
                empty_interval = Interval(last_right_bound, obj.left_bound)
                result += str(empty_interval) + '\n'
                additional_intervals += 1
            result += str(obj) + '\n'
            last_right_bound = obj.right_bound
        if self.end_time > last_right_bound:
            # insert empty interval at the end (if necessary)
            empty_interval = Interval(last_right_bound, self.end_time)
            result += str(empty_interval) + '\n'
            additional_intervals += 1
        w = lambda x: '"' + str(x) + '"'
        tier_header = '\n'.join(map(str, [w(self.type), w(self.name), self.start_time,
                    self.end_time, len(self) + additional_intervals]))
        return tier_header + '\n' + result
    

class PointTier(Tier):
    '''A PointTier (also "TextTier").'''
    
    def __init__(self, start_time=0, end_time=0, name=''):
        super(PointTier, self).__init__(start_time, end_time, name)
        self.type = 'TextTier'
    
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
    
    def __init__(self, left_bound, right_bound, text=''):
        super(Interval, self).__init__()
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.text = text.strip()
    
    def duration(self):
        """Get duration of this interval."""
        return self.right_bound - self.left_bound
    
    def __eq__(self, other):
        return (self.left_bound == other.left_bound
                    and self.right_bound == other.right_bound
                    and self.text == other.text)
    
    def __repr__(self):
        return 'Interval({0}, {1}, "{2}")'.format(self.left_bound, self.right_bound, self.text)
    
    def __str__(self):
        return '{0}\n{1}\n"{2}"'.format(self.left_bound, self.right_bound, self.text)
    

class Point(object):
    '''A point of time with an attached text label.'''
    
    def __init__(self, time, text):
        super(Point, self).__init__()
        self.time = time
        self.text = text.strip()
    
    def __eq__(self, other):
        return self.time == other.time and self.text == other.text
    
    def __repr__(self):
        return 'Point({0}, "{1}")'.format(self.time, self.text)
    
    def __str__(self):
        return '{0}\n"{1}"'.format(self.time, self.text)
    

##  Functions for reading TextGrid files in the 'short' format.
##----------------------------------------------------------------------------

def read_short_textgrid(filename):
    '''Reads a Praat short TextGrid file and returns a TextGrid object.'''
    f = open(filename, 'r')
    # read whole file into memory ignoring empty lines
    stg = filter(lambda s: s != '', map(lambda s: s[0:-1], f.readlines()))
    f.close()
    tg = TextGrid(filename)
    if stg[0] != 'File type = "ooTextFile"':
        raise Exception(filename)
    if stg[1] != 'Object class = "TextGrid"':
        raise Exception(filename)
    read_start_time = float(stg[2])
    read_end_time = float(stg[3])
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

def write_short_textgrid(textgrid, filename):
    '''Writes a TextGrid object to a Praat short TextGrid file.'''
    textgrid.write_to_file(filename)

def read_interval_tier(stg_extract):
    '''Reads and returns an IntervalTier.'''
    name = stg_extract[1][1:-1] # name w/o quotes
    start_time = float(stg_extract[2])
    end_time = float(stg_extract[3])
    it = IntervalTier(start_time, end_time, name)
    i = 5
    while i < len(stg_extract):
        it.add_interval(Interval(float(stg_extract[i]), # left bound
            float(stg_extract[i+1]),                    # right bound 
            stg_extract[i+2][1:-1]))                    # text w/o quotes
        i += 3
    return it

def read_point_tier(stg_extract):
    '''Reads and returns a PointTier (called TextTier).'''    
    name = stg_extract[1][1:-1] # name w/o quotes
    start_time = float(stg_extract[2])
    end_time = float(stg_extract[3])
    pt = PointTier(start_time, end_time, name)
    i = 5
    while i < len(stg_extract):
        pt.add_point(Point(float(stg_extract[i]), # time
            stg_extract[i+1][1:-1]))              # text w/o quotes
        i += 2
    return pt

