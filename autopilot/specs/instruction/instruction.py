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


EXIT_APP_INSTRUCTION = 'Exit App(X)'
EXIT_APP_INSTRUCTION_2 = 'Exit App("X")'


class InstructionSpecification(unittest.TestCase):
    
    def test_instruction_has_a_text_description(self):
        self.assert_text_description(EXIT_APP_INSTRUCTION)
        
    def test_arg_can_be_text(self):
        self.assert_symbol("X")
        
    def test_arg_can_be_string(self):
        self.given_an_instruction(EXIT_APP_INSTRUCTION_2)
        self.assert_symbol("X")
        
        
    def setUp(self):
        self.instruction = create_instruction(EXIT_APP_INSTRUCTION)
        self.manuscript = Mock(Manuscript)
    
    def tearDown(self):
        pass

    
    def given_an_instruction(self, text_description):
        self.instruction = create_instruction(text_description)

        
    def assert_text_description(self, text_description):
        self.assertEqual("exit application(X)", str(self.instruction))

    def assert_symbol(self, arg):
        self.assertEqual(arg, self.instruction.symbol(3))
        