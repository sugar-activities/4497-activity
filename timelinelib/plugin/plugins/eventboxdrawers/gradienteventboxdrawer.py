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

from timelinelib.plugin.plugins.eventboxdrawers.defaulteventboxdrawer import DefaultEventBoxDrawer
from timelinelib.drawing.utils import darken_color
from timelinelib.drawing.utils import lighten_color


class GradientEventBoxDrawer(DefaultEventBoxDrawer):

    def display_name(self):
        return _("Gradient Event box drawer")

    def _draw_background(self, dc, rect, event):
        dc.SetPen(self._get_border_pen(event))
        dc.DrawRectangleRect(rect)
        inner_rect = wx.Rect(*rect)
        inner_rect.Deflate(1, 1)
        dc.GradientFillLinear(inner_rect, self._get_light_color(event), self._get_dark_color(event), wx.SOUTH)

    def _get_light_color(self, event):
        return lighten_color(self._get_base_color(event))

    def _get_dark_color(self, event):
        return darken_color(self._get_base_color(event), factor=0.8)
