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


class EnterTextInstruction(Instruction):
    """
        0        1       2  3  4  5    6
        command  object  (  n  ,  text )
        
        command ::=  Enter
        object  ::=  Text
        n       ::=  NUM
        text    ::=  STRING | TEXT
        
        Enter the given text into a Text Control field.
        n     Indicates the n:th text field in the dialog. n starts with 1.
        
        Example 1:   Enter text(1, "2013-10-12")
        Example 2:   Enter text(2, myname)
    """    

    @Overrides(Instruction)    
    def execute(self, manuscript, win):
        manuscript.execute_next_instruction()
        self._enter_text(win)
        
    def _enter_text(self, win):
        pos = int(self.arg(1))
        text = self.arg(2)
        try:
            win.enter_text(pos, text)
        except NotFoundException:
            Logger.add_error("Text control #%d not found" % pos)
