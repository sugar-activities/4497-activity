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


class HideFrameInstruction(Instruction):
    """
        0        1         2  3    4
        command  object [  (  arg  )  ]?
        
        command ::=  Hide
        object  ::=  Frame
        arg     ::=  STRING | TEXT 
        
        Hide a frame window. If no arg is given, the frame to hide is 
        assumed to be the current window.
        
        Example 1:   Hide Frame(Help)
        Example 2:   Hide Frame
    """       
    
    @Overrides(Instruction)    
    def execute(self, manuscript, win=None):
        manuscript.execute_next_instruction()
        self._hide_frame(win)
        
    def _hide_frame(self, win):
        try:
            win, name = self.find_win(win, "wxFrame", self.arg(1))
            win.Hide()
        except NotFoundException:
            Logger.add_error("Frame(%s) not found" % name)
