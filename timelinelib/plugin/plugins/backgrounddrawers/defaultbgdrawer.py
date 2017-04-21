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

from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.factory import BACKGROUND_DRAWER
from timelinelib.wxgui.utils import get_colour


class DefaultBackgroundDrawer(PluginBase):

    def service(self):
        return BACKGROUND_DRAWER

    def display_name(self):
        return _("Default background drawer")

    def draw(self, drawer, dc, scene, timeline):
        self.drawer = drawer
        self._erase_background(dc)
        self._draw_eras(dc, scene, timeline)

    def _erase_background(self, dc):
        w, h = dc.GetSizeTuple()
        self._set_color(dc, wx.WHITE)
        dc.DrawRectangle(0, 0, w, h)

    def _draw_eras(self, dc, scene, timeline):
        _, h = dc.GetSizeTuple()
        for era in timeline.get_all_eras():
            if self.drawer.period_is_visible(era.get_time_period()):
                self._draw_era(era, h)

    def _draw_era(self, era, h):
        self._draw_era_rect(era, h)
        self._draw_era_name_in_center_of_visible_era(era, h)

    def _draw_era_rect(self, era, h):
        x1, width = self._get_era_measures(era)
        self._set_color(self.drawer.dc, get_colour(era.get_color()))
        self.drawer.dc.DrawRectangle(x1, 0, width, h)

    def _draw_era_name_in_center_of_visible_era(self, era, h):
        x1, width = self._get_era_measures(era)
        wt, ht = self.drawer.dc.GetTextExtent(era.get_name())
        self.drawer.dc.DrawText(era.get_name(), x1 + width / 2 - wt / 2, h - ht)

    def _get_era_measures(self, era):
        x1, x2 = self.drawer.get_period_xpos(era.get_time_period())
        return x1, x2 - x1

    def _set_color(self, dc, color):
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
