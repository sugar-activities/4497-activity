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

from specs.utils import human_time_to_py
from specs.utils import py_period
from timelinelib.config.dotfile import Config
from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimeOutOfRangeLeftError
from timelinelib.db.objects import TimeOutOfRangeRightError
from timelinelib.wxgui.components.timelineview import DrawingArea
from timelinelib.wxgui.components.timelineview import DrawingAreaPanel
from timelinelib.wxgui.dialogs.mainframe import StatusBarAdapter


# TODO: testSavesEventAfterMove
# TODO: testSavesEventAfterResize


ANY_Y = 0


class TimelineViewSpec(unittest.TestCase):

    def test_initializes_displayed_period_from_db(self):
        self.init_view_with_db_with_period("1 Aug 2010", "2 Aug 2010")
        self.assert_displays_period("1 Aug 2010", "2 Aug 2010")

    def test_scrolls_timeline_when_dragging_mouse(self):
        self.given_time_at_x_is(0, "1 Aug 2010")
        self.given_time_at_x_is(10, "2 Aug 2010")
        self.init_view_with_db_with_period("11 Aug 2010", "31 Aug 2010")
        self.simulate_mouse_down_move_up((0, ANY_Y), (10, ANY_Y))
        self.assert_displays_period("10 Aug 2010", "30 Aug 2010")

    def test_zooms_timeline_when_shift_dragging_mouse(self):
        self.given_time_at_x_is(0, "1 Aug 2010")
        self.given_time_at_x_is(20, "3 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_down_move_up((0, ANY_Y), (20, ANY_Y), shift_down=True)
        self.assert_displays_period("1 Aug 2010", "3 Aug 2010")

    def test_displays_zoom_intstructions_in_status_bar(self):
        self.init_view_with_db()
        self.controller.left_mouse_down(0, 0, ctrl_down=False, shift_down=True)
        self.assert_displays_status_text(_("Select region to zoom into"))

    def test_displays_period_to_short_message_when_zooming(self):
        self.given_time_at_x_is(0, "1 Aug 2010 00:00")
        self.given_time_at_x_is(1, "1 Aug 2010 00:01")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(1)
        self.assert_displays_status_text(_("Region too short"))

    def test_displays_nothing_if_period_ok_when_zooming(self):
        self.given_time_at_x_is(0, "1 Aug 2010")
        self.given_time_at_x_is(1, "2 Aug 2010")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(1)
        self.assert_displays_status_text("")

    def test_displays_period_to_long_message_when_zooming(self):
        self.given_time_at_x_is(0, "1 Aug 2000")
        self.given_time_at_x_is(200, "1 Aug 4000")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(200)
        self.assert_displays_status_text(_("Region too long"))

    def test_removes_zoom_instructions_when_zoom_done(self):
        self.init_view_with_db()
        self.simulate_mouse_down_move_up((0, ANY_Y), (20, ANY_Y), shift_down=True)
        self.assert_displays_status_text("")

    def test_hightlights_selected_region_while_zooming(self):
        self.given_time_at_x_is(0, "1 Jan 2010")
        self.given_time_at_x_is(1, "1 Jan 2011")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(1)
        self.assert_highlights_region(("1 Jan 2010", "1 Jan 2011"))

    def test_highlights_last_valid_region_while_zooming(self):
        self.given_time_at_x_is(0, "1 Jan 2010")
        self.given_time_at_x_is(1, "1 Jan 2011")
        self.given_time_at_x_is(2000, "1 Jan 4010")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(1)
        self.move_mouse_to_x(2000)
        self.assert_highlights_region(("1 Jan 2010", "1 Jan 2011"))

    def test_highlights_no_region_when_zooming_is_completed(self):
        self.given_time_at_x_is(0, "1 Aug 2010")
        self.given_time_at_x_is(20, "3 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_down_move_up((0, ANY_Y), (20, ANY_Y), shift_down=True)
        self.assert_highlights_region(None)

    def test_zooms_to_last_valid_selection(self):
        self.given_time_at_x_is(0, "1 Jan 2010")
        self.given_time_at_x_is(1, "1 Jan 2011")
        self.given_time_at_x_is(2000, "1 Jan 4010")
        self.init_view_with_db()
        self.start_shift_drag_at_x(0)
        self.move_mouse_to_x(1)
        self.move_mouse_to_x(2000)
        self.release_mouse()
        self.assert_displays_period("1 Jan 2010", "1 Jan 2011")

    def test_centers_displayed_period_around_middle_click_position(self):
        self.given_time_at_x_is(150, "15 Aug 2010")
        self.init_view_with_db_with_period("1 Aug 2010", "11 Aug 2010")
        self.controller.middle_mouse_clicked(150)
        self.assert_displays_period("10 Aug 2010", "20 Aug 2010")

    def test_zooms_timeline_by_10_percent_on_each_side_when_scrolling_while_holding_down_ctrl(self):
        self.init_view_with_db_with_period("1 Aug 2010", "21 Aug 2010")
        self.controller.mouse_wheel_moved(
            1, ctrl_down=True, shift_down=False, x=self.middle_x)
        self.assert_displays_period("3 Aug 2010", "19 Aug 2010")

    def test_displays_balloon_for_event_with_description(self):
        event = self.given_event_with(description="any description", pos=(40, 60), size=(20, 10))
        self.init_view_with_db()
        self.controller.mouse_moved(50, 65)
        self.fire_balloon_show_timer()
        self.assert_balloon_drawn_for_event(event)

    def test_hides_balloon_when_leaving_event(self):
        event = self.given_event_with(description="any description", pos=(40, 60), size=(20, 10))
        self.init_view_with_db()
        self.controller.mouse_moved(50, 65)
        self.fire_balloon_show_timer()
        self.assert_balloon_drawn_for_event(event)
        self.controller.mouse_moved(0, ANY_Y)
        self.fire_balloon_hide_timer()
        self.assert_balloon_drawn_for_event(None)

    def test_creates_event_when_ctrl_dragging_mouse(self):
        self.given_time_at_x_is(10, "1 Aug 2010")
        self.given_time_at_x_is(30, "3 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_down_move_up((10, ANY_Y), (30, ANY_Y), ctrl_down=True)
        self.assert_created_event_with_period("1 Aug 2010", "3 Aug 2010")
        self.assert_timeline_redrawn()

    def test_displays_event_info_in_status_bar_when_hovering_event(self):
        event = self.given_event_with(text="Period event", pos=(40, 60), size=(20, 10))
        self.init_view_with_db()
        self.simulate_mouse_move(50, 65)
        self.assertTrue("Period event" in self.get_status_text())

    def test_removes_event_info_from_status_bar_when_un_hovering_event(self):
        self.init_view_with_db()
        self.simulate_mouse_move(0, ANY_Y)
        self.assertEquals("", self.get_status_text())

    def test_displays_hidden_event_count_in_status_bar(self):
        self.mock_drawer.hidden_event_count = 3
        self.init_view_with_db()
        self.assertTrue("3" in self.get_hidden_event_count_text())

    def test_displays_error_in_status_bar_when_scrolling_too_far_left(self):
        def navigate(time_period):
            raise TimeOutOfRangeLeftError()
        self.init_view_with_db()
        self.controller.navigate_timeline(navigate)
        self.assert_displays_status_text(_("Can't scroll more to the left"))

    def test_displays_error_in_status_bar_when_scrolling_too_far_right(self):
        def navigate(time_period):
            raise TimeOutOfRangeRightError()
        self.init_view_with_db()
        self.controller.navigate_timeline(navigate)
        self.assert_displays_status_text(_("Can't scroll more to the right"))

    def test_creates_event_when_double_clicking_surface(self):
        self.given_time_at_x_is(30, "3 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_double_click(30, ANY_Y)
        self.assert_created_event_with_period("3 Aug 2010", "3 Aug 2010")
        self.assert_timeline_redrawn()

    def test_edits_event_when_double_clicking_it(self):
        event = self.given_event_with(pos=(40, 60), size=(20, 10))
        self.init_view_with_db()
        self.simulate_mouse_double_click(50, 65)
        self.view.open_event_editor_for.assert_called_with(event)
        self.assert_timeline_redrawn()

    def test_selects_and_deselects_event_when_clicking_on_it(self):
        event = self.given_event_with(pos=(30, 60), size=(50, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(40, 65)
        self.assert_is_selected(event)
        self.simulate_mouse_click(40, 65)
        self.assert_is_not_selected(event)

    def test_deselects_event_when_clicking_outside_of_it(self):
        event = self.given_event_with(pos=(30, 60), size=(50, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(50, 65)
        self.assert_is_selected(event)
        self.simulate_mouse_click(0, ANY_Y)
        self.assert_is_not_selected(event)

    def test_selects_multiple_events_when_clicked_if_ctrl_is_pressed(self):
        period_event = self.given_event_with(pos=(30, 60), size=(50, 10))
        point_event = self.given_event_with(pos=(130, 30), size=(50, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(50, 65)
        self.simulate_mouse_click(140, 35, ctrl_down=True)
        self.assert_is_selected(period_event)
        self.assert_is_selected(point_event)

    def test_displays_move_cursor_when_hovering_move_icon_on_event(self):
        event = self.given_event_with(pos=(0, 60), size=(30, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(10, 65)
        self.simulate_mouse_move(10, 65)
        self.assertTrue(self.view.set_move_cursor.called)

    def test_displays_resize_cursor_when_hovering_resize_icons_on_event(self):
        event = self.given_event_with(pos=(30, 60), size=(60, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(50, 65)
        self.simulate_mouse_move(31, 65)
        self.simulate_mouse_move(89, 65)
        self.assertEquals(2, self.view.set_size_cursor.call_count)

    def test_resizes_event_when_dragging_right_drag_icon_on_event(self):
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.given_time_at_x_is(89, "4 Aug 2010")
        self.given_time_at_x_is(109, "11 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_click(50, 60)
        self.simulate_mouse_down_move_up((89, 60), (109, 60))
        self.assert_event_has_period(event, "4 Aug 2010", "11 Aug 2010")
        self.assert_timeline_redrawn()

    def test_resizes_event_when_dragging_left_drag_icon_on_event(self):
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.given_time_at_x_is(31, "4 Aug 2010")
        self.given_time_at_x_is(20, "3 Aug 2010")
        self.init_view_with_db()
        self.simulate_mouse_click(50, 60)
        self.simulate_mouse_down_move_up((31, 60), (20, 60))
        self.assert_event_has_period(event, "3 Aug 2010", "10 Aug 2010")
        self.assert_timeline_redrawn()

    def test_snaps_event_edge_when_resizing_event(self):
        self.given_time_at_x_is(89, "10 Aug 2010")
        self.given_time_at_x_is(120, "13 Aug 2010")
        self.mock_drawer.setup_snap("13 Aug 2010", "27 Aug 2010")
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(50, 60)
        self.simulate_mouse_down_move_up((89, 60), (120, 60))
        self.assert_event_has_period(event, "4 Aug 2010", "27 Aug 2010")
        self.assert_timeline_redrawn()

    def test_snaps_event_when_moving_event(self):
        self.given_time_at_x_is(31, "4 Aug 2010")
        self.given_time_at_x_is(10, "2 Aug 2010")
        self.mock_drawer.setup_snap("2 Aug 2010", "28 Jul 2010")
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.init_view_with_db()
        self.simulate_mouse_click(55, 60)
        self.simulate_mouse_down_move_up((31, 60), (10, 60))
        self.assert_event_has_period(event, "28 Jul 2010", "10 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_moving_event(self):
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.init_view_with_db_with_period("1 Aug 2010", "21 Aug 2010")
        self.simulate_mouse_click(50, 60)
        self.controller.left_mouse_down(65, 60, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(199, 60)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_timeline_by_10_percent_when_resizing_event(self):
        event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 55), size=(60, 10))
        self.init_view_with_db_with_period("1 Aug 2010", "21 Aug 2010")
        self.simulate_mouse_click(50, 60)
        self.controller.left_mouse_down(89, 60, ctrl_down=False, shift_down=False)
        self.controller.mouse_moved(199, 60)
        self.assertTrue(self.view.start_dragscroll_timer.called)
        self.controller.dragscroll_timer_fired()
        self.controller.left_mouse_up()
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()

    def test_scrolls_with_10_percent_when_using_mouse_wheel(self):
        self.init_view_with_db_with_period("1 Aug 2010", "21 Aug 2010")
        self.controller.mouse_wheel_moved(
            -1, ctrl_down=False, shift_down=False, x=self.middle_x)
        self.assert_displays_period("3 Aug 2010", "23 Aug 2010")
        self.assert_timeline_redrawn()
        self.controller.mouse_wheel_moved(
            1, ctrl_down=False, shift_down=False, x=self.middle_x)
        self.assert_displays_period("1 Aug 2010", "21 Aug 2010")
        self.assert_timeline_redrawn()

    def test_deletes_selected_events_when_pressing_del_and_answering_yes_in_dialog(self):
        period_event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 60-5), size=(60, 10))
        point_event = self.given_event_with(start="15 Aug 2010", end="15 Aug 2010", pos=(130, 30-5), size=(50, 10))
        self.init_view_with_db()
        self.view.ask_question.return_value = wx.YES
        self.simulate_mouse_click(50, 60)
        self.controller.key_down(wx.WXK_DELETE, False)
        self.assertEquals([point_event], self.db.get_all_events())

    def test_deletes_no_selected_events_when_pressing_del_and_answering_no_in_dialog(self):
        period_event = self.given_event_with(start="4 Aug 2010", end="10 Aug 2010", pos=(30, 60-5), size=(60, 10))
        point_event = self.given_event_with(start="15 Aug 2010", end="15 Aug 2010", pos=(130, 30-5), size=(50, 10))
        self.init_view_with_db()
        self.view.ask_question.return_value = wx.NO
        self.simulate_mouse_click(50, 60)
        self.controller.key_down(wx.WXK_DELETE, False)
        self.assertTrue(period_event in self.db.get_all_events())
        self.assertTrue(point_event in self.db.get_all_events())

    def test_shift_scroll_changes_divider_line_value_and_redraws(self):
        self.init_view_with_db()
        self.controller.mouse_wheel_moved(
            1, ctrl_down=False, shift_down=True, x=self.middle_x)
        self.assertTrue(self.divider_line_slider.SetValue.called)
        self.assert_timeline_redrawn()

    def test_disables_view_if_no_timeline_set(self):
        self.controller.set_timeline(None)
        self.view.Disable.assert_called_with()

    def setUp(self):
        self.db = MemoryDB()
        self.view = Mock(DrawingAreaPanel)
        self.width = 10
        self.middle_x = self.width / 2
        self.view.GetSizeTuple.return_value = (self.width, 10)
        self.status_bar_adapter = Mock(StatusBarAdapter)
        self.config = Mock(Config)
        self.mock_drawer = MockDrawer()
        self.divider_line_slider = Mock()
        self.divider_line_slider.GetValue.return_value = 50
        self.fn_handle_db_error = Mock()
        self.controller = DrawingArea(
            self.view,
            self.status_bar_adapter,
            self.config,
            self.mock_drawer,
            self.divider_line_slider,
            self.fn_handle_db_error)

    def given_event_with(self, start="4 Aug 2010", end="10 Aug 2010",
                         text="Text", description=None,
                         pos=(0, 0), size=(0, 0)):
        event = Event(self.db.get_time_type(), human_time_to_py(start), human_time_to_py(end), text)
        if description is not None:
            event.set_data("description", description)
        self.db.save_event(event)
        self.mock_drawer.events_and_rects.append((event, wx.Rect(pos[0], pos[1], size[0], size[1])))
        return event

    def given_time_at_x_is(self, x, time):
        self.mock_drawer.setup_get_time_call(x, human_time_to_py(time))

    def init_view_with_db_with_period(self, start, end):
        self.db._set_displayed_period(py_period(start, end))
        self.init_view_with_db()

    def init_view_with_db(self):
        self.controller.set_timeline(self.db)

    def fire_balloon_show_timer(self):
        self.assertTrue(self.view.start_balloon_show_timer.called)
        self.controller.balloon_show_timer_fired()

    def fire_balloon_hide_timer(self):
        self.assertTrue(self.view.start_balloon_hide_timer.called)
        self.controller.balloon_hide_timer_fired()

    def start_shift_drag_at_x(self, x):
        ctrl_down = False
        shift_down = True
        self.controller.left_mouse_down(x, ANY_Y, ctrl_down, shift_down)

    def simulate_mouse_double_click(self, x, y):
        self.simulate_mouse_click(x, y)
        self.controller.left_mouse_dclick(x, y, ctrl_down=False)

    def simulate_mouse_click(self, x, y, ctrl_down=False):
        self.controller.left_mouse_down(x, y, ctrl_down=ctrl_down, shift_down=False)
        self.controller.left_mouse_up()

    def simulate_mouse_down_move_up(self, from_, to, ctrl_down=False, shift_down=False):
        x1, y1 = from_
        x2, y2 = to
        self.controller.left_mouse_down(x1, y1, ctrl_down, shift_down)
        self.controller.mouse_moved(x2, y2)
        self.controller.config.use_inertial_scrolling = False
        self.controller.left_mouse_up()

    def simulate_mouse_move(self, x, y):
        self.controller.mouse_moved(x, y)

    def move_mouse_to_x(self, x):
        self.controller.mouse_moved(x, ANY_Y)

    def release_mouse(self):
        self.controller.left_mouse_up()

    def get_status_text(self):
        self.assertTrue(self.status_bar_adapter.set_text.called)
        text = self.status_bar_adapter.set_text.call_args[0][0]
        return text

    def get_hidden_event_count_text(self):
        self.assertTrue(self.status_bar_adapter.set_hidden_event_count_text.called)
        text = self.status_bar_adapter.set_hidden_event_count_text.call_args[0][0]
        return text

    def assert_event_has_period(self, event, start, end):
        self.assertEquals(py_period(start, end), event.time_period)

    def assert_balloon_drawn_for_event(self, event):
        view_properties = self.get_view_properties_used_when_drawing()
        self.assertEquals(event, view_properties.hovered_event)

    def assert_highlights_region(self, start_end):
        if start_end is not None:
            start_end = (human_time_to_py(start_end[0]), human_time_to_py(start_end[1]))
        view_properties = self.get_view_properties_used_when_drawing()
        self.assertEquals(start_end, view_properties.period_selection)

    def assert_displays_period(self, start, end):
        view_properties = self.get_view_properties_used_when_drawing()
        self.assertEquals(
            py_period(start, end), view_properties.displayed_period)

    def assert_timeline_redrawn(self):
        self.assertTrue(self.view.redraw_surface.called)

    def assert_created_event_with_period(self, start, end):
        self.view.open_create_event_editor.assert_called_with(
            human_time_to_py(start), human_time_to_py(end))

    def assert_is_selected(self, event):
        view_properties = self.get_view_properties_used_when_drawing()
        self.assertTrue(view_properties.is_selected(event))

    def assert_is_not_selected(self, event):
        view_properties = self.get_view_properties_used_when_drawing()
        self.assertFalse(view_properties.is_selected(event))

    def assert_displays_status_text(self, text):
        self.assertEquals(text, self.get_status_text())

    def get_view_properties_used_when_drawing(self):
        self.assertTrue(self.view.redraw_surface.called)
        draw_fn = self.view.redraw_surface.call_args[0][0]
        draw_fn(Mock())
        return self.mock_drawer.draw_view_properties


class MockDrawer(object):

    def __init__(self):
        self.events_and_rects = []
        self.snaps = []
        self.get_time_calls = {}
        self.hidden_event_count = 0

    def use_fast_draw(self, value):
        pass

    def setup_get_time_call(self, x, time):
        self.get_time_calls[x] = time

    def setup_snap(self, time, snap_to):
        self.snaps.append((human_time_to_py(time), human_time_to_py(snap_to)))

    def snap(self, time):
        for (time_inner, snap_to) in self.snaps:
            if time_inner == time:
                return snap_to
        return time

    def snap_selection(self, selection):
        return selection

    def event_at(self, x, y, alt_down=False):
        for (event, rect) in self.events_and_rects:
            if rect.Contains((x, y)):
                return event
        return None

    def event_rect(self, event):
        for (event_inner, rect) in self.events_and_rects:
            if event_inner == event:
                return rect
        raise Exception("Should not get here in tests.")

    def event_with_rect_at(self, x, y, alt_down=False):
        event = self.event_at(x, y)
        if event is None:
            return None
        return (event, self.event_rect(event))

    def get_time(self, x):
        any_time = human_time_to_py("19 Sep 1999")
        return self.get_time_calls.get(x, any_time)

    def balloon_at(self, x, y):
        return None

    def get_hidden_event_count(self):
        return self.hidden_event_count

    def event_is_period(self, event):
        return False

    def draw(self, dc, timeline, view_properties, config):
        self.draw_dc = dc
        self.draw_timeline = timeline
        self.draw_view_properties = view_properties
        self.draw_config = config
