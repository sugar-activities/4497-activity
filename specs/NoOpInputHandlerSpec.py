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

from specs.utils import an_event, an_event_with, human_time_to_py
from timelinelib.view.drawingarea import DrawingArea
from timelinelib.view.noop import NoOpInputHandler
from timelinelib.wxgui.components.timelineview import DrawingAreaPanel


class NoOpInputHandlerSpec(unittest.TestCase):

    def test_changes_input_handler_to_move_when_pressing_move_handle(self):
        event = an_event()
        time = human_time_to_py("1 Jan 2011")
        self.given_time_at_x_is(10, time)
        self.given_event_with_rect_at(10, 10, event, wx.Rect(0, 0, 20, 20))
        self.given_event_selected(event)
        self.handler.left_mouse_down(10, 10, False, False)
        self.drawing_area.change_input_handler_to_move_by_drag.assert_called_once_with(event, time)

    def test_disables_move_handler_when_event_ends_today(self):
        event = an_event_with(ends_today=True)
        time = human_time_to_py("1 Jan 2011")
        self.given_time_at_x_is(10, time)
        self.given_event_with_rect_at(10, 10, event, wx.Rect(0, 0, 20, 20))
        self.given_event_selected(event)
        self.handler.left_mouse_down(10, 10, False, False)
        self.assertEquals(0, self.drawing_area.change_input_handler_to_move_by_drag.call_count)

    def test_disables_mouse_cursor_when_event_ends_today(self):
        event = an_event_with(ends_today=True)
        time = human_time_to_py("1 Jan 2011")
        self.given_time_at_x_is(10, time)
        self.given_event_with_rect_at(10, 10, event, wx.Rect(0, 0, 20, 20))
        self.given_event_selected(event)
        self.handler.mouse_moved(10, 10)
        self.assertEquals(0, self.view.set_move_cursor.call_count)

    def setUp(self):
        self.setup_drawing_area_mock()
        self.view = Mock(DrawingAreaPanel)
        self.handler = NoOpInputHandler(self.drawing_area, self.view)

    def setup_drawing_area_mock(self):
        self.times_at = {}
        self.events_at = {}
        self.selected_events = []
        self.drawing_area = Mock(DrawingArea)
        self.drawing_area.drawing_algorithm = Mock()
        self.drawing_area.view_properties = Mock()
        self.drawing_area.get_time.side_effect = lambda x: self.times_at[x]
        self.drawing_area.event_with_rect_at.side_effect = lambda x, y, alt: self.events_at[(x, y)]
        self.drawing_area.event_at.side_effect = lambda x, y, alt: self.events_at[(x, y)][0]
        self.drawing_area.is_selected.side_effect = lambda event: event in self.selected_events

    def given_time_at_x_is(self, x, time):
        self.times_at[x] = time

    def given_event_with_rect_at(self, x, y, event, rect):
        self.events_at[(x, y)] = (event, rect)

    def given_event_selected(self, event):
        self.selected_events.append(event)
