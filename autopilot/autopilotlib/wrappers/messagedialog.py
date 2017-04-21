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

from autopilotlib.app.logger import Logger
from autopilotlib.wrappers.wrapper import Wrapper
from autopilotlib.app.constants import TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS


wxMessageDialog = wx.MessageDialog


class MessageDialog(wxMessageDialog, Wrapper):
    
    def __init__(self, *args, **kw):
        wxMessageDialog.__init__(self, *args, **kw)
        
    def ShowModal(self):
        Logger.add_result("MessageDialog opened")
        wx.CallLater(TIME_TO_WAIT_FOR_DIALOG_TO_SHOW_IN_MILLISECONDS, 
                     self._explore, MessageDialog.listener)
        super(MessageDialog, self).ShowModal()
        
    @classmethod
    def wrap(self, listener):
        wx.MessageDialog = MessageDialog
        MessageDialog.listener = listener
