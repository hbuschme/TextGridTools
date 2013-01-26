#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import tgt
import unittest

class TestTime(unittest.TestCase):

    def setUp(self):
        self.t1 = tgt.Time(1.0)
        self.t2 = tgt.Time(1.1)
        self.t3 = tgt.Time(1.01)
        self.t4 = tgt.Time(1.001)
        self.t5 = tgt.Time(1.00001)

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
        t = tgt.Tier()

        # Add to empty tier
        ao1 = tgt.AnnotationObject(0.0, 0.5, 'ao1')
        t._add_object(ao1)
        self.assertTrue(len(t) == 1)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.5)

        # Append to tier leaving empty space
        ao2 = tgt.AnnotationObject(0.6, 0.75, 'ao2')
        t._add_object(ao2)
        self.assertTrue(len(t) == 2)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.75)

        ao3 = tgt.AnnotationObject(0.81, 0.9, 'ao3')
        t._add_object(ao3)
        self.assertTrue(len(t) == 3)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # Insert between existing annotation objects
        # - leaving gaps on both sides
        ao4 = tgt.AnnotationObject(0.75, 0.77, 'ao4')
        t._add_object(ao4) 
        self.assertTrue(len(t) == 4)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # - meeting preceeding annotation object
        ao5 = tgt.AnnotationObject(0.77, 0.79, 'ao5')
        t._add_object(ao5)
        self.assertTrue(len(t) == 5)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # - meeting preceeding and succeeding annotation object
        ao6 = tgt.AnnotationObject(0.8, 0.81, 'ao6')
        t._add_object(ao6) 
        self.assertTrue(len(t) == 6)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

        # Insert at a place that is already occupied
        # - within ao3
        with self.assertRaises(ValueError):
            ao7 = tgt.AnnotationObject(0.85, 0.87, 'ao7')
            t._add_object(ao7)
        # - same boundaries as ao3
        with self.assertRaises(ValueError):
            ao8 = tgt.AnnotationObject(0.81, 0.9, 'ao8')
            t._add_object(ao8)
        # - start time earlier than start time of ao3
        with self.assertRaises(ValueError):
            ao9 = tgt.AnnotationObject(0.8, 0.89, 'ao9')
            t._add_object(ao9)
        # - end time later than end time of ao3
        with self.assertRaises(ValueError):
            ao10 = tgt.AnnotationObject(0.82, 0.91, 'ao10')
            t._add_object(ao10)
        # - start time earlier than start time of ao3 and 
        #   end time later than end time of ao3
        with self.assertRaises(ValueError):
            ao11 = tgt.AnnotationObject(0.8, 0.91, 'ao11')
            t._add_object(ao11)

        # - Check that no annotation object was added
        self.assertTrue(len(t) == 6)
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 0.9)

    def test_start_end_times(self):
        t = tgt.Tier(1, 2)

        # Check whether specified start/end times are used
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 2)

        # Check whether adding an annotation within specified
        # start and end times leaves them unchanged
        t._add_object(tgt.AnnotationObject(1.1, 1.9, 'text'))
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 2)

        # Expand end time by adding an annotation that ends later
        t._add_object(tgt.AnnotationObject(2, 3, 'text'))
        self.assertTrue(t.start_time == 1)
        self.assertTrue(t.end_time == 3)

        # Expand start time by adding an annotation that starts ealier
        t._add_object(tgt.AnnotationObject(0, 1, 'text'))
        self.assertTrue(t.start_time == 0)
        self.assertTrue(t.end_time == 3)

    def test_queries(self):
        t = tgt.Tier()
        ao1 = tgt.AnnotationObject(0, 1, 'ao1')
        ao2 = tgt.AnnotationObject(1, 2, 'ao2')
        ao3 = tgt.AnnotationObject(5, 6, 'ao3')
        t._add_objects([ao1, ao2, ao3])

        # Query with start time
        # - query for existing objects
        ao1_retr = t._get_object_by_start_time(ao1.start_time)
        self.assertTrue(ao1_retr == ao1)
        ao2_retr = t._get_object_by_start_time(ao2.start_time)
        self.assertTrue(ao2_retr == ao2)
        ao3_retr = t._get_object_by_start_time(ao3.start_time)
        self.assertTrue(ao3_retr == ao3)
        # - query for non-existing object
        aox_retr = t._get_object_by_start_time(0.5)
        self.assertTrue(aox_retr is None)

        # Query with end time
        # - query for existing objects
        ao1_retr = t._get_object_by_end_time(ao1.end_time)
        self.assertTrue(ao1_retr == ao1)
        ao2_retr = t._get_object_by_end_time(ao2.end_time)
        self.assertTrue(ao2_retr == ao2)
        ao3_retr = t._get_object_by_end_time(ao3.end_time)
        self.assertTrue(ao3_retr == ao3)
        # - query for non-existing object
        aox_retr = t._get_object_by_end_time(0.5)
        self.assertTrue(aox_retr is None)

        # Query with time
        # - query for existing objects
        #   - time falls within object
        ao1_retr = t._get_objects_by_time(ao1.start_time + (ao1.end_time - ao1.start_time) * 0.5)
        self.assertTrue(ao1_retr[0] == ao1)
        #   - time equals end time of object
        ao2_retr = t._get_objects_by_time(ao2.end_time)
        self.assertTrue(ao2_retr[0] == ao2)
        #   - time equals start time of object
        ao3_retr = t._get_objects_by_time(ao3.start_time)
        self.assertTrue(ao3_retr[0] == ao3)
        #   - time equals start time of one object and end_time of another
        ao12_retr = t._get_objects_by_time(ao1.end_time)
        self.assertTrue(len(ao12_retr) == 2)
        self.assertTrue(ao12_retr[0] == ao1)
        self.assertTrue(ao12_retr[1] == ao2)

        # - query for non-existing object
        aox_retr = t._get_objects_by_time(3)
        self.assertTrue(aox_retr == [])

        # Query with text/regex
        # - one match
        ao1_retr = t._get_objects_with_matching_text('ao1')
        self.assertTrue(len(ao1_retr) == 1)
        self.assertTrue(ao1_retr[0] == ao1)

        # - mutiple matches
        ao31 = tgt.AnnotationObject(7, 8, 'ao3')
        ao32 = tgt.AnnotationObject(9, 10, 'ao3')
        ao33 = tgt.AnnotationObject(11, 12, 'ao3')
        t._add_objects([ao31, ao32, ao33])

        ao3x_retr = t._get_objects_with_matching_text('ao3')
        self.assertTrue(len(ao3x_retr) == 4)
        self.assertTrue(ao3x_retr[0] == ao3)
        self.assertTrue(ao3x_retr[1] == ao31)
        self.assertTrue(ao3x_retr[2] == ao32)
        self.assertTrue(ao3x_retr[3] == ao33)

        # - multiple matches, select first n
        ao3xn_retr = t._get_objects_with_matching_text('ao3', 2)
        self.assertTrue(len(ao3xn_retr) == 2)
        self.assertTrue(ao3xn_retr[0] == ao3)
        self.assertTrue(ao3xn_retr[1] == ao31)

        # - multiple matches, select last n
        ao3xn_retr = t._get_objects_with_matching_text('ao3', -2)
        self.assertTrue(len(ao3xn_retr) == 2)
        self.assertTrue(ao3xn_retr[0] == ao32)
        self.assertTrue(ao3xn_retr[1] == ao33)

    def test_get_nearest_objects(self):
        t = tgt.Tier()
        ao1 = tgt.AnnotationObject(0, 1, 'ao1')
        ao2 = tgt.AnnotationObject(1, 2, 'ao2')
        ao3 = tgt.AnnotationObject(3, 4, 'ao3')
        ao4 = tgt.AnnotationObject(5, 6, 'ao4')
        t._add_objects([ao1, ao2, ao3, ao4])

        # - coincides with start time of the first interval
        r = t._get_nearest_objects(0.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(0.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao1]))

        # - lies between start and end time of the first interval
        r = t._get_nearest_objects(0.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.4, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(0.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.4, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(0.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(0.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao1]))

        r = t._get_nearest_objects(0.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.5, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(0.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(0.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(0.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(0.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        r = t._get_nearest_objects(0.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.6, boundary='end', direction='left')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(0.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(0.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(0.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(0.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(0.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        # - coincides with end time of one interval and coincides with start
        #   time of another interval
        r = t._get_nearest_objects(1.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(1.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(1.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(1.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(1.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(1.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao1, ao2]))
        r = t._get_nearest_objects(1.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(1.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao1]))
        r = t._get_nearest_objects(1.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao1, ao2]))

        ## - lies between two intervals
        r = t._get_nearest_objects(2.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.4, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.4, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao2]))

        r = t._get_nearest_objects(2.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao3, ao2]))

        r = t._get_nearest_objects(2.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(2.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(2.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - coincides with start time of an isolated interval
        r = t._get_nearest_objects(3.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(3.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao2, ao3]))
        r = t._get_nearest_objects(3.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - lies withing an isolated interval
        r = t._get_nearest_objects(3.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        r = t._get_nearest_objects(3.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(3.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(3.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        r = t._get_nearest_objects(3.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao2]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(3.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        ## - coincides with end time of an isolated interval
        r = t._get_nearest_objects(4.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(4.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao3, ao4]))
        r = t._get_nearest_objects(4.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(4.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao3]))

        #5.0, 5.4, 5.5, 5.6, 6.0

        ## - coincides with start time of the last interval
        r = t._get_nearest_objects(5.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(5.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='start', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao3, ao4]))
        r = t._get_nearest_objects(5.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        ## - lies withing an the last interval
        r = t._get_nearest_objects(5.4, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(5.4, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(5.4, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.4, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        r = t._get_nearest_objects(5.5, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(5.5, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(5.5, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.5, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        r = t._get_nearest_objects(5.6, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='end', direction='left')
        self.assertTrue(r == set([ao3]))
        r = t._get_nearest_objects(5.6, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(5.6, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(5.6, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))

        ## - coincides with end time of the last interval
        r = t._get_nearest_objects(6.0, boundary='start', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='end', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='both', direction='left')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='start', direction='right')
        self.assertTrue(r == set([]))
        r = t._get_nearest_objects(6.0, boundary='end', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='both', direction='right')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='start', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='end', direction='both')
        self.assertTrue(r == set([ao4]))
        r = t._get_nearest_objects(6.0, boundary='both', direction='both')
        self.assertTrue(r == set([ao4]))


class TestInterval(unittest.TestCase):

    def test_change_time(self):
        ict = tgt.Interval(0, 1)
        # Changing start and end times has an effect
        ict.start_time = 0.5
        self.assertTrue(ict.start_time == 0.5)
        ict.end_time = 1.5
        self.assertTrue(ict.end_time == 1.5)
        # Correct order of start and end times is checked
        with self.assertRaises(ValueError):
            tgt.Interval(1,0)
        with self.assertRaises(ValueError):
            ict.start_time = 2.0
        with self.assertRaises(ValueError):
            ict.end_time = 0

    def test_change_text(self):
        ict = tgt.Interval(0, 1, 'text')
        self.assertTrue(ict.text == 'text')
        ict.text = 'text changed'
        self.assertTrue(ict.text == 'text changed')

    def test_duration(self):
        self.id1 = tgt.Interval(0, 1)
        self.assertTrue(self.id1.duration() == 1.0)
        self.id2 = tgt.Interval(1, 1)
        self.assertTrue(self.id2.duration() == 0)

    def test_equality(self):
        ie1 = tgt.Interval(0, 1, 'text')
        ie2 = tgt.Interval(0, 1, 'text')
        self.assertTrue(ie1 == ie2)
        ie3 = tgt.Interval(1, 1, 'text')
        self.assertFalse(ie1 == ie3)
        ie4 = tgt.Interval(0, 2, 'text')
        self.assertFalse(ie1 == ie4)
        ie5 = tgt.Interval(0, 1, 'text changed')
        self.assertFalse(ie1 == ie5)

    def test_repr(self):
        ir = tgt.Interval(0, 1, 'text')
        s = repr(ir)
        from tgt import Interval
        ir_recreated = eval(s)
        self.assertTrue(ir == ir_recreated)


class TestPoint(unittest.TestCase):

    def test_change_time(self):
        pct = tgt.Point(0)
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
        pct = tgt.Point(0, 'text')
        self.assertTrue(pct.text == 'text')
        pct.text = 'text changed'
        self.assertTrue(pct.text == 'text changed')

    def test_equality(self):
        pe1 = tgt.Point(0, 'text')
        pe2 = tgt.Point(0, 'text')
        self.assertTrue(pe1 == pe2)
        pe3 = tgt.Point(1, 'text')
        self.assertFalse(pe1 == pe3)
        pe4 = tgt.Point(0, 'text changed')
        self.assertFalse(pe1 == pe4)

    def test_repr(self):
        pr = tgt.Point(0, 'text')
        s = repr(pr)
        from tgt import Point
        pr_recreated = eval(s)
        self.assertTrue(pr == pr_recreated)



if __name__ == '__main__':
    unittest.main()
