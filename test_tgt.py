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
        self.interval_tier1 = tgt.IntervalTier(name='interval_tier1')
        self.intervals1 = [tgt.Interval(0, 0.5, ''),
                           tgt.Interval(0.5, 2.5, 'a'),
                           tgt.Interval(2.5, 3.5, 'b'),
                           tgt.Interval(3.5, 5, ''),
                           tgt.Interval(5, 6, 'c')]
        self.interval_tier1.add_intervals(self.intervals1)
        self.interval_tier2 = tgt.IntervalTier(name='interval_tier2',)
        self.intervals2 = [tgt.Interval(0, 0.7, 'e'),
                           tgt.Interval(0.7, 2.5, ''),
                           tgt.Interval(2.5, 3.5, 'f'),
                           tgt.Interval(3.5, 6, ''),
                           tgt.Interval(6, 7, 'g'),
                           tgt.Interval(7, 11, 'h')]
        self.interval_tier2.add_intervals(self.intervals2)
        
    def test_get_interval_by_left_bound(self):
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(-1) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(0) == self.intervals1[0])
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(1) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(2.5) == self.intervals1[2])
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(6) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_left_bound(7) is None)

    def test_get_interval_by_right_bound(self):
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(-1) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(0) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(1) is None)
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(2.5) == self.intervals1[1])
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(6) is self.intervals1[4])
        self.assertTrue(self.interval_tier1.get_interval_by_right_bound(7) is None)

    def test_get_interval_at_time(self):
        self.assertTrue(self.interval_tier1.get_interval_at_time(-1) is None)
        self.assertTrue(self.interval_tier1.get_interval_at_time(0) == self.intervals1[0])
        self.assertTrue(self.interval_tier1.get_interval_at_time(1) == self.intervals1[1])
        self.assertTrue(self.interval_tier1.get_interval_at_time(2.5) == self.intervals1[2])
        self.assertTrue(self.interval_tier1.get_interval_at_time(6) is None)
        self.assertTrue(self.interval_tier1.get_interval_at_time(7) is None)

    def test_get_intervals_between_timepoints(self):
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0, True, True) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0.25) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0.25, True, True) == [self.intervals1[0]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0.25, True, False) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(-2, 0.25, False, True) == [self.intervals1[0]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(0.5, 3.5) == self.intervals1[1:3])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(0.5, 3.5, True, True) == self.intervals1[1:3])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(1, 4) == [self.intervals1[2]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(1, 4, False, True) == self.intervals1[2:4])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(1, 4, True, False) == self.intervals1[1:3])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(1, 4, True, True) == self.intervals1[1:4])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(4, 4.5) == []) 
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(4, 4.5, True, False) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(4, 4.5, False, True) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(4, 4.5, True, True) == [self.intervals1[3]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(5.5, 7) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(5.5, 7, True, False) == [self.intervals1[-1]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(5.5, 7, False, True) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(5.5, 7, True, True) == [self.intervals1[-1]])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(7, 8) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(7, 8, True, False) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(7, 8, False, True) == [])
        self.assertTrue(self.interval_tier1.get_intervals_between_timepoints(7, 8, True, True) == [])

    def test_get_overlapping_intervals(self):
        self.assertTrue(self.interval_tier1.get_overlapping_intervals(self.interval_tier2) == [tgt.Interval(0.5, 0.7, 'overlap'),
                                                                                               tgt.Interval(2.5, 3.5, 'overlap')])
        self.assertTrue(self.interval_tier2.get_overlapping_intervals(self.interval_tier1) == [tgt.Interval(0.5, 0.7, 'overlap'),
                                                                                               tgt.Interval(2.5, 3.5, 'overlap')])
        self.assertTrue(self.interval_tier2.get_overlapping_intervals(self.interval_tier1, overlap_label='xxx') == [tgt.Interval(0.5, 0.7, 'xxx'),
                                                                                                                    tgt.Interval(2.5, 3.5, 'xxx')])
        self.assertTrue(self.interval_tier1.get_overlapping_intervals(self.interval_tier2, r'^\s*$') == [tgt.Interval(3.5, 5, 'overlap')])
        self.assertTrue(self.interval_tier1.get_overlapping_intervals(self.interval_tier2, r'\d+') == [])
        


        
if __name__ == '__main__':
    unittest.main()
