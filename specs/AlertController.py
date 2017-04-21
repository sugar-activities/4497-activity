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
import wx

from specs.utils import an_event
from timelinelib.time.pytime import PyTimeType
from timelinelib.time.wxtime import WxTimeType
from timelinelib.wxgui.dialogs.mainframe import AlertController

class AlertControllerSpec(unittest.TestCase):

    def test_alert_text_formatting(self):
        text = self.controller._format_alert_text(self.alert, self.event)
        expected_text = "Trigger time: %s\n\nEvent: %s\n\nTime to go" % (self.now, self.event.get_label())
        self.assertEqual(expected_text, text)


    def test_pytime_has_expired(self):
        self.given_early_pytimes()
        self.given_controller_time_type(PyTimeType())
        time_as_text = "%s" % self.tm
        expired = self.controller._time_has_expired(self.tm)
        self.assertTrue(expired)

    def test_pytime_has_not_expired(self):
        self.given_late_pytimes()
        expired = self.controller._time_has_expired(self.tm)
        self.assertFalse(expired)

    def test_wxtime_has_expired(self):
        self.given_early_wxtimes()
        self.given_controller_time_type(WxTimeType())
        expired = self.controller._time_has_expired(self.tm)
        self.assertTrue(expired)

    def test_wxtime_has_not_expired(self):
        self.given_late_wxtimes()
        self.given_controller_time_type(WxTimeType())
        expired = self.controller._time_has_expired(self.tm)
        self.assertFalse(expired)

    def given_early_pytimes(self):
        self.given_pytime_now()
        self.given_pytime_earlier()
        self.given_controller_time_type(PyTimeType())
        self.alert = (self.now, "Time to go")

    def given_late_pytimes(self):
        self.given_pytime_now()
        self.given_pytime_later()
        self.given_controller_time_type(PyTimeType())
        self.alert = (self.now, "Time to go")

    def given_early_wxtimes(self):
        self.given_wxtime_now()
        self.given_wxtime_earlier()
        self.given_controller_time_type(WxTimeType())
        self.alert = (self.now, "Time to go")

    def given_late_wxtimes(self):
        self.given_wxtime_now()
        self.given_wxtime_later()
        self.given_controller_time_type(WxTimeType())
        self.alert = (self.now, "Time to go")

    def given_wxtime_now(self):
        self.now = WxTimeType().now()

    def given_wxtime_later(self):
        self.tm = self.now + wx.TimeSpan(hours=12)

    def given_wxtime_earlier(self):
        self.tm = self.now - wx.TimeSpan(hours=12)

    def given_pytime_now(self):
        self.now = PyTimeType().now()

    def given_pytime_later(self):
        self.tm = self.now + datetime.timedelta(days=1)

    def given_pytime_earlier(self):
        self.tm = self.now + datetime.timedelta(days=-1)

    def given_controller_time_type(self, time_type):
        self.controller.time_type = time_type

    def setUp(self):
        self.now = PyTimeType().now()
        self.alert = (self.now, "Time to go")
        self.event = an_event()
        self.controller = AlertController()
