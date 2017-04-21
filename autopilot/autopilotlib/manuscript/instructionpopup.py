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


import wx


class InstructionPopup(wx.PopupWindow):

    def __init__(self, parent):
        self.parent = parent
        wx.PopupWindow.__init__(self, parent, wx.SIMPLE_BORDER)
        self._create_gui()
        self.Show(True)
        wx.CallAfter(self.Refresh)

    def SetText(self, text):
        self.st.SetLabel(text)

    def _create_gui(self):
        self.SetBackgroundColour("GOLDENROD")
        self.st = wx.StaticText(self, -1, "", pos=(10,10))
        sz = self.st.GetBestSize()
        self.SetSize((sz.width + 20 + 350, sz.height + 20))
        w, h = wx.DisplaySize()
        w1, h1 = self.GetSize()
        x = w - w1 - 20
        y = h - 2.5 * h1
        self.SetPosition((x,y))
        # TODO:
        # Adjustments for two screens
        #   displays = (wx.Display(i) for i in range(wx.Display.GetCount()))
        #   sizes = [display.GetGeometry().GetSize() for display in displays]
