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


import os
import wx
import math

from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.factory import EVENTBOX_DRAWER
from timelinelib.drawing.utils import darken_color
from timelinelib.features.experimental.experimentalfeatures import EXTENDED_CONTAINER_HEIGHT
from timelinelib.wxgui.utils import get_colour
from timelinelib.config.paths import ICONS_DIR


HANDLE_SIZE = 4
HALF_HANDLE_SIZE = HANDLE_SIZE / 2
DATA_INDICATOR_SIZE = 10
INNER_PADDING = 3  # Space inside event box to text (pixels)
GRAY = (200, 200, 200)


class DefaultEventBoxDrawer(PluginBase):

    def service(self):
        return EVENTBOX_DRAWER

    def display_name(self):
        return _("Default Event box drawer")

    def run(self, dc, scene, rect, event, selected=False):
        self.center_text = scene.center_text()
        if scene.never_show_period_events_as_point_events() and rect.y < scene.divider_y and event.is_period():
            self._draw_period_event_as_symbol_below_divider_line(dc, scene, event)
        else:
            self._draw_event_box(dc, rect, event, selected)

    def _draw_period_event_as_symbol_below_divider_line(self, dc, scene, event):
        dc.DestroyClippingRegion()
        x = scene.x_pos_for_time(event.mean_time())
        y0 = scene.divider_y
        y1 = y0 + 10
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.SOLID))
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1, wx.SOLID))
        dc.DrawLine(x, y0, x, y1)
        dc.DrawCircle(x, y1, 2)

    def _draw_event_box(self, dc, rect, event, selected):
        self._draw_background(dc, rect, event)
        self._draw_fuzzy_edges(dc, rect, event)
        self._draw_locked_edges(dc, rect, event)
        self._draw_progress_box(dc, rect, event)
        self._draw_text(dc, rect, event)
        self._draw_contents_indicator(dc, event, rect)
        self._draw_locked_edges(dc, rect, event)
        self._draw_selection_handles(dc, event, rect, selected)
        self._draw_hyperlink(dc, rect, event)

    def _draw_background(self, dc, rect, event):
        dc.SetBrush(wx.Brush(self._get_base_color(event), wx.SOLID))
        dc.SetPen(self._get_border_pen(event))
        dc.DrawRectangleRect(rect)

    def _draw_fuzzy_edges(self, dc, rect, event):
        if event.get_fuzzy():
            self._draw_fuzzy_start(dc, rect, event)
            if not event.get_ends_today():
                self._draw_fuzzy_end(dc, rect, event)

    def _draw_locked_edges(self, dc, rect, event):
        if event.get_ends_today():
            self._draw_locked_end(dc, event, rect)
        if event.get_locked():
            self._draw_locked_start(dc, event, rect)
            self._draw_locked_end(dc, event, rect)

    def _draw_contents_indicator(self, dc, event, rect):
        if event.has_balloon_data():
            self._draw_balloon_indicator(dc, event, rect)

    def _draw_selection_handles(self, dc, event, rect, selected):
        if not event.locked and selected:
            self._draw_handles(dc, event, rect)

    def _get_border_pen(self, event):
        return wx.Pen(self._get_border_color(event), 1, wx.SOLID)

    def _get_balloon_indicator_brush(self, event):
        base_color = self._get_base_color(event)
        darker_color = darken_color(base_color, 0.6)
        brush = wx.Brush(darker_color, wx.SOLID)
        return brush

    def _get_border_color(self, event):
        return darken_color(self._get_base_color(event))

    def _get_base_color(self, event):
        try:
            return event.get_category().color
        except:
            return GRAY

    def _draw_fuzzy_start(self, dc, rect, event):
        self._inflate_clipping_region(dc, rect)
        dc.DrawBitmap(self._get_fuzzy_bitmap(), rect.x - 4, rect.y + 4, True)

    def _draw_fuzzy_end(self, dc, rect, event):
        self._inflate_clipping_region(dc, rect)
        dc.DrawBitmap(self._get_fuzzy_bitmap(), rect.x + rect.width - 8, rect.y + 4, True)

    def draw_fuzzy(self, dc, event, p1, p2, p3, p4, p5):
        self._erase_outzide_fuzzy_box(dc, p1, p2, p3)
        self._erase_outzide_fuzzy_box(dc, p3, p4, p5)
        self._draw_fuzzy_border(dc, event, p2, p3, p5)

    def _erase_outzide_fuzzy_box(self, dc, p1, p2, p3):
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawPolygon((p1, p2, p3))

    def _draw_fuzzy_border(self, dc, event, p1, p2, p3):
        gc = wx.GraphicsContext.Create(dc)
        path = gc.CreatePath()
        path.MoveToPoint(p1.x, p1.y)
        path.AddLineToPoint(p2.x, p2.y)
        path.AddLineToPoint(p3.x, p3.y)
        gc.SetPen(self._get_border_pen(event))
        gc.StrokePath(path)

    def _draw_locked_start(self, dc, event, rect):
        self._inflate_clipping_region(dc, rect)
        dc.DrawBitmap(self._get_lock_bitmap(), rect.x - 7, rect.y + 3, True)

    def _draw_locked_end(self, dc, event, rect):
        self._inflate_clipping_region(dc, rect)
        dc.DrawBitmap(self._get_lock_bitmap(), rect.x + rect.width - 8, rect.y + 3, True)

    def _draw_locked(self, dc, event, rect, x, start_angle, end_angle):
        y = rect.y + rect.height / 2
        r = rect.height / 2.5
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawCircle(x, y, r)
        dc.SetPen(self._get_border_pen(event))
        self.draw_segment(dc, event, x, y, r, start_angle, end_angle)

    def draw_segment(self, dc, event, x0, y0, r, start_angle, end_angle):
        gc = wx.GraphicsContext.Create(dc)
        path = gc.CreatePath()
        segment_length = 2.0 * (end_angle - start_angle) * r
        delta = (end_angle - start_angle) / segment_length
        angle = start_angle
        x1 = r * math.cos(angle) + x0
        y1 = r * math.sin(angle) + y0
        path.MoveToPoint(x1, y1)
        while angle < end_angle:
            angle += delta
            if angle > end_angle:
                angle = end_angle
            x2 = r * math.cos(angle) + x0
            y2 = r * math.sin(angle) + y0
            path.AddLineToPoint(x2, y2)
            x1 = x2
            y1 = y2
        gc.SetPen(self._get_border_pen(event))
        gc.StrokePath(path)

    def _draw_progress_box(self, dc, rect, event):
        if event.get_data("progress"):
            self._set_progress_color(dc, event)
            progress_rect = self._get_progress_rect(rect, event.get_data("progress") / 100.0)
            dc.DrawRectangleRect(progress_rect)

    def _set_progress_color(self, dc, event):
        progress_color = event.get_progress_color()
        dc.SetBrush(wx.Brush(wx.Colour(progress_color[0], progress_color[1], progress_color[2])))

    def _get_progress_rect(self, event_rect, width_factor):
        HEIGHT_FACTOR = 0.35
        w = event_rect.width * width_factor
        h = event_rect.height * HEIGHT_FACTOR
        y = event_rect.y + (event_rect.height - h)
        return wx.Rect(event_rect.x, y, w, h)

    def _draw_balloon_indicator(self, dc, event, rect):
        """
        The data contents indicator is a small triangle drawn in the upper
        right corner of the event rectangle.
        """
        corner_x = rect.X + rect.Width
        points = (
            wx.Point(corner_x - DATA_INDICATOR_SIZE, rect.Y),
            wx.Point(corner_x, rect.Y),
            wx.Point(corner_x, rect.Y + DATA_INDICATOR_SIZE),
        )
        dc.SetBrush(self._get_balloon_indicator_brush(event))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawPolygon(points)

    def _draw_text(self, dc, rect, event):

        def center_text():
            width, _ = dc.GetTextExtent(event.get_text())
            if width < rect_copy.width:
                return text_x + (rect_copy.width - width) / 2
            else:
                return text_x

        # Ensure that we can't draw content outside inner rectangle
        rect_copy = wx.Rect(*rect)
        rect_copy.Deflate(INNER_PADDING, INNER_PADDING)
        if rect_copy.Width > 0:
            # Draw the text (if there is room for it)
            text_x = rect.X + INNER_PADDING
            if event.get_fuzzy() or event.get_locked():
                text_x += rect.Height / 2
            text_y = rect.Y + INNER_PADDING
            if text_x < INNER_PADDING:
                text_x = INNER_PADDING
            self._set_text_foreground_color(dc, event)
            if event.is_container() and EXTENDED_CONTAINER_HEIGHT.enabled():
                EXTENDED_CONTAINER_HEIGHT.draw_container_text_top_adjusted(event.get_text(), dc, rect)
            else:
                if self.center_text:
                    text_x = center_text()
                dc.SetClippingRect(rect_copy)
                dc.DrawText(event.get_text(), text_x, text_y)
            dc.DestroyClippingRegion()

    def _set_text_foreground_color(self, dc, event):
        try:
            dc.SetTextForeground(get_colour(event.get_category().font_color))
        except:
            dc.SetTextForeground(wx.BLACK)

    def _draw_handles(self, dc, event, rect):

        def draw_frame_around_event():
            small_rect = wx.Rect(*rect)
            small_rect.Deflate(1, 1)
            border_color = self._get_border_color(event)
            border_color = darken_color(border_color)
            pen = wx.Pen(border_color, 1, wx.SOLID)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(pen)
            dc.DrawRectangleRect(small_rect)

        dc.SetClippingRect(rect)
        draw_frame_around_event()
        self._draw_all_handles(dc, rect, event)
        dc.DestroyClippingRegion()

    def _draw_all_handles(self, dc, rect, event):

        def inflate_clipping_region():
            big_rect = wx.Rect(*rect)
            big_rect.Inflate(HANDLE_SIZE, HANDLE_SIZE)
            dc.DestroyClippingRegion()
            dc.SetClippingRect(big_rect)

        def set_pen_and_brush():
            dc.SetBrush(wx.BLACK_BRUSH)
            dc.SetPen(wx.BLACK_PEN)

        def create_handle_rect():
            HALF_EVENT_HEIGHT = rect.Height / 2
            y = rect.Y + HALF_EVENT_HEIGHT - HALF_HANDLE_SIZE
            x = rect.X - HALF_HANDLE_SIZE + 1
            return wx.Rect(x, y, HANDLE_SIZE, HANDLE_SIZE)

        def draw_rect(handle_rect, offset):
            handle_rect.OffsetXY(offset, 0)
            dc.DrawRectangleRect(handle_rect)

        def draw_handle_rects(handle_rect):
            HALF_EVENT_WIDTH = rect.Width / 2
            EVENT_WIDTH = rect.Width
            draw_rect(handle_rect, 0)
            draw_rect(handle_rect, EVENT_WIDTH - 2)
            if not event.ends_today:
                draw_rect(handle_rect, -HALF_EVENT_WIDTH)

        inflate_clipping_region()
        set_pen_and_brush()
        handle_rect = create_handle_rect()
        draw_handle_rects(handle_rect)

    def _draw_hyperlink(self, dc, rect, event):
        if event.get_hyperlink():
            dc.DrawBitmap(self._get_hyperlink_bitmap(), rect.x + rect.width - 14, rect.y + 4, True)

    def _get_hyperlink_bitmap(self):
        return wx.Bitmap(os.path.join(ICONS_DIR, "hyperlink.png"))

    def _inflate_clipping_region(self, dc, rect):
        copy = wx.Rect(*rect)
        copy.Inflate(10, 0)
        dc.DestroyClippingRegion()
        dc.SetClippingRect(copy)

    def _get_lock_bitmap(self):
        return wx.Bitmap(os.path.join(ICONS_DIR, "lock.png"))

    def _get_fuzzy_bitmap(self):
        return wx.Bitmap(os.path.join(ICONS_DIR, "appx.png"))
