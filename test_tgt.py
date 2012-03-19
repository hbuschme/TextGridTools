#!/usr/bin/env python

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

    def tearDown(self):
        pass
    

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

class TestIntervalTier(unittest.TestCase):

    def setUp(self):
        self.interval1 = tgt.IntervalTier(name='interval_tier1')
        self.interval1.add_intervals([tgt.Interval(0, 0.5, ''),
                                      tgt.Interval(0.5, 2.5, 'a'),
                                      tgt.Interval(2.5, 3.5, 'b'),
                                      tgt.Interval(3.5, 5, ''),
                                      tgt.Interval(5, 6, 'c'),
                                      tgt.Interval(6, 7.5, ''),
                                      tgt.Interval(7.5, 9, 'd')])
        self.interval2 = tgt.IntervalTier(name='interval_tier2')
        self.interval2.add_intervals([tgt.Interval(0, 0.7, 'e'),
                                      tgt.Interval(0.7, 2.5, 'f'),
                                      tgt.Interval(2.5, 3.5, ''),
                                      tgt.Interval(3.5, 6, 'g'),
                                      tgt.Interval(6, 7, ''),
                                      tgt.Interval(7, 11, 'i')])
        

        
                     

    def test_get_interval_by_left_bound(self):
        self.assertTrue(self.interval1.get_interval_by_left_bound(0.5) == tgt.Interval(0.5, 2.5, 'a'))
        self.assertTrue(self.interval1.get_interval_by_left_bound(2.5) == tgt.Interval(2.5, 3.5, 'b'))
        self.assertTrue(self.interval1.get_interval_by_left_bound(7) is None)
        self.assertTrue(self.interval1.get_interval_by_left_bound(9) is None)

    def test_get_interval_by_right_bound(self):
        self.assertTrue(self.interval1.get_interval_by_right_bound(2.5) == tgt.Interval(0.5, 2.5, 'a'))
        self.assertTrue(self.interval1.get_interval_by_right_bound(3.5) == tgt.Interval(2.5, 3.5, 'b'))
        self.assertTrue(self.interval1.get_interval_by_right_bound(7) is None)
        self.assertTrue(self.interval1.get_interval_by_right_bound(9) == tgt.Interval(7.5, 9, 'd'))

    def test_get_interval_at_time(self):
        self.assertTrue(self.interval1.get_interval_at_time(1) == tgt.Interval(0.5, 2.5, 'a'))
        self.assertTrue(self.interval1.get_interval_at_time(2.5) == tgt.Interval(2.5, 3.5, 'b'))
        self.assertTrue(self.interval1.get_interval_at_time(7) == tgt.Interval(6, 7.5, ''))
        self.assertTrue(self.interval1.get_interval_at_time(9) is None)
        self.assertTrue(self.interval1.get_interval_at_time(10) is None)

    def test_get_intervals_between_timepoints(self):
        self.assertTrue(self.interval1.get_intervals_between_timepoints(-2, 0) is None)
        self.assertTrue(self.interval1.get_intervals_between_timepoints(-2, 0.25) is None)
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(0.5, 3.5) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                          tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(0.5, 3) == [tgt.Interval(0.5, 2.5,'a')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(2, 3) is None)
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(0.5, 4) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                        tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(8, 11) is None)
        self.assertTrue(self.interval1.get_intervals_between_timepoints(9, 11) is None)
        self.assertTrue(self.interval1.get_intervals_between_timepoints(10, 11) is None)

        self.assertTrue(self.interval1.get_intervals_between_timepoints(-2, 0, True, True) is None)
        self.assertTrue(self.interval1.get_intervals_between_timepoints(-2, 0.25, True, True) == [tgt.Interval(0, 0.5, '')])
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(0.5, 3.5, True, True) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                   tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(0.5, 3, True, True) == [tgt.Interval(0.5, 2.5,'a'),
                                                                             tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(2, 3, True, True) == [tgt.Interval(0.5, 2.5,'a'),
                                                                           tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(0.5, 4, True, True) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                 tgt.Interval(2.5, 3.5, 'b'),
                                                                 tgt.Interval(3.5, 5, ''),])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(8, 11, True, True) == [tgt.Interval(7.5, 9, 'd')])
        self.assertTrue(self.interval1.get_intervals_between_timepoints(9, 11, True, True) is None)
        self.assertTrue(self.interval1.get_intervals_between_timepoints(10, 11, True, True) is None)
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(1, 4, False, True) == [tgt.Interval(2.5, 3.5, 'b'),
                                                                                   tgt.Interval(3.5, 5, '')])
        self.assertTrue(
            self.interval1.get_intervals_between_timepoints(1, 4, True, False) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                        tgt.Interval(2.5, 3.5, 'b')])
    def test_get_overlapping_intervals(self):
        self.assertTrue(self.interval1.get_overlapping_intervals(self.interval2) == [tgt.Interval(0.5, 0.7, 'overlap'),
                                                                                     tgt.Interval(0.7, 2.5, 'overlap'),
                                                                                     tgt.Interval(5, 6, 'overlap'),
                                                                                     tgt.Interval(7.5, 9, 'overlap')])
        self.assertTrue(self.interval2.get_overlapping_intervals(self.interval1) == [tgt.Interval(0.5, 0.7, 'overlap'),
                                                                                     tgt.Interval(0.7, 2.5, 'overlap'),
                                                                                     tgt.Interval(5, 6, 'overlap'),
                                                                                     tgt.Interval(7.5, 9, 'overlap')])
        self.assertTrue(self.interval2.get_overlapping_intervals(self.interval1, r'^\s*$') == [tgt.Interval(6,7, 'overlap')])
        


        
if __name__ == '__main__':
    unittest.main()
