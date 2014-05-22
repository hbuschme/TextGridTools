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

import copy
import datetime
import collections

from .core import TextGrid, IntervalTier, Interval, PointTier, Point, Time


def read_textgrid(filename, encoding='utf-8', include_empty_intervals=False):
    '''Read a Praat TextGrid file and return a TextGrid object. 
    If include_empty_intervals is False (the default), empty intervals
    are excluded. If True, they are included. Empty intervals from specific
    tiers can be also included by specifying tier names as a string (for one tier)
    or as a list.'''
    with open(filename, 'rt', encoding=encoding) as f:
        # Read whole file into memory ignoring empty lines and lines consisting
        # solely of a single double quotes.
        stg = [line.strip() for line in f.readlines()
            if line.strip() not in ['', '"']]
    if stg[0] != 'File type = "ooTextFile"':
        raise Exception(filename)
    if stg[1] != 'Object class = "TextGrid"':
        raise Exception(filename)
    # Determine the TextGrid format.
    if stg[2].startswith('xmin'):
        return read_long_textgrid(filename, stg, include_empty_intervals)
    else:
        return read_short_textgrid(filename, stg, include_empty_intervals)


def read_short_textgrid(filename, stg, include_empty_intervals=False):
    '''Read a Praat short TextGrid file and return a TextGrid object.'''

    def read_interval_tier(stg_extract):
        '''Read and return an IntervalTier from a short TextGrid.'''
        name = stg_extract[1].strip('"')  # name w/o quotes
        start_time = Time(stg_extract[2])
        end_time = Time(stg_extract[3])
        include_empty_intervals_this_tier = include_empty_intervals_in_tier(name, include_empty_intervals)
        it = IntervalTier(start_time, end_time, name)
        i = 5
        while i < len(stg_extract):
            text = stg_extract[i + 2].strip('"') # text w/o quotes
            if text.strip() != '' or include_empty_intervals_this_tier:
                it.add_annotation(Interval(
                    Time(stg_extract[i]), # left bound
                    Time(stg_extract[i + 1]), # right bound
                    text))
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
            text = stg_extract[i + 1].strip('"') # text w/o quotes
            pt.add_annotation(Point(
                stg_extract[i], # time
                text))   
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


def read_long_textgrid(filename, stg, include_empty_intervals=False):
    '''Read a Praat long TextGrid file and return a TextGrid object.'''

    def get_attr_val(x):
        """Extract the attribute value from a long TextGrid line."""
        return x.split(' = ')[1]

    def read_interval_tier(stg_extract):
        '''Read and return an IntervalTier from a long TextGrid.'''
        name = get_attr_val(stg_extract[2])[1:-1]  # name w/o quotes
        start_time = get_attr_val(stg_extract[3])
        end_time = get_attr_val(stg_extract[4])
        include_empty_intervals_this_tier = include_empty_intervals_in_tier(name, include_empty_intervals)
        it = IntervalTier(start_time, end_time, name)
        i = 7
        while i < len(stg_extract):
            text = get_attr_val(stg_extract[i + 2])[1:-1] # text w/o quotes
            if text.strip() != '' or include_empty_intervals_this_tier:
                it.add_annotation(Interval(
                    Time(get_attr_val(stg_extract[i])), # left bound
                    Time(get_attr_val(stg_extract[i + 1])), # right bound
                    text))
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
            text = get_attr_val(stg_extract[i + 1])[1:-1] # text w/o quotes
            pt.add_annotation(Point(
                Time(get_attr_val(stg_extract[i])), # time
                text))
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

def include_empty_intervals_in_tier(tier_name, include_empty_intervals):
    """Check whether to include empty intervals for a particular tier"""
    if isinstance(include_empty_intervals, bool):
        return include_empty_intervals
    elif isinstance(include_empty_intervals, str):
        return tier_name == include_empty_intervals
    elif isinstance(include_empty_intervals, list):
        return tier_name in include_empty_intervals
    else:
        raise TypeError('Invalid type of include_empty_intervals: {0}.'.format(type(include_empty_intervals)))

##  Functions for writing TextGrid files
##----------------------------------------------------------------------------

def correct_start_end_times_and_fill_gaps(textgrid):
    '''Correct the start/end times of all tiers and fill gaps.

    Returns a copy of a textgrid, where empty gaps between intervals
    are filled with empty intervals and where start and end times are
    unified with the start and end times of the whole textgrid.
    '''
    textgrid_copy = copy.deepcopy(textgrid)
    for tier in textgrid_copy:
        if isinstance(tier, IntervalTier):
            tier_corrected = tier.get_copy_with_gaps_filled(textgrid.start_time, textgrid.end_time)
            position = textgrid_copy.tiers.index(tier)
            textgrid_copy.tiers[position] = tier_corrected
    return textgrid_copy

