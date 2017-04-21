# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015  Rickard Lindberg, Roger Lindberg
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


import wx

from timelinelib.wxgui.components.canvas.inputhandler import InputHandler


# Used by Sizer and Mover classes to detect when to go into action
HIT_REGION_PX_WITH = 5


class NoOpInputHandler(InputHandler):

    def __init__(self, timeline_canvas_controller, timeline_canvas):
        self.timeline_canvas_controller = timeline_canvas_controller
        self.timeline_canvas = timeline_canvas
        self.drawer = timeline_canvas_controller.drawing_algorithm
        self.view_properties = timeline_canvas_controller.view_properties
        self.show_timer_running = False
        self.hide_timer_running = False
        self.last_hovered_event = None
        self.last_hovered_balloon_event = None

    def left_mouse_down(self, x, y, ctrl_down, shift_down, alt_down=False):
        self._toggle_balloon_stickyness(x, y)
        event = self.timeline_canvas_controller.event_at(x, y, alt_down)
        time_at_x = self.timeline_canvas_controller.get_time(x)
        if self._hit_resize_handle(x, y, alt_down) is not None:
            if self.timeline_canvas.ok_to_edit():
                try:
                    direction = self._hit_resize_handle(x, y, alt_down)
                    self.timeline_canvas_controller.change_input_handler_to_resize_by_drag(event, direction)
                except:
                    self.timeline_canvas.edit_ends()
                    raise
            return
        if self._hit_move_handle(x, y, alt_down) and not event.get_ends_today():
            if self.timeline_canvas.ok_to_edit():
                try:
                    self.timeline_canvas_controller.change_input_handler_to_move_by_drag(event, time_at_x)
                except:
                    self.timeline_canvas.edit_ends()
                    raise
            return
        if (event is None and ctrl_down is False and shift_down is False):
            self.timeline_canvas_controller._toggle_event_selection(x, y, ctrl_down)
            self.timeline_canvas_controller.change_input_handler_to_scroll_by_drag(time_at_x)
            return
        if (event is None and ctrl_down is True):
            self.timeline_canvas_controller._toggle_event_selection(x, y, ctrl_down)
            self.timeline_canvas_controller.change_input_handler_to_create_period_event_by_drag(time_at_x)
            return
        if (event is None and shift_down is True):
            self.timeline_canvas_controller._toggle_event_selection(x, y, ctrl_down)
            self.timeline_canvas_controller.change_input_handler_to_zoom_by_drag(time_at_x)
            return
        self.timeline_canvas_controller._toggle_event_selection(x, y, ctrl_down, alt_down)

    def _toggle_balloon_stickyness(self, x, y):
        event_with_balloon = self.drawer.balloon_at(x, y)
        if event_with_balloon:
            stick = not self.view_properties.event_has_sticky_balloon(event_with_balloon)
            self.view_properties.set_event_has_sticky_balloon(event_with_balloon, has_sticky=stick)
            if stick:
                self.timeline_canvas_controller._redraw_timeline()
            else:
                if self.view_properties.show_balloons_on_hover:
                    self.timeline_canvas_controller._redraw_balloons(event_with_balloon)
                else:
                    self.timeline_canvas_controller._redraw_balloons(None)

    def mouse_moved(self, x, y, alt_down=False):
        self.last_hovered_event = self.timeline_canvas_controller.event_at(x, y, alt_down)
        self.last_hovered_balloon_event = self.drawer.balloon_at(x, y)
        self._start_balloon_timers()
        self.timeline_canvas_controller._display_eventinfo_in_statusbar(x, y, alt_down)
        if self._hit_resize_handle(x, y, alt_down) is not None:
            self.timeline_canvas.set_size_cursor()
        elif self._hit_move_handle(x, y, alt_down) and not self.last_hovered_event.get_ends_today():
            self.timeline_canvas.set_move_cursor()
        else:
            self.timeline_canvas.set_default_cursor()

    def _start_balloon_timers(self):
        if self._balloons_disabled():
            return
        if self._current_event_selected():
            return
        if self.show_timer_running:
            return
        if self.hide_timer_running:
            return
        if self._should_start_balloon_show_timer():
            self.timeline_canvas.start_balloon_show_timer(milliseconds=500, oneShot=True)
            self.show_timer_running = True
        elif self._should_start_balloon_hide_timer():
            self.timeline_canvas.start_balloon_hide_timer(milliseconds=100, oneShot=True)
            self.hide_timer_running = True

    def _balloons_disabled(self):
        return not self.view_properties.show_balloons_on_hover

    def _current_event_selected(self):
        return (self.last_hovered_event is not None and
                self.timeline_canvas_controller.is_selected(self.last_hovered_event))

    def _should_start_balloon_show_timer(self):
        return (self._mouse_is_over_event() and
                not self._mouse_is_over_balloon() and
                not self._balloon_shown_for_event(self.last_hovered_event))

    def _should_start_balloon_hide_timer(self):
        return (self._balloon_is_shown() and
                not self._mouse_is_over_event() and
                not self._balloon_shown_for_event(self.last_hovered_balloon_event))

    def _mouse_is_over_event(self):
        return self.last_hovered_event is not None

    def _mouse_is_over_balloon(self):
        return self.last_hovered_balloon_event is not None

    def _balloon_is_shown(self):
        return self.view_properties.hovered_event is not None

    def _balloon_shown_for_event(self, event):
        return self.view_properties.hovered_event == event

    def balloon_show_timer_fired(self):
        self.show_timer_running = False
        self.timeline_canvas_controller._redraw_balloons(self.last_hovered_event)

    def balloon_hide_timer_fired(self):
        self.hide_timer_running = False
        hevt = self.view_properties.hovered_event
        # If there is no balloon visible we don't have to do anything
        if hevt is None:
            return
        cevt = self.last_hovered_event
        bevt = self.last_hovered_balloon_event
        # If the visible balloon doesn't belong to the event pointed to
        # we remove the ballloon.
        if hevt != cevt and hevt != bevt:
            self.timeline_canvas_controller._redraw_balloons(None)

    def _hit_move_handle(self, x, y, alt_down=False):
        event_and_rect = self.timeline_canvas_controller.event_with_rect_at(x, y, alt_down)
        if event_and_rect is None:
            return False
        event, rect = event_and_rect
        if event.get_locked():
            return None
        if not self.timeline_canvas_controller.is_selected(event):
            return False
        center = rect.X + rect.Width / 2
        if abs(x - center) <= HIT_REGION_PX_WITH:
            return True
        return False

    def _hit_resize_handle(self, x, y, alt_down=False):
        event_and_rect = self.timeline_canvas_controller.event_with_rect_at(x, y, alt_down)
        if event_and_rect is None:
            return None
        event, rect = event_and_rect
        if event.get_locked():
            return None
        if not self.timeline_canvas_controller.is_selected(event):
            return None
        if abs(x - rect.X) < HIT_REGION_PX_WITH:
            return wx.LEFT
        elif abs(rect.X + rect.Width - x) < HIT_REGION_PX_WITH:
            return wx.RIGHT
        return None
