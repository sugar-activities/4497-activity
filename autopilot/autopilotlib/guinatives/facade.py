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


import platform


def isWindows():
    return platform.system() == "Windows"


if isWindows():
    import win32api
    import win32gui
    import win32con


def get_foreground_window():
    if isWindows():
        return win32gui.GetForegroundWindow()

    
def get_active_window():
    if isWindows():
        return win32gui.GetActiveWindow()

    
def get_classname(hwnd):
    return win32gui.GetClassName(hwnd)

    
def get_window_text(hwnd):
    return win32gui.GetWindowText(hwnd)


def get_children(hwnd):
    if isWindows():
        children = []
        win32gui.EnumChildWindows(hwnd, _get_child, children)
        return children
        
        
def _get_child(hwnd, children):
    if isWindows():
        class_name = win32gui.GetClassName(hwnd)
        text = win32gui.GetWindowText(hwnd)
        children.append((hwnd, class_name, text))
        return True


def send_lbutton_click_to_window(position):
    if isWindows():
        win32api.SetCursorPos(position)
        flags = win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_ABSOLUTE
        win32api.mouse_event(flags, 0, 0)
        flags = win32con.MOUSEEVENTF_LEFTUP | win32con.MOUSEEVENTF_ABSOLUTE
        win32api.mouse_event(flags, 0, 0)
  
          
def send_text_to_text_control(hwnd, text):
    if isWindows():
        win32gui.SetWindowText(hwnd, text)


def send_click_message_to_button(hwnd):
    if isWindows():
        win32gui.SendMessage(hwnd, win32con.BM_CLICK)


def send_select_combobox_item(hwnd, text):
    if isWindows():
        return win32gui.SendMessage(hwnd, win32con.CB_SELECTSTRING, -1, text)
                                