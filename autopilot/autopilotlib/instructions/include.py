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


class IncludeInstruction(Instruction):
    """
        0        1  2    3 
        command  (  arg  )
        
        command ::=  Include
        arg     ::=  STRING | TEXT
        
        Include a named manuscript into the current manuscript at the position
        of the include instruction.
        
        Example 1:   include(release_validation.txt)
    """        

    def __init__(self, tokens):
        Instruction.__init__(self, tokens)
        self.include = True
        
    def filename(self):
        return self.arg(1)
