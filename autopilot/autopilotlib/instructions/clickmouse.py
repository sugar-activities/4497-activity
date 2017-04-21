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
from autopilotlib.app.exceptions import NotFoundException
from autopilotlib.app.logger import Logger
from autopilotlib.app.decorators import Overrides


class ClickMouseInstruction(Instruction):
    """
        0        1       2  3  4  5  6
        command  object  (  x  ,  y  )
        
        command ::=  Click
        object  ::=  Mouse
        x, y    ::=  NUM
        
        X, y is measured relative the position of the active window and are
        expressed in pixels.
        
        Example 1:   Click Mouse (100,200)
    """    
    
    @Overrides(Instruction)    
    def execute(self, manuscript, win):
        manuscript.execute_next_instruction()
        self._clik_mouse(win)
        
    def _clik_mouse(self, win):
        pos = self._position(win)
        try:
            win.click_mouse(pos)
        except NotFoundException:
            Logger.add_error("Mouse click at (%d, %d) failed" % (pos[0], pos[1]))

    def _position(self, win):
        x, y = win.GetPosition()
        return (x + int(self.arg(1)), y + int(self.arg(2)))
