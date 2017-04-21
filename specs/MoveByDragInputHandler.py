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

from specs.utils import an_event_with, human_time_to_py, py_period
from timelinelib.view.drawingarea import DrawingArea
from timelinelib.view.move import MoveByDragInputHandler
from timelinelib.wxgui.dialogs.mainframe import StatusBarAdapter


class MoveByDragInputHandlerSpec(unittest.TestCase):

    def test_moves_point_events(self):
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(self.a_point_event("1 Jan 2011"),
                         from_time="1 Jan 2011", to_x=50)
        self.assert_event_has_period("5 Jan 2011", "5 Jan 2011")

    def test_moves_period_events(self):
        self.given_no_snap()
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(self.a_period_event("1 Jan 2011", "3 Jan 2011"),
                         from_time="3 Jan 2011", to_x=50)
        self.assert_event_has_period("3 Jan 2011", "5 Jan 2011")

    def test_snaps_period_events_to_the_left(self):
        self.given_snaps("3 Jan 2011", "4 Jan 2011")
        self.given_snaps("4 Jan 2011", "6 Jan 2011")
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(self.a_period_event("1 Jan 2011", "2 Jan 2011"),
                         from_time="3 Jan 2011", to_x=50)
        self.assert_event_has_period("4 Jan 2011", "5 Jan 2011")

    def test_snaps_period_events_to_the_right(self):
        self.given_snaps("3 Jan 2011", "3 Jan 2011")
        self.given_snaps("4 Jan 2011", "6 Jan 2011")
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(self.a_period_event("1 Jan 2011", "2 Jan 2011"),
                         from_time="3 Jan 2011", to_x=50)
        self.assert_event_has_period("5 Jan 2011", "6 Jan 2011")

    def test_moves_all_selected_events(self):
        event_1 = self.a_point_event("1 Jan 2011")
        event_2 = self.a_point_event("2 Jan 2011")
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(event_1, from_time="1 Jan 2011", to_x=50)
        self.assert_event_has_period("5 Jan 2011", "5 Jan 2011", event_1)
        self.assert_event_has_period("6 Jan 2011", "6 Jan 2011", event_2)

    def test_moves_no_events_if_one_is_locked(self):
        event_1 = self.a_point_event("1 Jan 2011")
        event_2 = self.a_point_event("2 Jan 2011")
        event_2.locked = True
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(event_1, from_time="1 Jan 2011", to_x=50)
        self.assert_event_has_period("1 Jan 2011", "1 Jan 2011", event_1)
        self.assert_event_has_period("2 Jan 2011", "2 Jan 2011", event_2)

    def test_informs_user_through_status_text_why_locked_events_cant_be_moved(self):
        event_1 = self.a_point_event("1 Jan 2011")
        event_2 = self.a_point_event("2 Jan 2011")
        event_2.locked = True
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(event_1, from_time="1 Jan 2011", to_x=50)
        self.assertTrue(self.status_bar.set_text.called)

    def test_clears_status_text_when_done_moving(self):
        self.when_move_done()
        self.status_bar.set_text.assert_called_with("")

    def test_redraws_timeline_after_move(self):
        self.given_time_at_x_is(50, "5 Jan 2011")
        self.when_moving(self.a_point_event("1 Jan 2011"),
                         from_time="1 Jan 2011", to_x=50)
        self.assertTrue(self.drawing_area.redraw_timeline.called)

    def setUp(self):
        self.times_at = {}
        self.period_events = []
        self.snap_times = {}
        self.selected_events = []
        self.drawing_area = Mock(DrawingArea)
        self.drawing_area.timeline = None
        self.drawing_area.view = Mock()
        self.drawing_area.get_time.side_effect = lambda x: self.times_at[x]
        self.drawing_area.event_is_period.side_effect = lambda event: event in self.period_events
        self.drawing_area.snap.side_effect = lambda time: self.snap_times[time]
        self.drawing_area.get_selected_events.return_value = self.selected_events
        self.status_bar = Mock(StatusBarAdapter)

    def a_point_event(self, time):
        event = an_event_with(time=time)
        self.selected_events.append(event)
        return event

    def a_period_event(self, start, end):
        event = an_event_with(start=start, end=end)
        self.selected_events.append(event)
        return event

    def given_snaps(self, from_, to):
        self.snap_times[human_time_to_py(from_)] = human_time_to_py(to)

    def given_no_snap(self):
        self.drawing_area.snap.side_effect = lambda x: x

    def given_time_at_x_is(self, x, time):
        self.times_at[x] = human_time_to_py(time)

    def when_moving(self, event, from_time, to_x):
        self.moved_event = event
        if event.is_period():
            self.period_events.append(event)
        handler = MoveByDragInputHandler(
            self.drawing_area, self.status_bar, event, human_time_to_py(from_time))
        handler.mouse_moved(to_x, 10)

    def when_move_done(self):
        handler = MoveByDragInputHandler(
            self.drawing_area, self.status_bar, self.a_point_event("1 Jan 2011"), None)
        handler.left_mouse_up()

    def assert_event_has_period(self, start, end, event=None):
        if event is None:
            event = self.selected_events[0]
        self.assertEquals(event.time_period, py_period(start, end))
