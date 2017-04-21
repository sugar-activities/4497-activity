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

from autopilotlib.app.decorators import Overrides
from autopilotlib.app.logger import Logger
from autopilotlib.wrappers.wrapper import Wrapper


wxPreviewFrame = wx.PreviewFrame


class PreviewFrame(wxPreviewFrame, Wrapper):
    
    def __init__(self, *args, **kw):
        self.set_active_window()
        wxPreviewFrame.__init__(self, *args, **kw)
        self._shown = False
        
    @Overrides(wxPreviewFrame)
    def Show(self, *args, **kw):
        self._shown = True
        Logger.add_open(self)
        self.call_when_win_shows(self._explore_and_register)
        super(PreviewFrame, self).Show(*args, **kw)
        
    def _explore_and_register(self):
        self._explore()
        PreviewFrame.register(self)
        
    def name(self):
        return self.GetLabel()
    
    def classname(self):
        return self.GetClassName()
        
    @Overrides(wxPreviewFrame)
    def IsShown(self):
        return self._shown
        
    @Overrides(wxPreviewFrame)
    def Destroy(self, *args, **kw):
        self._shown = False
        Logger.add_close(self)
        wxPreviewFrame.Destroy(self, *args, **kw)
        
    @classmethod
    def wrap(self, register):
        wx.PreviewFrame = PreviewFrame
        PreviewFrame.register = register
