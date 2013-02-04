# -*- coding: utf-8 -*-

# TextGridTools -- Read, write, and manipulate Praat TextGrid files
# Copyright (C) 2013 Hendrik Buschmeier, Marcin Włodarczak
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

from __future__ import division, print_function

import unittest
from ..core import *

class TestTime(unittest.TestCase):

    def setUp(self):
        self.t1 = Time(1.0)
        self.t2 = Time(1.1)
        self.t3 = Time(1.01)
        self.t4 = Time(1.001)
        self.t5 = Time(1.00001)

    def test_equals(self):
        self.assertTrue(self.t1 == self.t1)
        self.assertFalse(self.t1 == self.t2)
        self.assertFalse(self.t1 == self.t3)
        self.assertFalse(self.t1 == self.t4)
        self.assertTrue(self.t1 == self.t5)

    def test_not_equals(self):
        self.assertFalse(self.t1 != self.t1)
        self.assertTrue(self.t1 != self.t2)
        self.assertTrue(self.t1 != self.t3)
        self.assertTrue(self.t1 != self.t4)
        self.assertFalse(self.t1 != self.t5)

    def test_less(self):
        self.assertFalse(self.t1 < self.t1)
        self.assertTrue(self.t1 < self.t2)
        self.assertTrue(self.t1 < self.t3)
        self.assertTrue(self.t1 < self.t4)
        self.assertFalse(self.t1 < self.t5)

    def test_greater(self):
        self.assertFalse(self.t1 > self.t1)
        self.assertFalse(self.t1 > self.t2)
        self.assertFalse(self.t1 > self.t3)
        self.assertFalse(self.t1 > self.t4)
        self.assertFalse(self.t1 > self.t5)
        self.assertTrue(self.t2 > self.t1)

    def test_greater_equal(self):
        self.assertTrue(self.t1 >= self.t1)
        self.assertFalse(self.t1 >= self.t2)
        self.assertFalse(self.t1 >= self.t3)
        self.assertFalse(self.t1 >= self.t4)
        self.assertTrue(self.t1 >= self.t5)
        self.assertTrue(self.t2 >= self.t1)

    def test_less_equal(self):
        self.assertTrue(self.t1 <= self.t1)
        self.assertTrue(self.t1 <= self.t2)
        self.assertTrue(self.t1 <= self.t3)
        self.assertTrue(self.t1 <= self.t4)
        self.assertTrue(self.t1 <= self.t5)
        self.assertFalse(self.t2 <= self.t1)

