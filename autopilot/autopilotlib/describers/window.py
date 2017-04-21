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


from autopilotlib.app.logger import Logger
from autopilotlib.describers.menubar import MenuBarDescriber
import autopilotlib.guinatives.facade as win


class WindowDescriber():
    
    @classmethod
    def describe(self, win):
        if Logger.log_dialog_descriptions:
            self.describe_window(win.hwnd)
            self.describe_wxdialog(win)
            MenuBarDescriber.describe(win)
                
    @classmethod
    def describe_window(self, hwnd):
        if hwnd == None:
            hwnd = win.get_active_window()
        Logger.header(" Window Description hwnd: %d Classname: '%s' Label: '%s'" % (hwnd, win.get_classname(hwnd), win.get_window_text))
        Logger.header2("Native Description")
        self.describe_children(hwnd)
        
    @classmethod
    def describe_children(self, hwnd):
        Logger.add("    hwnd     Classname                 Label")
        Logger.add("    -------  ------------------------  ------------------")
        children = win.get_children(hwnd)
        for hwnd, class_name, text in children:
            Logger.add("   %8d  %-24.24s  '%s'" % (hwnd, class_name, text))
            
    @classmethod
    def describe_wxdialog(self, win, level=0):
        if win is None:
            return
        try:
            if len(win.Children) == 0:
                return
        except AttributeError:
            return
        Logger.newline()
        Logger.header2("wx Description")
        Logger.add("   Id    Classname                Label             Name")
        Logger.add("   ----  ------------------------ ----------------  ----------------")
        self.describe_wxdialog_windows(win)
        
    @classmethod
    def describe_wxdialog_windows(self, win, level=0):
        try:
            for child in win.Children:
                child_id = child.GetId()
                margin = "%*.*s" % (level*3, level*3, "")
                Logger.add("   %s%4d  %-24.24s %-16.16s  '%s'" % (margin, child_id, child.GetClassName(), child.GetLabel(), child.GetName()))
                self.describe_wxdialog_windows(child, level+1)
        except AttributeError:
            Logger.add("   No children exiets")
            