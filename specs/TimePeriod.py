# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


import unittest

from timelinelib.db.objects import TimePeriod
from timelinelib.time.typeinterface import TimeType


class ATime(object):

    def __init__(self, num):
        self.num = num

    # Exists only only to simplify testing
    def __repr__(self):
        return "ATime<%s>" % self.num

    def __eq__(self, other):
        return isinstance(other, ATime) and self.num == other.num

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if isinstance(other, ADelta):
            return ATime(self.num + other.num)
        raise Exception("Only time+delta supported")

    def __sub__(self, other):
        if isinstance(other, ATime):
            return ADelta(self.num - other.num)
        elif isinstance(other, ADelta):
            return ATime(self.num - other.num)
        raise Exception("Only time-time and time-delta supported")

    def __lt__(self, other):
        return self.num < other.num

    def __le__(self, other):
        return self.num <= other.num

    def __gt__(self, other):
        return self.num > other.num

    def __ge__(self, other):
        return self.num >= other.num


class ADelta(object):

    def __init__(self, num):
        self.num = num

    # Exists only only to simplify testing
    def __eq__(self, other):
        return isinstance(other, ADelta) and self.num == other.num

    # Exists only only to simplify testing
    def __ne__(self, other):
        return not (self == other)

    # Exists only only to simplify testing
    def __repr__(self):
        return "ADelta<%s>" % self.num

    def __neg__(self):
        return ADelta(-self.num)

    def __lt__(self, other):
        return self.num < other.num

    def __gt__(self, other):
        return other < self

    def __sub__(self, other):
        if isinstance(other, ADelta):
            return ADelta(self.num - other.num)
        raise Exception("Only delta-delta supported")

    def __rmul__(self, other):
        if isinstance(other, int):
            return ADelta(self.num*other)
        raise Exception("Only int*delta supported")

    def __div__(self, other):
        if isinstance(other, int):
            return ADelta(int(self.num/other))
        raise Exception("Only delta/int supported")


class ATimeType(TimeType):

    def get_min_time(self):
        return (ATime(0), "can't be before 0")

    def get_max_time(self):
        return (ATime(100), "can't be after 100")

    def get_zero_delta(self):
        return ADelta(0)

    def format_period(self, period):
        return "%s to %s" % (period.start_time.num, period.end_time.num)

    def mult_timedelta(self, delta, times):
        return ADelta(int(delta.num * times))

    def get_min_zoom_delta(self):
        return (ADelta(1), "")

    def get_max_zoom_delta(self):
        return (ADelta(100), "")

    def half_delta(self, delta):
        return delta / 2


class time_period_spec(unittest.TestCase):

    def test_creating_period_with_too_small_start_time_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(-1), ATime(5))

    def test_creating_period_with_too_large_end_time_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(0), ATime(150))

    def test_creating_period_with_end_before_start_should_fail(self):
        self.assertRaises(ValueError, TimePeriod,
                          ATimeType(), ATime(50), ATime(10))

    def test_inside_should_return_true_if_time_is_inside_period(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertTrue(tp.inside(ATime(3)))

    def test_inside_should_return_true_if_time_is_on_lower_edge(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertTrue(tp.inside(ATime(0)))

    def test_inside_should_return_true_if_time_is_on_higher_edge(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertTrue(tp.inside(ATime(4)))

    def test_inside_should_return_false_if_time_is_outside_period(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertFalse(tp.inside(ATime(5)))

    def test_delta_should_return_time_specific_delta(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertEquals(ADelta(4), tp.delta())

    def test_mean_time_should_return_time_specific_time(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertEquals(ATime(2), tp.mean_time())

    def test_center_should_center_period_around_time(self):
        tp = TimePeriod(ATimeType(), ATime(0), ATime(4))
        self.assertEquals(
            tp.center(ATime(5)),
            TimePeriod(ATimeType(), ATime(3), ATime(7)))

    def test_center_before_lower_limit_should_make_period_start_there(self):
        tp = TimePeriod(ATimeType(), ATime(10), ATime(14))
        self.assertEquals(
            tp.center(ATime(-5)),
            TimePeriod(ATimeType(), ATime(0), ATime(4)))

    def test_center_after_upper_limit_should_make_period_end_there(self):
        tp = TimePeriod(ATimeType(), ATime(10), ATime(14))
        self.assertEquals(
            tp.center(ATime(200)),
            TimePeriod(ATimeType(), ATime(96), ATime(100)))

    def test_formats_period_using_time_type(self):
        time_period = TimePeriod(ATimeType(), ATime(5), ATime(9))
        self.assertEquals("5 to 9", time_period.get_label())

    def test_move_moves_1_10th_forward(self):
        time_period = TimePeriod(ATimeType(), ATime(0), ATime(10))
        self.assertEquals(
            time_period.move(1),
            TimePeriod(ATimeType(), ATime(1), ATime(11)))

    def test_move_moves_1_10th_backward(self):
        time_period = TimePeriod(ATimeType(), ATime(20), ATime(30))
        self.assertEquals(
            time_period.move(-1),
            TimePeriod(ATimeType(), ATime(19), ATime(29)))

    def test_zoom_in_removes_1_10th_on_each_side(self):
        time_period = TimePeriod(ATimeType(), ATime(10), ATime(20))
        self.assertEquals(
            time_period.zoom(1),
            TimePeriod(ATimeType(), ATime(11), ATime(19)))

    def test_zoom_out_adds_1_10th_on_each_side(self):
        time_period = TimePeriod(ATimeType(), ATime(10), ATime(20))
        self.assertEquals(
            time_period.zoom(-1),
            TimePeriod(ATimeType(), ATime(9), ATime(21)))

    def test_move_delta_moves_the_period_that_delta(self):
        time_period = TimePeriod(ATimeType(), ATime(10), ATime(20))
        self.assertEquals(
            time_period.move_delta(ADelta(-10)),
            TimePeriod(ATimeType(), ATime(0), ATime(10)))
