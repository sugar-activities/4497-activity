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

from mock import Mock

from specs.utils import py_period
from timelinelib.db.objects import TimeOutOfRangeLeftError
from timelinelib.db.objects import TimeOutOfRangeRightError
from timelinelib.time.pytime import backward_fn
from timelinelib.time.pytime import fit_century_fn
from timelinelib.time.pytime import fit_week_fn
from timelinelib.time.pytime import fit_day_fn
from timelinelib.time.pytime import fit_decade_fn
from timelinelib.time.pytime import fit_millennium_fn
from timelinelib.time.pytime import fit_month_fn
from timelinelib.time.pytime import fit_year_fn
from timelinelib.time.pytime import forward_fn
from timelinelib.wxgui.dialogs.mainframe import MainFrame


class PyTimeNavigationFunctionsSpec(unittest.TestCase):

    def test_fit_week_should_display_the_week_of_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_week_fn, "30 Oct 2012", "13 Nov 2012")
        self.then_period_becomes("5 Nov 2012", "12 Nov 2012")

    def test_fit_week_sunday_start_should_display_the_week_of_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_week_fn, "30 Oct 2012", "13 Nov 2012", False)
        self.then_period_becomes("4 Nov 2012", "11 Nov 2012")

    def test_fit_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "1 Jan 2010", "4 Jan 2010")
        self.then_period_becomes("2 Jan 2010", "3 Jan 2010")

    def test_fit_first_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "2 Jan 10")

    def test_fit_last_day_should_display_the_day_that_is_in_the_center(self):
        self.when_navigating(fit_day_fn, "31 Dec 9989", "1 Jan 9990")
        self.then_period_becomes("31 Dec 9989", "1 Jan 9990")

    def test_fit_month_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Feb 2010")

    def test_fit_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Dec 2010", "2 Dec 2010")
        self.then_period_becomes("1 Dec 2010", "1 Jan 2011")

    def test_fit_first_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Feb 10")

    def test_fit_last_month_december_should_display_the_month_that_is_in_the_center(self):
        self.when_navigating(fit_month_fn, "1 Dec 9989", "1 Jan 9990")
        self.then_period_becomes("1 Dec 9989", "1 Jan 9990")

    def test_fit_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2011")

    def test_fit_first_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Jan 11")

    def test_fit_last_year_should_display_the_year_that_is_in_the_center(self):
        self.when_navigating(fit_year_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9989", "1 Jan 9990")

    def test_fit_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2020")

    def test_fit_first_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Jan 20")

    def test_fit_last_decade_should_display_the_decade_that_is_in_the_center(self):
        self.when_navigating(fit_decade_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9980", "1 Jan 9990")

    def test_fit_century_should_display_the_century_that_is_in_the_center(self):
        self.when_navigating(fit_century_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2000", "1 Jan 2100")

    def test_fit_first_century_should_display_the_century_that_is_in_the_center(self):
        self.when_navigating(fit_century_fn, "1 Jan 10", "1 Jan 11")
        self.then_period_becomes("1 Jan 10", "1 Jan 110")

    def test_fit_last_century_should_display_the_century_that_is_in_the_center(self):
        self.when_navigating(fit_century_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 9890", "1 Jan 9990")

    def test_fit_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan 2010", "2 Jan 2010")
        self.then_period_becomes("1 Jan 2000", "1 Jan 3000")

    def test_fit_first_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan 10", "2 Jan 10")
        self.then_period_becomes("1 Jan 10", "1 Jan 1010")

    def test_fit_last_millennium_should_display_the_millennium_that_is_in_the_center(self):
        self.when_navigating(fit_millennium_fn, "1 Jan 9989", "1 Jan 9990")
        self.then_period_becomes("1 Jan 8990", "1 Jan 9990")

    def test_move_page_smart_not_smart_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "5 Jan 2010")
        self.then_period_becomes("5 Jan 2010", "9 Jan 2010")

    def test_move_page_smart_not_smart_backward(self):
        self.when_navigating(backward_fn, "5 Jan 2010", "9 Jan 2010")
        self.then_period_becomes("1 Jan 2010", "5 Jan 2010")

    def test_move_page_smart_month_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "1 Feb 2010")
        self.then_period_becomes("1 Feb 2010", "1 Mar 2010")

    def test_move_page_smart_month_forward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeRightError, forward_fn, "1 Jan 9000", "1 Dec 9989")

    def test_move_page_smart_month_backward(self):
        self.when_navigating(backward_fn, "1 Feb 2010", "1 Mar 2010")
        self.then_period_becomes("1 Jan 2010", "1 Feb 2010")

    def test_move_page_smart_month_backward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeLeftError, backward_fn, "1 Jan 11", "1 Dec 25")

    def test_move_page_smart_month_over_year_boundry_backward(self):
        self.when_navigating(backward_fn, "1 Jan 2010", "1 Mar 2010")
        self.then_period_becomes("1 Nov 2009", "1 Jan 2010")

    def test_move_page_smart_year_forward(self):
        self.when_navigating(forward_fn, "1 Jan 2010", "1 Jan 2011")
        self.then_period_becomes("1 Jan 2011", "1 Jan 2012")

    def test_move_page_smart_year_forward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeRightError, forward_fn, "1 Jan 9000", "1 Jan 9989")

    def test_move_page_smart_year_backward(self):
        self.when_navigating(backward_fn, "1 Jan 2011", "1 Jan 2012")
        self.then_period_becomes("1 Jan 2010", "1 Jan 2011")

    def test_move_page_smart_year_backward_beyond_limit(self):
        self.assert_navigation_raises(
            TimeOutOfRangeLeftError, backward_fn, "1 Jan 100", "1 Jan 1000")

    def assert_navigation_raises(self, exception, fn, start, end):
        def navigation_fn(fn):
            self.assertRaises(exception, fn, self.time_period)
        self.time_period = py_period(start, end)
        fn(None, self.time_period, navigation_fn)

    def when_navigating(self, fn, start, end, week_starts_on_monday=True):
        def navigation_fn(fn):
            self.new_period = fn(self.time_period)
        self.time_period = py_period(start, end)
        main_frame = Mock(MainFrame)
        main_frame.week_starts_on_monday.return_value = week_starts_on_monday
        fn(main_frame, self.time_period, navigation_fn)

    def then_period_becomes(self, start, end):
        self.assertEquals(py_period(start, end), self.new_period)
