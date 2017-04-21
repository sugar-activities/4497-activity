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


import unittest

from mock import Mock

from autopilotlib.instructions.factory import create_instruction 
from autopilotlib.manuscript.manuscript import Manuscript 


INCLUDE_INSTRUCTION = 'Include(file.txt)'


class IncludeInstructionSpecification(unittest.TestCase):
    
    def test_include_instruction_has_include_flag(self):
        self.assertTrue(self.instruction.include)
        
    def test_include_instruction_has_a_filename(self):
        self.assertEqual("file.txt", self.instruction.filename())
        
    def test_include_instruction_can_execute(self):
        self.when_execute_called()
        self.manuscript.execute_next_instruction.assert_called()
        

    def setUp(self):
        self.instruction = create_instruction(INCLUDE_INSTRUCTION)
        self.manuscript = Mock(Manuscript)
    
    def tearDown(self):
        pass

        
    def when_execute_called(self):
        self.instruction.execute(self.manuscript)
        