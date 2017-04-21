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


import datetime
import unittest

from timelinelib.db.objects import TimePeriod
from timelinelib.time import PyTimeType


class PyTimeTypeSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = PyTimeType()

    def test_converts_time_to_string(self):
        self.assertEquals(
            "2010-8-31 13:44:0",
            self.time_type.time_string(datetime.datetime(2010, 8, 31, 13, 44)))

    def test_parses_time_from_string(self):
        self.assertEquals(
            datetime.datetime(2010, 8, 31, 13, 44),
            self.time_type.parse_time("2010-8-31 13:44:0"))

    def test_raises_ValueError_when_parsing_invalid_time(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-31 0:0:0")

    def test_raises_ValueError_when_parsing_badly_formatted_time(self):
        self.assertRaises(
            ValueError,
            self.time_type.parse_time, "2010-31-hello 0:0:0")

    def test_formats_period_to_string(self):
        time_period = TimePeriod(self.time_type,
                                 datetime.datetime(2010, 8, 01, 13, 44),
                                 datetime.datetime(2010, 8, 02, 13, 30))
        self.assertEquals(
            u"1 %s 2010 13:44 to 2 %s 2010 13:30" % (_("Aug"), _("Aug")),
            self.time_type.format_period(time_period))

    def test_returns_min_time(self):
        self.assertEquals(datetime.datetime(10, 1, 1),
                          self.time_type.get_min_time()[0])

    def test_returns_max_time(self):
        self.assertEquals(datetime.datetime(9990, 1, 1),
                          self.time_type.get_max_time()[0])

    def test_returns_half_delta(self):
        delta = datetime.timedelta(days=4)
        half_delta = self.time_type.half_delta(delta)
        self.assertEquals(datetime.timedelta(days=2), half_delta)

    def test_returns_margin_delta(self):
        delta = datetime.timedelta(days=48)
        margin_delta = self.time_type.margin_delta(delta)
        self.assertEquals(datetime.timedelta(days=2), margin_delta)

    def test_event_date_string_method(self):
        self.assertEquals(
            "2010-08-01",
            self.time_type.event_date_string(datetime.datetime(2010, 8, 1, 13, 44, 22)))

    def test_event_time_string_method(self):
        self.assertEquals(
            "13:44",
            self.time_type.event_time_string(datetime.datetime(2010, 8, 01, 13, 44,22)))

    def test_eventtimes_equals_method_when_equals(self):
        self.assertTrue(
            self.time_type.eventtimes_equals(datetime.datetime(2010, 8, 01, 13, 44, 22),
                                             datetime.datetime(2010, 8, 01, 13, 44, 00)))

    def test_eventtimes_equals_method_when_not_equals(self):
        self.assertFalse(
            self.time_type.eventtimes_equals(datetime.datetime(2010, 8, 01, 13, 44, 22),
                                             datetime.datetime(2010, 7, 01, 13, 44, 22)))

class PyTimeTypeDeltaFormattingSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = PyTimeType()

    def test_format_delta_method(self):
        time_period1 = TimePeriod(self.time_type,
                                  datetime.datetime(2010, 8, 01, 13, 44),
                                  datetime.datetime(2010, 8, 01, 13, 44))
        time_period2 = TimePeriod(self.time_type,
                                  datetime.datetime(2010, 8, 02, 13, 44),
                                  datetime.datetime(2010, 8, 02, 13, 44))
        delta = time_period2.start_time - time_period1.start_time
        self.assertEquals(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=1)
        self.assertEquals(u"1 %s" % _("minute"), self.time_type.format_delta(delta))

    def test_format_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=0, minutes=2)
        self.assertEquals(u"2 %s" % _("minutes"), self.time_type.format_delta(delta))

    def test_format_one_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=0)
        self.assertEquals(u"1 %s" % _("hour"), self.time_type.format_delta(delta))

    def test_format_two_hour_delta(self):
        delta = self.get_days_delta(days=0, hours=2, minutes=0)
        self.assertEquals(u"2 %s" % _("hours"), self.time_type.format_delta(delta))

    def test_format_one_day_delta(self):
        delta = self.get_days_delta(days=1, hours=0, minutes=0)
        self.assertEquals(u"1 %s" % _("day"), self.time_type.format_delta(delta))

    def test_format_two_days_delta(self):
        delta = self.get_days_delta(days=2, hours=0, minutes=0)
        self.assertEquals(u"2 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_one_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=1)
        self.assertEquals(u"1 %s 1 %s" % (_("hour"), _("minute")), self.time_type.format_delta(delta))

    def test_format_one_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=0, hours=1, minutes=2)
        self.assertEquals(u"1 %s 2 %s" % (_("hour"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_one_day_one_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=1, minutes=0)
        self.assertEquals(u"1 %s 1 %s" % (_("day"), _("hour")), self.time_type.format_delta(delta))

    def test_format_one_day_two_hour_delta(self):
        delta = self.get_days_delta(days=1, hours=2, minutes=0)
        self.assertEquals(u"1 %s 2 %s" % (_("day"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=0)
        self.assertEquals(u"2 %s 2 %s" % (_("days"), _("hours")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_one_minute_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=1)
        self.assertEquals(u"2 %s 2 %s 1 %s" % (_("days"), _("hours"), _("minute")), self.time_type.format_delta(delta))

    def test_format_two_days_two_hour_two_minutes_delta(self):
        delta = self.get_days_delta(days=2, hours=2, minutes=2)
        self.assertEquals(u"2 %s 2 %s 2 %s" % (_("days"), _("hours"), _("minutes")), self.time_type.format_delta(delta))

    def test_format_hundred_days_one_minute_delta(self):
        delta = self.get_days_delta(days=100, hours=0, minutes=0)
        self.assertEquals(u"100 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_2_years_2_months(self):
        time_period1 = self.create_point_period(1, 1, 1999, 0, 0)
        time_period2 = self.create_point_period(1, 3, 2001, 0, 0)
        delta = time_period2.start_time - time_period1.start_time
        self.assertEquals(u"790 %s" % _("days"), self.time_type.format_delta(delta))

    def test_format_overlapping_events(self):
        time_period1 = TimePeriod(self.time_type,
                                  datetime.datetime(2010, 8, 01, 13, 44),
                                  datetime.datetime(2010, 8, 03, 13, 44))
        time_period2 = TimePeriod(self.time_type,
                                  datetime.datetime(2010, 8, 01, 13, 44),
                                  datetime.datetime(2010, 8, 03, 13, 44))
        delta = time_period2.start_time - time_period1.end_time
        self.assertEquals("0", self.time_type.format_delta(delta))

    def  get_days_delta(self, days=0, hours=0, minutes=0):
        def add_mars(month, days):
            if days >= 31:
                month = 4
                days = days - 31
                month, days = add_mars(month,days)
            return month, days
        def add_february(month, days):
            if days >= 28:
                month = 3
                days = days - 28
                month, days = add_mars(month,days)
            return month, days
        def add_january(month, days):
            if days >= 31:
                month = 2
                days = days - 31
                month, days = add_february(month, days)
            return month, days
        month = 1
        month, days = add_january(month, days)
        time_period1 = self.create_point_period(1, 1, 1999, 0, 0)
        time_period2 = self.create_point_period(1 + days, month, 1999, hours, minutes)
        return time_period2.start_time - time_period1.start_time

    def create_point_period(self, day, month, year, hour, minute):
        dt = datetime.datetime(year, month, day, hour, minute)
        return TimePeriod(self.time_type, dt, dt)