class TestTier(unittest.TestCase):

    def test_adding(self):
        t = Tier()

        # Add to empty tier
        ao1 = Annotation(0.0, 0.5, 'ao1')
        t.add_annotation(ao1)
        self.assertTrue(len(t) == 1)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.5)

        # Append to tier leaving empty space
        ao2 = Annotation(0.6, 0.75, 'ao2')
        t.add_annotation(ao2)
        self.assertTrue(len(t) == 2)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.75)

        ao3 = Annotation(0.81, 0.9, 'ao3')
        t.add_annotation(ao3)
        self.assertTrue(len(t) == 3)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # Insert between existing annotations
        # - leaving gaps on both sides
        ao4 = Annotation(0.75, 0.77, 'ao4')
        t.add_annotation(ao4) 
        self.assertTrue(len(t) == 4)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # - meeting preceeding annotation
        ao5 = Annotation(0.77, 0.79, 'ao5')
        t.add_annotation(ao5)
        self.assertTrue(len(t) == 5)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # - meeting preceeding and succeeding annotation
        ao6 = Annotation(0.8, 0.81, 'ao6')
        t.add_annotation(ao6) 
        self.assertTrue(len(t) == 6)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # Insert at a place that is already occupied
        # - within ao3
        with self.assertRaises(ValueError):
            ao7 = Annotation(0.85, 0.87, 'ao7')
            t.add_annotation(ao7)
        # - same boundaries as ao3
        with self.assertRaises(ValueError):
            ao8 = Annotation(0.81, 0.9, 'ao8')
            t.add_annotation(ao8)
        # - start time earlier than start time of ao3
        with self.assertRaises(ValueError):
            ao9 = Annotation(0.8, 0.89, 'ao9')
            t.add_annotation(ao9)
        # - end time later than end time of ao3
        with self.assertRaises(ValueError):
            ao10 = Annotation(0.82, 0.91, 'ao10')
            t.add_annotation(ao10)
        # - start time earlier than start time of ao3 and 
        #   end time later than end time of ao3
        with self.assertRaises(ValueError):
            ao11 = Annotation(0.8, 0.91, 'ao11')
            t.add_annotation(ao11)

        # - Check that no annotation was added
        self.assertTrue(len(t) == 6)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

    def test_start_end_times(self):
        t = Tier(1, 2)

        # Check whether specified start/end times are used
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 2)

        # Check whether adding an annotation within specified
        # start and end times leaves them unchanged
        t.add_annotation(Annotation(1.1, 1.9, 'text'))
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 2)

        # Expand end time by adding an annotation that ends later
        t.add_annotation(Annotation(2, 3, 'text'))
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 3)

        # Expand start time by adding an annotation that starts ealier
        t.add_annotation(Annotation(0, 1, 'text'))
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 3)

    def test_queries(self):
        t = Tier()
        ao1 = Annotation(0, 1, 'ao1')
        ao2 = Annotation(1, 2, 'ao2')
        ao3 = Annotation(5, 6, 'ao3')
        t.add_annotations([ao1, ao2, ao3])

        # Query with start time
        # - query for existing objects
        ao1_retr = t.get_annotation_by_start_time(ao1.start_time)
        self.assertTrue(ao1_retr == ao1)
        ao2_retr = t.get_annotation_by_start_time(ao2.start_time)
        self.assertTrue(ao2_retr == ao2)
        ao3_retr = t.get_annotation_by_start_time(ao3.start_time)
        self.assertTrue(ao3_retr == ao3)
        # - query for non-existing object
        aox_retr = t.get_annotation_by_start_time(0.5)
        self.assertTrue(aox_retr is None)

        # Query with end time
        # - query for existing objects
        ao1_retr = t.get_annotation_by_end_time(ao1.end_time)
        self.assertTrue(ao1_retr == ao1)
        ao2_retr = t.get_annotation_by_end_time(ao2.end_time)
        self.assertTrue(ao2_retr == ao2)
        ao3_retr = t.get_annotation_by_end_time(ao3.end_time)
        self.assertTrue(ao3_retr == ao3)
        # - query for non-existing object
        aox_retr = t.get_annotation_by_end_time(0.5)
        self.assertTrue(aox_retr is None)

        # Query with time
        # - query for existing objects
        #   - time falls within object
        ao1_retr = t.get_annotations_by_time(ao1.start_time + (ao1.end_time - ao1.start_time) * 0.5)
        self.assertTrue(ao1_retr[0] == ao1)
        #   - time equals end time of object
        ao2_retr = t.get_annotations_by_time(ao2.end_time)
        self.assertTrue(ao2_retr[0] == ao2)
        #   - time equals start time of object
        ao3_retr = t.get_annotations_by_time(ao3.start_time)
        self.assertTrue(ao3_retr[0] == ao3)
        #   - time equals start time of one object and end_time of another
        ao12_retr = t.get_annotations_by_time(ao1.end_time)
        self.assertTrue(len(ao12_retr) == 2)
        self.assertTrue(ao12_retr[0] == ao1)
        self.assertTrue(ao12_retr[1] == ao2)

        # - query for non-existing object
        aox_retr = t.get_annotations_by_time(3)
        self.assertTrue(aox_retr == [])

        # Query with text/regex
        # - one match
        ao1_retr = t.get_annotations_with_matching_text('ao1')
        self.assertTrue(len(ao1_retr) == 1)
        self.assertTrue(ao1_retr[0] == ao1)

        # - mutiple matches
        ao31 = Annotation(7, 8, 'ao3')
        ao32 = Annotation(9, 10, 'ao3')
        ao33 = Annotation(11, 12, 'ao3')
        t.add_annotations([ao31, ao32, ao33])

        ao3x_retr = t.get_annotations_with_matching_text('ao3')
        self.assertTrue(len(ao3x_retr) == 4)
        self.assertTrue(ao3x_retr[0] == ao3)
        self.assertTrue(ao3x_retr[1] == ao31)
        self.assertTrue(ao3x_retr[2] == ao32)
        self.assertTrue(ao3x_retr[3] == ao33)

        # - multiple matches, select first n
        ao3xn_retr = t.get_annotations_with_matching_text('ao3', 2)
        self.assertTrue(len(ao3xn_retr) == 2)
        self.assertTrue(ao3xn_retr[0] == ao3)
        self.assertTrue(ao3xn_retr[1] == ao31)

        # - multiple matches, select last n
        ao3xn_retr = t.get_annotations_with_matching_text('ao3', -2)
        self.assertTrue(len(ao3xn_retr) == 2)
        self.assertTrue(ao3xn_retr[0] == ao32)
        self.assertTrue(ao3xn_retr[1] == ao33)

    def test_get_nearest_annotation(self):
        t = Tier()
        ao1 = Annotation(0, 1, 'ao1')
        ao2 = Annotation(1, 2, 'ao2')
        ao3 = Annotation(3, 4, 'ao3')
        ao4 = Annotation(5, 6, 'ao4')
        t.add_annotations([ao1, ao2, ao3, ao4])

        # - coincides with start time of the first interval
        r = t.get_nearest_annotation(0.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(0.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao1]))

        # - lies between start and end time of the first interval
        r = t.get_nearest_annotation(0.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.4, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(0.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.4, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(0.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(0.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao1]))

        r = t.get_nearest_annotation(0.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.5, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(0.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(0.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(0.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(0.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        r = t.get_nearest_annotation(0.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.6, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(0.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(0.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(0.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(0.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(0.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        # - coincides with end time of one interval and coincides with start
        #   time of another interval
        r = t.get_nearest_annotation(1.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(1.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(1.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(1.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(1.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(1.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t.get_nearest_annotation(1.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(1.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t.get_nearest_annotation(1.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        ## - lies between two intervals
        r = t.get_nearest_annotation(2.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.4, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.4, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao2]))

        r = t.get_nearest_annotation(2.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao3, ao2]))

        r = t.get_nearest_annotation(2.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(2.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(2.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - coincides with start time of an isolated interval
        r = t.get_nearest_annotation(3.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(3.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao2, ao3]))
        r = t.get_nearest_annotation(3.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - lies withing an isolated interval
        r = t.get_nearest_annotation(3.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        r = t.get_nearest_annotation(3.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(3.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(3.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        r = t.get_nearest_annotation(3.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(3.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - coincides with end time of an isolated interval
        r = t.get_nearest_annotation(4.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(4.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao3, ao4]))
        r = t.get_nearest_annotation(4.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(4.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        #5.0, 5.4, 5.5, 5.6, 6.0

        ## - coincides with start time of the last interval
        r = t.get_nearest_annotation(5.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(5.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao3, ao4]))
        r = t.get_nearest_annotation(5.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        ## - lies withing an the last interval
        r = t.get_nearest_annotation(5.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(5.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(5.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        r = t.get_nearest_annotation(5.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(5.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(5.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        r = t.get_nearest_annotation(5.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t.get_nearest_annotation(5.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(5.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(5.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        ## - coincides with end time of the last interval
        r = t.get_nearest_annotation(6.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t.get_nearest_annotation(6.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t.get_nearest_annotation(6.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

    def test_get_copy_with_gaps_filled(self):
        i1 = Interval(0,2, 'i1')
        i2 = Interval(2,3, 'i2')
        i3 = Interval(4,5, 'i3')
        i4 = Interval(7,8, 'i4')
        i5 = Interval(8.5,9.5, 'i5')

        # - insert empty start interval
        t1 = IntervalTier(0, 3, 't1')
        t1.add_annotations([i2])
        t1_c = t1.get_copy_with_gaps_filled()
        self.assertTrue(len(t1) == 1)
        self.assertTrue(len(t1_c) == 2)

        # - insert emtpy end interval
        t2 = IntervalTier(0, 3, 't2')
        t2.add_annotations([i1])
        t2_c = t2.get_copy_with_gaps_filled()
        self.assertTrue(len(t2) == 1)
        self.assertTrue(len(t2_c) == 2)

        # - insert all over the place
        t3 = IntervalTier(0, 10, 't3')
        t3.add_annotations([i2, i3, i4, i5])
        t3_c = t3.get_copy_with_gaps_filled()
        self.assertTrue(len(t3) == 4)
        self.assertTrue(len(t3_c) == 9)

        # - insert into emtpy tier
        t4 = IntervalTier(0, 5, 't4')
        t4_c = t4.get_copy_with_gaps_filled()
        self.assertTrue(len(t4) == 0)
        self.assertTrue(len(t4_c) == 1)

        # - do nothing
        t5 = IntervalTier(0, 3, 't5')
        t5.add_annotations([i1, i2])
        t5_c = t5.get_copy_with_gaps_filled()
        self.assertTrue(len(t5) == 2)
        self.assertTrue(len(t5_c) == 2)


class TestInterval(unittest.TestCase):

    def test_change_time(self):
        ict = Interval(0, 1)
        # Changing start and end times has an effect
        ict.start_time = 0.5
        self.assertTrue(ict.start_time == 0.5)
        ict.end_time = 1.5
        self.assertTrue(ict.end_time == 1.5)
        # Correct order of start and end times is checked
        with self.assertRaises(ValueError):
            Interval(1,0)
        with self.assertRaises(ValueError):
            ict.start_time = 2.0
        with self.assertRaises(ValueError):
            ict.end_time = 0

    def test_change_text(self):
        ict = Interval(0, 1, 'text')
        self.assertTrue(ict.text == 'text')
        ict.text = 'text changed'
        self.assertTrue(ict.text == 'text changed')

    def test_duration(self):
        self.id1 = Interval(0, 1)
        self.assertTrue(self.id1.duration() == 1.0)
        self.id2 = Interval(1, 1)
        self.assertTrue(self.id2.duration() == 0)

    def test_equality(self):
        ie1 = Interval(0, 1, 'text')
        ie2 = Interval(0, 1, 'text')
        self.assertTrue(ie1 == ie2)
        ie3 = Interval(1, 1, 'text')
        self.assertFalse(ie1 == ie3)
        ie4 = Interval(0, 2, 'text')
        self.assertFalse(ie1 == ie4)
        ie5 = Interval(0, 1, 'text changed')
        self.assertFalse(ie1 == ie5)

    def test_repr(self):
        ir = Interval(0, 1, 'text')
        s = repr(ir)
        ir_recreated = eval(s)
        self.assertTrue(ir == ir_recreated)


class TestPoint(unittest.TestCase):

    def test_change_time(self):
        pct = Point(0)
        # Changing start and end times has an effect
        pct.time = 0.5
        self.assertTrue(pct.time == 0.5)
        self.assertTrue(pct.start_time == 0.5)
        self.assertTrue(pct.end_time == 0.5)
        pct.start_time = 1
        self.assertTrue(pct.time == 1)
        self.assertTrue(pct.start_time == 1)
        self.assertTrue(pct.end_time == 1)
        pct.end_time = 1.5
        self.assertTrue(pct.time == 1.5)
        self.assertTrue(pct.start_time == 1.5)
        self.assertTrue(pct.end_time == 1.5)

    def test_change_text(self):
        pct = Point(0, 'text')
        self.assertTrue(pct.text == 'text')
        pct.text = 'text changed'
        self.assertTrue(pct.text == 'text changed')

    def test_equality(self):
        pe1 = Point(0, 'text')
        pe2 = Point(0, 'text')
        self.assertTrue(pe1 == pe2)
        pe3 = Point(1, 'text')
        self.assertFalse(pe1 == pe3)
        pe4 = Point(0, 'text changed')
        self.assertFalse(pe1 == pe4)

    def test_repr(self):
        pr = Point(0, 'text')
        s = repr(pr)
        pr_recreated = eval(s)
        self.assertTrue(pr == pr_recreated)
