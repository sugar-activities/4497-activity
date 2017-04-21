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


import os

import unittest
from mock import Mock

from autopilotlib.instructions.factory import create_instruction 
from autopilotlib.manuscript.manuscript import Manuscript 
from autopilotlib.app.logger import Logger

EXIT_INSTRUCTION = "Exit Application"


class WinMock():
    
    nbr_of_calls_to_destroy = 0
    
    def Destroy(self):
        WinMock.nbr_of_calls_to_destroy += 1
        

class ExitInstructionSpecification(unittest.TestCase):
    
    def test_exit_instruction_calls_win_destroy_method(self):
        self.when_execute_called()
        self.assertEqual(1, WinMock.nbr_of_calls_to_destroy)
        self.manuscript.execute_next_instruction.assert_called()
        

    def setUp(self):
        Logger.set_path(os.path.join(os.path.dirname(__file__), "test.log"))
        self.instruction = create_instruction(EXIT_INSTRUCTION)
        self.win = WinMock()
        self.manuscript = Mock(Manuscript)
        self.manuscript.get_application_frame.return_value = self.win
        
    def tearDown(self):
        pass

        
    def when_execute_called(self):
        self.instruction.execute(self.manuscript, self.win)
        
        
