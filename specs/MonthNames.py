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

import timelinelib.calendar.monthnames


class MonthNamesSpec(unittest.TestCase):

    def test_english_name_for_month_1_should_be_january(self):
        self.assertEquals(
            "January",
            timelinelib.calendar.monthnames.english_name_of_month(1))

    def test_abbreviated_name_for_month_1_should_be_jan_translated(self):
        self.assertEquals(
            _("Jan"),
            timelinelib.calendar.monthnames.abbreviated_name_of_month(1))

    def test_month_from_english_name_january_should_be_1(self):
        self.assertEquals(
            1,
            timelinelib.calendar.monthnames.month_from_english_name("January"))

    def test_english_name_for_month_12_should_be_december(self):
        self.assertEquals(
            "December",
            timelinelib.calendar.monthnames.english_name_of_month(12))

    def test_abbreviated_name_for_month_12_should_be_dec_translated(self):
        self.assertEquals(
            _("Dec"),
            timelinelib.calendar.monthnames.abbreviated_name_of_month(12))

    def test_month_from_english_name_december_should_be_12(self):
        self.assertEquals(
            12,
            timelinelib.calendar.monthnames.month_from_english_name("December"))