def export_to_short_textgrid(textgrid):
    '''Convert a TextGrid object into a string of Praat short TextGrid format.'''
    result = ['File type = "ooTextFile"',
              'Object class = "TextGrid"',
              '',
              str(textgrid.start_time),
              str(textgrid.end_time),
              '<exists>',
              str(len(textgrid))]
    textgrid_corrected = correct_start_end_times_and_fill_gaps(textgrid)
    for tier in textgrid_corrected:
        result += ['"' + tier.tier_type() + '"',
                   '"' + tier.name + '"',
                   str(tier.start_time), str(tier.end_time), str(len(tier))]
        if isinstance(tier, IntervalTier):
            result += [u'{0}\n{1}\n"{2}"'.format(obj.start_time, obj.end_time, obj.text)
                       for obj in tier]
        elif isinstance(tier, PointTier):
            result += [u'{0}\n"{1}"'.format(obj.time, obj.text)
                       for obj in tier]
        else:
            raise Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(result)


def export_to_long_textgrid(textgrid):
    """Convert a TextGrid object into a string of Praat long TextGrid format."""
    result = ['File type = "ooTextFile"',
              'Object class = "TextGrid"',
              '',
              'xmin = ' + str(textgrid.start_time),
              'xmax = ' + str(textgrid.end_time),
              'tiers? <exists>',
              'size = ' + str(len(textgrid)),
              'item []:']
    textgrid_corrected = correct_start_end_times_and_fill_gaps(textgrid)
    for i, tier in enumerate(textgrid_corrected):
        result += ['\titem [{0}]:'.format(i + 1),
                   '\t\tclass = "{0}"'.format(tier.tier_type()),
                   '\t\tname = "{0}"'.format(tier.name),
                   '\t\txmin = ' + str(tier.start_time),
                   '\t\txmax = ' + str(tier.end_time),
                   '\t\tintervals: size = ' + str(len(tier))]
        if isinstance(tier, IntervalTier):
            for j, obj in enumerate(tier):
                result += ['\t\tintervals [{0}]:'.format(j + 1),
                           '\t\t\txmin = ' + str(obj.start_time),
                           '\t\t\txmax = ' + str(obj.end_time),
                           '\t\t\ttext = "' + obj.text + '"']
        elif isinstance(tier, PointTier):
            for j, obj in enumerate(tier):
                result += ['\t\tpoints [{0}]:'.format(j + 1),
                           '\t\t\tnumber = ' + str(obj.time),
                           '\t\t\tmark = "' + obj.text + '"']
        else:
            raise Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(result)


def export_to_elan(textgrid, encoding='utf-8', include_empty_intervals=False,
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
    textgrid_copy = correct_start_end_times_and_fill_gaps(textgrid) if include_empty_intervals else textgrid
    for tier in textgrid_copy:
        annotations.append(u'<TIER DEFAULT_LOCALE="en" LINGUISTIC_TYPE_REF="default-lt" TIER_ID="{0}">'.format(tier.name))
        if isinstance(tier, IntervalTier):
            for interval in tier:
                if include_empty_intervals or interval.text != '':
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
            raise Exception('Unknown tier type: {0}'.format(tier.name))
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
    return '\n'.join(eaf)


def export_to_table(textgrid, separator=','):
    """Convert a TextGrid object into a table with fields delimited
    with the specified separator (comma by default)."""
    result = [separator.join(['tier_name', 'tier_type', 'start_time', 'end_time', 'text'])]

    for tier in textgrid:
        if isinstance(tier, IntervalTier):
            for obj in tier:
                if obj.text:
                    result.append(separator.join([tier.name, tier.tier_type(),
                                                  str(obj.start_time), str(obj.end_time), obj.text]))
        elif isinstance(tier, PointTier):
            for obj in tier:
                result.append(separator.join([tier.name, tier.tier_type(),
                                              str(obj.time), str(obj.time), obj.text]))
        else:
            raise Exception('Unknown tier type: {0}'.format(tier.name))
    return '\n'.join(result)


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
    with open(filename, 'w', encoding=encoding) as f:
        if format in _EXPORT_FORMATS:
            f.write(_EXPORT_FORMATS[format](textgrid, **kwargs))
        else:
            raise Exception('Unknown output format: {0}'.format(format))
