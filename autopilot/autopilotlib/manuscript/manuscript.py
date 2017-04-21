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


from autopilotlib.instructions.factory import InstructionSyntaxException
from autopilotlib.path.path import PathNotFoundException
from autopilotlib.path.path import Path 
from autopilotlib.app.logger import Logger
from autopilotlib.instructions.factory import create_instruction 
from autopilotlib.app.constants import TIME_TO_WAIT_BEFORE_CONTINUING_IN_MILLISECONDS
from autopilotlib.manuscript.instructionpopup import InstructionPopup
from autopilotlib.guinatives.facade import get_foreground_window
from autopilotlib.guinatives.facade import get_active_window
from autopilotlib.guinatives.facade import get_window_text
import autopilotlib.guinatives.facade as win


class NoMoreInstructionsException(Exception):
    pass


class Manuscript():
    """
    This class holds all instructions for running a GUI application. The 
    manuscript can be merged from several manuscript instruction files.
    All files given on the command line to Autopilot are concatenated into
    one Manuscript. A Manuscript can also have Include instructions that
    include other manuscript instruction files.
    
    The instructions in the files are converted into Instruction objects.
    
    So a Manuscript has a list of Instruction objects.
    
    When the Manuscript is executed the Instructions are applied on the
    GUI application under test. 
    """
    
    def __init__(self, args):
        self.args = args
        self.instructions = []
        self.syntax_errors = []
        self.missing_scripts = []
        self.filepaths = []
        self.windows = []
        self.execution_started = False
        self.current_dialog = None
        self.popup = None
        self._load_manuscript([args.manuscript()])
            
    def execute_next_instruction(self):
        try:
            instruction = self._next_instruction()
            self._display_instruction_in_popup_window(instruction)
            if instruction.comment:
                delay = 0
            else:
                # TODO: We have some timing problem so we can't set
                #       waiting time to 0. 40 seems to be ok,
                delay = max(40, self.args.timedelay() * 1000) 
            wx.CallLater(delay, self._execute_instruction, instruction)
        except NoMoreInstructionsException:
            Logger.add("INSTRUCTION: None")
                
    def _display_instruction_in_popup_window(self, instruction):
        if self.popup == None:
            self.popup = InstructionPopup(self.windows[0])
        self.popup.SetText("%s" % instruction)
        
    def _next_instruction(self):
        try:
            instruction = self.instructions[0]
            self.instructions = self.instructions[1:]
            return instruction
        except:
            raise NoMoreInstructionsException()

    def _execute_instruction(self, instruction):
        Logger.add_instruction(instruction)
        current_window = self._get_current_window()
        instruction.execute(self, current_window)

    def __str__(self):
        collector = []
        for instruction in self.instructions:
            collector.append(str(instruction))
        if len(self.syntax_errors) > 0:
            collector.append(" ")
            collector.append("Instructions removed because of Invalid syntax:")
            collector.append("-----------------------------------------------")
            for line in self.syntax_errors:
                collector.append(line)
        if len(self.missing_scripts) > 0:
            collector.append(" ")
            collector.append("Scripts that can't be found:")
            collector.append("-----------------------------------------------")
            for line in self.missing_scripts:
                collector.append(line)
        return "\n".join(collector)
    
    def _load_manuscript(self, filenames):
        self._load_manuscript_from_command_line_files(filenames)
        self._load_manuscript_from_include_statements()
    
    def _load_manuscript_from_command_line_files(self, filenames): 
        for filename in filenames:
            instructions = self._read_manuscript(filename)
            self.instructions.extend(instructions)
        
    def _load_manuscript_from_include_statements(self):
        pos = 0
        for instruction in self.instructions:
            if instruction.include:
                self._load_included_manuscript(instruction, pos)
                # recursive call
                self._load_manuscript_from_include_statements()
                return
            pos += 1
    
    def _load_included_manuscript(self, include_instruction, pos):
        filename = include_instruction.filename()
        instructions = self._read_manuscript(filename)
        instructions.insert(0, create_instruction("#---- Included from %s ----" % filename))
        instructions.append(create_instruction("#---- End Included from %s ----" % filename))
        self.instructions[pos:pos+1] = instructions
        
    def _get_filename_from_include_instruction(self, instruction):
        return self._is_include(instruction)
    
    def _read_manuscript(self, manuscript):
        path = Path(self.args.paths())
        try:
            filepath = path.get_filepath(manuscript)
            fp = open(filepath, "r")
            instructions = []
            for line in fp:
                try:
                    instruction = create_instruction(line)
                    if instruction is not None:
                        instructions.append(instruction)
                except InstructionSyntaxException:
                    if len(line.strip()) > 0:
                        self.syntax_errors.append(line)
            fp.close()
            self.filepaths.append(filepath)
            return instructions
        except PathNotFoundException:
            self.missing_scripts.append(manuscript)
            return []
        
    def get_application_frame(self):
        return self.windows[0]
    
    def _get_current_window(self):
        self._validate_windows()
        try:
            current_window = self.windows[-1]
        except:
            current_window = None
        # MessageBox windows seems to to return ok on get_window_text(win.hwnd)
        # even though the dialog is closed!
        # So we remove it here because the only thing you can do is clicking a
        # a button and thereafter the dialog is closed.
        if current_window.messagebox:
            del(self.windows[-1])
        return current_window
            
    def _validate_windows(self):
        """Make sure the topmost window in the list self.windows is still
        valid. If not, remove it from the list and continue checking the
        list until the list is exhausted or a valid dialog is found.
        """
        self.windows.reverse()
        while len(self.windows) > 1:
            win = self.windows[0]
            try:
                get_window_text(win.hwnd)
                try:
                    if not win.IsShown():
                        self.windows = self.windows[1:]
                    else:
                        break
                except:
                    break
            except:
                self.windows = self.windows[1:]
        self.windows.reverse()
                
    def validate_dialog(self, hwnd, top_level_windows):
        top_level_windows.append(hwnd)
        return True
        
    def register_dialog(self, win=None):
        if win is None:
            return
        self.windows.append(win)
        if not self.execution_started:
            Logger.add_instruction("Execution of instructions start")
            self.execution_started = True
            wx.CallLater(TIME_TO_WAIT_BEFORE_CONTINUING_IN_MILLISECONDS, 
                         self.execute_next_instruction)
