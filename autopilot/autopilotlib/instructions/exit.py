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


class ExitInstruction(Instruction):
    """
        0        1       
        command  object  
        
        command ::=  Exit
        object  ::=  Application | App
        
        Destroys the application by destroying the application main window.
        
        Example 1:   Exit Application
        Example 2:   exit app
    """        
    
    def execute(self, manuscript, win):
        # Everything ends here so we don't bother to call Instruction.execute
        manuscript.get_application_frame().Destroy()
        Logger.add_result("Application destroyed")
