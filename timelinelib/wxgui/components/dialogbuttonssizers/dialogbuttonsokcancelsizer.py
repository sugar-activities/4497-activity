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
import platform

from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonssizer import DialogButtonsSizer


class DialogButtonsOkCancelSizer(DialogButtonsSizer):

    def __init__(self, parent):
        DialogButtonsSizer.__init__(self, parent)
        parent.btn_ok = wx.Button(parent, wx.ID_OK)
        parent.btn_cancel = wx.Button(parent, wx.ID_CANCEL)
        if platform.system() == "Windows":
            self.buttons = (parent.btn_ok, parent.btn_cancel)
            self.default = 0
        else:
            self.buttons = (parent.btn_cancel, parent.btn_ok)
            self.default = 1
        self.AddButtons(self.buttons, self.default)
