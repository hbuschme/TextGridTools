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
import itertools
import math
import operator
import re


__all__ = [
    # Classes
    'TextGrid', 'IntervalTier', 'Interval', 'PointTier', 'Point', 'Time',
    # Functions
    'read_textgrid', 'read_short_textgrid', 'read_long_textgrid',
    'export_to_short_textgrid', 'export_to_long_textgrid', 'write_to_file',
    'get_overlapping_intervals'
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
        return map(operator.attrgetter('name'), self.tiers)
        
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

    def __len__(self):
        '''Return the number of tiers.'''
        return len(self.tiers)

    
class Tier(object):
    "An abstract tier."
    
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
        return '{0}(start_time={1}, end_time={2}, name="{3}", objects={4})'.format(self.__class__.__name__,
                                                                          self.start_time,
                                                                          self.end_time,
                                                                          self.name,
                                                                          self._objects)


class IntervalTier(Tier):
    '''An IntervalTier.'''
    
    def __init__(self, start_time=0, end_time=0, name='', objects=None):
        super(IntervalTier, self).__init__(Time(start_time), Time(end_time),
            name, objects)
    
    def add_intervals(self, intervals):
        """Add a list of intervals to this tier."""
        self._add_objects(intervals, Interval)
        
    def add_interval(self, interval):
        """Add an interval to this tier. Insert an empty interval if
        necessary."""
        self._add_object(interval, Interval)
    
    def _get_intervals(self):
        """Get all intervals of this tier. Insert empty intervals if
        necessary."""
        return self._objects

    intervals = property(fget=_get_intervals,
                doc='The list of intervals of this tier.')

    def get_interval(self, time):
        """Get interval at the specified time (or None)."""
        index = bisect.bisect_right(map(operator.attrgetter('end_time'),
                                        self._objects), time)
        if (index != len(self._objects) and time >= self._objects[index].start_time):
            return self._objects[index]
        else:
            return None

    def get_interval_by_start_time(self, start_time):
        """Get interval with the specified left bound (or None)."""
        index = bisect.bisect_left(map(operator.attrgetter('start_time'),
                self._objects), start_time)
        if (index != len(self._objects) and 
                    self._objects[index].start_time == start_time):
            return self._objects[index]
        else:
            return None
    
    def get_interval_by_end_time(self, end_time):
        """Get interval with the specified right bound (or None)."""
        index = bisect.bisect_left(map(operator.attrgetter('end_time'),
                self._objects), end_time)
        if (index != len(self._objects) 
                    and self._objects[index].end_time == end_time):
            return self._objects[index]
        else:
            return None

    def get_intervals_between_timepoints(self, start, end, left_overlap=False, right_overlap=False):
        """Get intervals between start and end. If left_overlap or
        right_overlap is False (the default) intervals overlapping
        with start or end are excluded."""
        get_end_time = operator.attrgetter('end_time')
        get_start_time = operator.attrgetter('start_time')
        if left_overlap:
            index_lo = bisect.bisect_right(map(get_end_time,
                                               self._objects), start)
        else:
            index_lo = bisect.bisect_left(map(get_start_time,
                                              self._objects), start)

        if right_overlap:
            index_hi = bisect.bisect_left(map(get_start_time,
                                              self._objects), end)
        else:
            index_hi = bisect.bisect_right(map(get_end_time,
                                               self._objects), end)
        return self._objects[index_lo:index_hi]

    def get_intervals_with_text(self, text, n=0):
        """Get the intervals with the specified text.
        Returns the first n results for n > 0 and the last n results for n < 0.
        """
        result = [x for x in self.intervals if x.text == text]
        if limit == 0:
            return result # Return all matching intervals
        elif limit > 0:
            return result[:n] # Return the first n matching intervals
        else: # i.e., limit < 0
            return result[n:] # Return the last n matching intervals


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
    
    def get_point(self, time):
        """Get point at specified point of time."""
        index = bisect_left(map(lambda x: x.time, self._objects), time)
        if index != len(self._objects) and self._objects[index].time == time:
            return self._objects[index]
        else:
            return None

    def get_points_between_timepoints(self, start, end, left_inclusive=False, right_inclusive=False):
        """Get intervals between start and end. If left_inclusive or
        right_inclusive is False (the default) points coinciding
        with start or end are excluded."""
        get_time = operator.attrgetter('time')
        if left_inclusive:
            index_lo = bisect.bisect_left(map(get_time, self._objects), start)
        else:
            index_lo = bisect.bisect_right(map(get_time, self._objects), start)
        if right_inclusive:
            index_hi = bisect.bisect_right(map(get_time, self._objects), end)
        else:
            index_hi = bisect.bisect_left(map(get_time, self._objects), end)
        return self._objects[index_lo:index_hi]

    def get_points_with_text(self, text, n=0):
        """Get the points with the specified text.
        Returns the first n results for n > 0 and the last n results for n < 0.
        """
        result = [x for x in self.points if x.text == text]
        if limit == 0:
            return result # Return all matching points
        elif limit > 0:
            return result[:n] # Return the first n matching points
        else: # i.e., limit < 0
            return result[n:] # Return the last n matching points
    

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
        stg = filter(lambda s: s not in ['','"'], 
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
        '''Read and return a PointTier (called TextTier) from a short TextGrid.'''    
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
    '''Read a Praat long TextGrid file and return a TextGrid object.'''

    def get_attr_val(x):
        """Extract the attribute value from a long TextGrid line."""
        return x.split(' = ')[1]

    def read_interval_tier(stg_extract):
        '''Read and return an IntervalTier from a long TextGrid.'''
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
        '''Read and return a PointTier (called TextTier) from a long TextGrid.'''    
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


##  Functions for writing TextGrid files
##----------------------------------------------------------------------------

def correct_end_times(textgrid):
    """Correct then end times of all Tiers of a Textgrid object.

    Modifies the end times of all tiers to textgrid.end_time and (for
    IntervalTiers) adds the final empty intervals if necessary.
    
    """
    textgrid_copy = copy.deepcopy(textgrid)
    for tier in textgrid_copy.tiers:
        if isinstance(tier, IntervalTier) and tier.end_time < textgrid_copy.end_time:
            # For interval tiers insert the final empty interval
            # if necessary.
            empty_interval = Interval(tier.end_time, textgrid_copy.end_time, '')
            tier._add_object(empty_interval, Interval)
        tier.end_time = textgrid_copy.end_time
    return textgrid_copy


def export_to_short_textgrid(textgrid, encoding='utf-8'):
    '''Convert a TextGrid object into a string of Praat short TextGrid format.'''
    result =  ['File type = "ooTextFile"',
               'Object class = "TextGrid"',
               '',
               textgrid.start_time,
               textgrid.end_time,
               '<exists>',
               len(textgrid.tiers)]
    textgrid_corrected = correct_end_times(textgrid)
    quote = lambda x: '"' + unicode(x) + '"'
    for tier in textgrid_corrected.tiers:
        result += ['"{0}"'.format(unicode(tier.__class__.__name__)),
                         '"{0}"'.format(unicode(tier.name)),
                         tier.start_time, tier.end_time, len(tier)]
        if isinstance(tier, IntervalTier):
            result += [u'{0}\n{1}\n"{2}"'.format(obj.start_time, obj.end_time, obj.text)
                       for obj in tier._objects]
        elif isinstance(tier, PointTier):
            result += [u'{0}\n"{1}"'.format(obj.time, obj.text) 
                       for obj in tier._objects]
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(map(unicode, textgrid_str))


def export_to_long_textgrid(textgrid, encoding='utf-8'):
    """Convert a TextGrid object into a string of Praat long TextGrid format."""
    result =  ['File type = "ooTextFile"',
               'Object class = "TextGrid"',
               '',
               'xmin = ' + unicode(textgrid.start_time),
               'xmax = ' + unicode(textgrid.end_time),
               'tiers? <exists>',
               'size = ' + unicode(len(textgrid.tiers)),
               'item []:']    
    textgrid_corrected = correct_end_times(textgrid)
    for i, tier in enumerate(textgrid_corrected.tiers):
        result += ['\titem [{0}]:'.format(i + 1),
                   '\t\tclass = "{0}"'.format(tier.__class__.__name__),
                   '\t\tname = "{0}"'.format(tier.name),
                   '\t\txmin = ' + unicode(tier.start_time),
                   '\t\txmax = ' + unicode(tier.end_time),
                   '\t\tintervals: size = ' + unicode(len(tier))]
        if isinstance(tier, IntervalTier):
            for j, obj in enumerate(tier._objects):
                result += ['\t\tintervals [{0}]:'.format(j + 1),
                           '\t\t\txmin = ' + unicode(obj.start_time),
                           '\t\t\txmax = ' + unicode(obj.end_time),
                           '\t\t\ttext = "' + unicode(obj.text) + '"']
        elif isinstance(tier, PointTier):
            for j, obj in enumerate(tier._objects):
                result += ['\t\tpoints [{0}]:'.format(j + 1),
                           '\t\t\tnumber = ' + obj.time,
                           '\t\t\tmark = "' + obj.text + '"']
        else:
            Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(map(unicode, result))


def export_to_elan(textgrid, encoding='utf-8', include_empty_annotations=False,
                   point_tier_annotation_duration=40):
    """Convert a TextGrid object into a string of ELAN eaf format."""

    time_slots = collections.OrderedDict() # 
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
    for tier in textgrid.tiers:
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
        time_info.append(u'\t<TIME_SLOT TIME_SLOT_ID="{0}" \
            TIME_VALUE="{1}"/>'.format(time_slot_id, str(time_value)))
    time_info.append(u'</TIME_ORDER>')
    # Create ELAN footer
    foot = [u'<LINGUISTIC_TYPE GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>',
            u'<LOCALE COUNTRY_CODE="US" LANGUAGE_CODE="en"/>',
            u'</ANNOTATION_DOCUMENT>']
    eaf = head + time_info + annotations + foot
    return '\n'.join(map(unicode, eaf))


# Listing of currently supported export formats.
_EXPORT_FORMATS = {
    # Export to Praat TextGrid in short format
    'short' : export_to_short_textgrid,
    # Export to Praat TextGrid in long (i.e., standard) format
    'long' : export_to_long_textgrid,
    # Export to ELAN .seaf format
    'eaf' : export_to_elan,
}


def write_to_file(textgrid, filename, format='short', encoding='utf-8', **kwargs):
    """Write a TextGrid object to a file in the specified format."""
    with codecs.open(filename, 'w', encoding) as f:
        if format in _EXPORT_FORMATS:
            f.write(_EXPORT_FORMATS[format](textgrid, encoding, **kwargs))
        else:
            Exception('Unknown output format: {0}'.format(format))


##  High-level functions
##----------------------------------------------------------------------------
        
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
