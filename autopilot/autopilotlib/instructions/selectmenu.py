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

from autopilotlib.instructions.instruction import Instruction
from autopilotlib.app.logger import Logger
from autopilotlib.app.exceptions import NotFoundException
from autopilotlib.app.decorators import Overrides


class SelectMenuInstruction(Instruction):
    """
        0        1       2  3     4  5       6  7
        command  object  (  arg1  ,  arg2  [ ,  arg]*  )
        
        command ::=  Select
        object  ::=  Menu | Mnu
        arg     ::=  STRING | TEXT 
        
        Select a menu in the the menu hierarchy, given by the args.
        At least 2 targets must be present.
        
        Example 1:   Select menu (Show, Sidebar)
        Example 2:   Select menu (Show, "Balloons on hover")
        Example 3:   Select Menu(File, New, "File Timeline...") 
    """    
        
    @Overrides(Instruction)    
    def execute(self, manuscript, win):
        manuscript.execute_next_instruction()
        self._select_menu(win)
        
    def _select_menu(self, win):
        try:
            item_id = self._find_menu_item_id(win)
            win.click_menu_item(item_id)   
        except NotFoundException:
            Logger.add_error("Menu not found")
            
    def _find_menu_item_id(self, win):
        labels   = self.get_all_args()
        menu_bar = self._get_menu_bar(win)
        inx = menu_bar.FindMenu(labels[0])
        menu = menu_bar.GetMenu(inx)
        labels = labels [1:]
        while len(labels) > 0:
            item_id = self._get_menu_item_id(menu, labels[0])
            if len(labels) > 1:
                menu_item = menu_bar.FindItemById(item_id)
                menu = menu_item.GetSubMenu()
            labels = labels [1:]
        return item_id

    def _get_menu_bar(self, win):
        menu_bar = win.GetMenuBar()
        if menu_bar is None:
            raise NotFoundException()
        return menu_bar

    def _get_menu_item_id(self, menu, label):
        valid_labels = self._get_valid_labels(label)
        for label in valid_labels:
            item_id = menu.FindItem(label)
            if item_id != wx.NOT_FOUND:
                return item_id
        return wx.NOT_FOUND
        
    def _get_valid_labels(self, label):
        valid_labels = [label]
        self._get_elipsis_label(label, valid_labels)
        self._get_accelerator_labels(label, valid_labels)
        return valid_labels 
        
    def _get_elipsis_label(self, label, alternative_labels):
        alternative_labels.append(label + "...")
         
    def _get_accelerator_labels(self, label, alternative_labels):
        for i in range(len(label)):
            alternative_label = label[0:i] + "&" + label[i:]
            alternative_labels.append(alternative_label)
        return alternative_labels
