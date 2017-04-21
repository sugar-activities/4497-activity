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
import wx

from specs.utils import an_event
from specs.utils import an_event_with
from specs.utils import human_time_to_py
from specs.utils import py_period
from timelinelib.view.resize import ResizeByDragInputHandler
from timelinelib.wxgui.components.timelineview import DrawingAreaPanel
from timelinelib.wxgui.components.timelineview import DrawingArea
from timelinelib.wxgui.dialogs.mainframe import StatusBarAdapter


class ResizeEventSpec(unittest.TestCase):

    def test_updates_period_on_event(self):
        self.given_time_at_x_is(50, "31 Aug 2010")
        self.when_resizing(an_event_with(time="1 Jan 2010"), wx.RIGHT)
        self.and_moving_mouse_to_x(50)
        self.then_event_gets_period("1 Jan 2010", "31 Aug 2010")

    def test_indicates_a_too_long_event_in_status_bar(self):
        self.given_time_at_x_is(50, "1 Jan 5000")
        self.when_resizing(an_event_with(time="1 Jan 2000"), wx.RIGHT)
        self.and_moving_mouse_to_x(50)
        self.assertEquals(1, self.status_bar.set_text.call_count)

    def test_clears_status_message_if_resize_is_valid(self):
        self.given_time_at_x_is(50, "2 Jan 2000")
        self.when_resizing(an_event_with(time="1 Jan 2000"), wx.RIGHT)
        self.and_moving_mouse_to_x(50)
        self.status_bar.set_text.assert_called_with("")

    def test_clears_status_message_when_resize_is_done(self):
        self.when_resizing(an_event(), wx.RIGHT)
        self.resizer.left_mouse_up()
        self.status_bar.set_text.assert_called_with("")

    def test_changes_input_handler_when_resize_is_done(self):
        self.when_resizing(an_event(), wx.RIGHT)
        self.resizer.left_mouse_up()
        self.assertEquals(1, self.controller.change_input_handler_to_no_op.call_count)

    def setUp(self):
        self.drawer = Mock()
        self.controller = Mock(DrawingArea)
        self.controller.timeline = None
        self.controller.view = Mock(DrawingAreaPanel)
        self.controller.get_drawer.return_value = self.drawer
        self.status_bar = Mock(StatusBarAdapter)

    def given_time_at_x_is(self, x, time):
        self.controller.get_time.return_value = human_time_to_py(time)
        self.drawer.snap.return_value = human_time_to_py(time)

    def when_resizing(self, event, direction):
        self.event_being_resized = event
        self.resizer = ResizeByDragInputHandler(
            self.controller, self.status_bar, event, direction)

    def and_moving_mouse_to_x(self, x):
        any_y = 10
        self.resizer.mouse_moved(x, any_y)

    def then_event_gets_period(self, start, end):
        self.assertEquals(
            py_period(start, end),
            self.event_being_resized.time_period)
