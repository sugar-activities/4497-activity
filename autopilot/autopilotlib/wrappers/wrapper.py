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

from autopilotlib.app.constants import MILLISECONDS_TO_WAIT_FOR_DIALOG_TO_SHOW
from autopilotlib.app.exceptions import NotFoundException
from autopilotlib.app.logger import Logger
from autopilotlib.describers.window import WindowDescriber
import autopilotlib.guinatives.facade as win


BUTTON = "Button"
EDIT = "Edit"
COMBOBOX = "ComboBox"


class Wrapper(object):
    """
    This is the base class for all wrappers.
    
    A wrapper wraps a wx-defined window/dialog class, to be able to detect a 
    call to the constructor, from the AUT, to such a class.
    
    This base class contains generic functions for manipulate the children of
    the window/dialog. These functions are used by Instruction objects.
    The childrens of a window/dialog are buttons edit fields etc.
    
    Internally this base class is used by all wrappers to explore and register
    all the childrens of the window/dialog. The eplorer assumes that the 
    window to be explored is the 'active' window of the AUT.
    The explorer also uses a Describer class to log the description of the
    window/dialog.
    
    """
    
    #
    # Public methods
    #    
    def click_button(self, label):
        hwnd = self._get_button(label)
        self._send_click_message_to_button(hwnd)

    def click_mouse(self, position):
        try:
            self._send_lbutton_click_to_window(position)
            Logger.add_result("Mouse clicked at (%d, %d)" % (position[0], position[1]))
        except NotFoundException:
            Logger.add_error("Mouse click failed")

    def enter_text(self, position, new_text):
        hwnd = self._get_text_control(position)
        self._send_text_to_text_control(hwnd, new_text)

    def select_custom_tree_control_item(self, nbr, label):
        position = 1
        for child in self.Children:
            if child.GetLabel() == "CustomTreeCtrl" and position == nbr:
                tree = child
                item = self.get_item_by_label(tree, label, tree.GetRootItem())
                tree.SelectItem(item)
                return
        raise NotFoundException()
    
    def get_item_by_label(self, tree, search_text, root_item):
        item, cookie = tree.GetFirstChild(root_item)
        while item.IsOk():
            text = tree.GetItemText(item)
            if text.lower() == search_text.lower():
                return item
            if tree.ItemHasChildren(item):
                match = self.get_item_by_label(tree, search_text, item)
                if match.IsOk():
                    return match
            item, cookie = tree.GetNextChild(root_item, cookie)
    
    def click_menu_item(self, item_id):
        self.ProcessCommand(item_id)

    #
    # Internals
    #
    def _explore(self, register_win=None):
        self.messagebox = False
        self.hwnd = win.get_active_window()
        self.children = win.get_children(self.hwnd)
        WindowDescriber.describe(self)
        if register_win is not None:
            register_win(self)

    def select_combobox_item(self, pos, label):
        ctrl = self._get_combobox_control_by_position(pos)
        rv =  win.send_select_combobox_item(ctrl, label)
        if rv is not None and rv < 0:
            raise NotFoundException()
    
    def _send_click_message_to_button(self, hwnd):
        win.send_click_message_to_button(hwnd)
        
    def _send_text_to_text_control(self, hwnd, text):
        win.send_text_to_text_control(hwnd, text)
     
    def _send_lbutton_click_to_window(self, position):
        win.send_lbutton_click_to_window(position)
           
    def _get_button(self, label):     
        try:
            return self._get_button_by_poistion(int(label))
        except:
            return self._get_button_by_label(label)

    def _get_text_control(self, position):     
        return self._get_text_control_by_position(position)
 
    def _get_combobox_control_by_position(self, position):     
        return  self._get_control_by_position(position, COMBOBOX)
    
    def _get_text_control_by_position(self, position):     
        return  self._get_control_by_position(position, EDIT)
        
    def _get_button_by_poistion(self, position):
        return  self._get_control_by_position(position, BUTTON)

    def _get_button_by_label(self, label):
        return self._get_control_by_label(label, BUTTON)

    def _get_control_by_position(self, position, control_class):
        count = 1
        for hwnd, class_name, _ in self.children:
            if class_name == control_class: 
                if position == count:
                    return hwnd
                count += 1
        raise NotFoundException()                
            
    def _get_control_by_label(self, label, control_class):
        for hwnd, class_name, text in self.children:
            if class_name == control_class: 
                if text == label:
                    return hwnd   
                # Try with elipses
                elif text == label + "...":
                    return hwnd   
                # Try with accelerator
                else:
                    for i in range(len(label)):
                        lbl = label[0:i] + "&" + label[i:]
                        if text == lbl:
                            return hwnd   
        raise NotFoundException()

    def set_active_window(self):
        self._active_window = win.get_active_window()
        
    def call_when_win_shows(self, method):
        self._prev_win = None
        try:
            self._prev_win = self._active_window
        except:
            pass    
        if self._prev_win == None:
            self._prev_win = win.get_active_window()
        wx.CallLater(MILLISECONDS_TO_WAIT_FOR_DIALOG_TO_SHOW, self._wait_for_win_to_show, method)
        
    def _wait_for_win_to_show(self, method):
        if self._prev_win == win.get_active_window():
            wx.CallLater(MILLISECONDS_TO_WAIT_FOR_DIALOG_TO_SHOW, self._wait_for_win_to_show, method)
        else:
            method()
