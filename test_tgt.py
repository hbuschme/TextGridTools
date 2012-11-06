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
        self.it1 = tgt.IntervalTier(
            name='interval_tier1',
            objects = [tgt.Interval(0, 0.5, ''),
                       tgt.Interval(0.5, 2.5, 'a'),
                       tgt.Interval(2.5, 3.5, 'b'),
                       tgt.Interval(3.5, 5, ''),
                       tgt.Interval(5, 6, 'c')])
        
    def test_get_interval_by_left_bound(self):
        self.assertTrue(self.it1.get_interval_by_start_time(-1) is None)
        self.assertTrue(self.it1.get_interval_by_start_time(0) == tgt.Interval(0, 0.5, ''))
        self.assertTrue(self.it1.get_interval_by_start_time(1) is None)
        self.assertTrue(self.it1.get_interval_by_start_time(2.5) == tgt.Interval(2.5, 3.5, 'b'))
        self.assertTrue(self.it1.get_interval_by_start_time(6) is None)
        self.assertTrue(self.it1.get_interval_by_start_time(7) is None)

    def test_get_interval_by_right_bound(self):
        self.assertTrue(self.it1.get_interval_by_end_time(-1) is None)
        self.assertTrue(self.it1.get_interval_by_end_time(0) is None)
        self.assertTrue(self.it1.get_interval_by_end_time(1) is None)
        self.assertTrue(self.it1.get_interval_by_end_time(2.5) == tgt.Interval(0.5, 2.5, 'a'))
        self.assertTrue(self.it1.get_interval_by_end_time(6) == tgt.Interval(5, 6, 'c'))
        self.assertTrue(self.it1.get_interval_by_end_time(7) is None)

    def test_get_interval_at_time(self):
        self.assertTrue(self.it1.get_interval_at_time(-1) is None)
        self.assertTrue(self.it1.get_interval_at_time(0) == tgt.Interval(0, 0.5, ''))
        self.assertTrue(self.it1.get_interval_at_time(1) == tgt.Interval(0.5, 2.5, 'a'))
        self.assertTrue(self.it1.get_interval_at_time(2.5) == tgt.Interval(2.5, 3.5, 'b'))
        self.assertTrue(self.it1.get_interval_at_time(6) is None)
        self.assertTrue(self.it1.get_interval_at_time(7) is None)

    def test_get_intervals_between_timepoints(self):
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0, True, True) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0.25) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0.25, True, True) == [tgt.Interval(0, 0.5, '')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0.25, True, False) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(-2, 0.25, False, True) == [tgt.Interval(0, 0.5, '')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(0.5, 3.5) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                                tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(0.5, 3.5, True, True) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                                            tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(1, 4) == [tgt.Interval(2.5, 3.5, 'b')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(1, 4, False, True) == [tgt.Interval(2.5, 3.5, 'b'),
                                                                                         tgt.Interval(3.5, 5, '')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(1, 4, True, False) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                                         tgt.Interval(2.5, 3.5, 'b'),])
        self.assertTrue(self.it1.get_intervals_between_timepoints(1, 4, True, True) == [tgt.Interval(0.5, 2.5, 'a'),
                                                                                        tgt.Interval(2.5, 3.5, 'b'),
                                                                                        tgt.Interval(3.5, 5, '')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(4, 4.5) == []) 
        self.assertTrue(self.it1.get_intervals_between_timepoints(4, 4.5, True, False) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(4, 4.5, False, True) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(4, 4.5, True, True) == [tgt.Interval(3.5, 5, '')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(5.5, 7) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(5.5, 7, True, False) == [tgt.Interval(5, 6, 'c')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(5.5, 7, False, True) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(5.5, 7, True, True) == [tgt.Interval(5, 6, 'c')])
        self.assertTrue(self.it1.get_intervals_between_timepoints(7, 8) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(7, 8, True, False) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(7, 8, False, True) == [])
        self.assertTrue(self.it1.get_intervals_between_timepoints(7, 8, True, True) == [])

if __name__ == '__main__':
    unittest.main()
