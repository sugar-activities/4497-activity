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


from autopilotlib.instructions.instruction import Instruction
from autopilotlib.app.logger import Logger
from autopilotlib.app.exceptions import NotFoundException
from autopilotlib.app.decorators import Overrides


class SelectComboboxInstruction(Instruction):
    """
        0        1       2  3  4  5    6
        command  object  (  n  ,  text )
        
        command ::=  Select
        object  ::=  combobox
        n       ::=  position of control starting with 1
        text    ::=  STRING | TEXT
        
        Select an item in th n:th combobox control. The item to selected is 
        identified by text. 
        
        Example 1:   Select customtreecontrol(1, "Private")
    """    
    
    @Overrides(Instruction)    
    def execute(self, manuscript, win):
        manuscript.execute_next_instruction()
        self._select_combobox_item(win)
        
    def _select_combobox_item(self, win):
        try:
            pos = int(self.arg(1))
            text = self.arg(2)
            win.select_combobox_item(pos, text)
        except NotFoundException:
            Logger.add_error("ComboBox control #%d item %s not found" % (pos, text))
