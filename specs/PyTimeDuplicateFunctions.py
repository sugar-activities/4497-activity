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
import datetime

from mock import Mock

from timelinelib.db.objects import TimePeriod
from timelinelib.time import PyTimeType
from timelinelib.time.pytime import move_period_num_days
from timelinelib.time.pytime import move_period_num_weeks
from timelinelib.time.pytime import move_period_num_months
from timelinelib.time.pytime import move_period_num_years


class PyTimeDuplicateFunctionsSpec(unittest.TestCase):

    def setUp(self):
        self.period = TimePeriod(
            PyTimeType(),
            datetime.datetime(2010, 1, 1, 12, 0, 0),
            datetime.datetime(2010, 1, 1, 13, 0, 0))

    def test_move_period_num_days_adds_given_number_of_days(self):
        new_period = move_period_num_days(self.period, 6)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2010, 1, 7, 12, 0, 0),
                datetime.datetime(2010, 1, 7, 13, 0, 0)),
            new_period)

    def test_move_period_num_weeks_adds_given_number_of_weeks(self):
        new_period = move_period_num_weeks(self.period, -3)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2009, 12, 11, 12, 0, 0),
                datetime.datetime(2009, 12, 11, 13, 0, 0)),
            new_period)

    def test_move_period_num_months_adds_given_number_of_months(self):
        new_period = move_period_num_months(self.period, 2)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2010, 3, 1, 12, 0, 0),
                datetime.datetime(2010, 3, 1, 13, 0, 0)),
            new_period)

    def test_move_period_num_months_can_handle_year_boundries_up(self):
        new_period = move_period_num_months(self.period, 20)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2011, 9, 1, 12, 0, 0),
                datetime.datetime(2011, 9, 1, 13, 0, 0)),
            new_period)

    def test_move_period_num_months_can_handle_year_boundries_down(self):
        new_period = move_period_num_months(self.period, -1)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2009, 12, 1, 12, 0, 0),
                datetime.datetime(2009, 12, 1, 13, 0, 0)),
            new_period)

    def test_move_period_num_months_returns_none_if_day_does_not_exist(self):
        self.period = TimePeriod(
            PyTimeType(),
            datetime.datetime(2010, 1, 31, 12, 0, 0),
            datetime.datetime(2010, 1, 31, 13, 0, 0))
        new_period = move_period_num_months(self.period, 1)
        self.assertEquals(None, new_period)

    def test_move_period_num_years_adds_given_number_of_years(self):
        new_period = move_period_num_years(self.period, 1)
        self.assertEquals(
            TimePeriod(
                PyTimeType(),
                datetime.datetime(2011, 1, 1, 12, 0, 0),
                datetime.datetime(2011, 1, 1, 13, 0, 0)),
            new_period)

    def test_move_period_num_years_returns_none_if_year_does_not_exist(self):
        self.period = TimePeriod(
            PyTimeType(),
            datetime.datetime(2012, 2, 29, 12, 0, 0),
            datetime.datetime(2012, 2, 29, 13, 0, 0))
        new_period = move_period_num_years(self.period, 1)
        self.assertEquals(None, new_period)
