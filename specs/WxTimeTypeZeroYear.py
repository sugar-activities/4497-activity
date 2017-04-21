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


import platform

import unittest

import wx

from timelinelib.time import WxTimeType
from timelinelib.time import try_to_create_wx_date_time_from_dmy
from timelinelib.db.objects import TimePeriod


class WxTimeTypeZeroYearSpec(unittest.TestCase):

    def setUp(self):
        self.time_type = WxTimeType()

    def test_time_string_method(self):
        time1 = wx.DateTimeFromDMY(20,11, 0, 0, 0)
        time2 = wx.DateTimeFromDMY(20,11, 1, 0, 0)
        delta = time2 - time1
        self.assertEqual(365, delta.GetDays())
        self.assertEqual(u"0000-12-20", time1.FormatISODate())
        self.assertEqual(-1, time1.ConvertYearToBC(time1.GetYear()))
        

