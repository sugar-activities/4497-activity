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

import autopilotlib.manuscript.scanner as scanner
from autopilotlib.app.exceptions import NotFoundException

 
class Instruction():
    """
    The base class for all types of instructions.
    
    An instruction always belongs to a Manuscript.
    
    Textual syntax:  <instruction-name> <instruction-target>  <optional-arglist>

    """
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.include = False
        self.comment = False
        
    def __str__(self):
        text = []
        for token in self.tokens:
            if token.id in (scanner.KEYWORD, ):
                text.append(" ")
            text.append(token.lexeme)
        return "".join(text).strip()

    def execute(self, manuscript, win):
        manuscript.execute_next_instruction()
    
    def arg(self, n):
        """
        Return the n:th argument, where n = 1,2,....
        """
        try:
            offset = self._find_index_to_first_token_after_parenthesis()
            inx = offset + 2 * (n - 1)
            return self._symbol(inx)
        except:
            return None
    
    def _find_index_to_first_token_after_parenthesis(self):
        inx = 0
        for token in self.tokens:
            inx += 1
            if token.id == scanner.LP:
                break
        return inx
    
    def _symbol(self, index):
        try:
            token = self.tokens[index]
            if token.id == scanner.STRING:
                return token.lexeme[1:-1]
            else:
                return token.lexeme
        except:
            return None
  
    def get_all_args(self):
        args = []
        for token in self.tokens:
            if token.id == scanner.ID:
                args.append(token.lexeme)
            elif token.id == scanner.STRING:
                args.append(token.lexeme[1:-1])
        return args
            
    def find_win(self, win, classname, label=None):
        if label == None:
            name = win.GetLabel()
            win  = self._find_win_from_input(win, classname)
        else:
            name = label
            win = self._find_win_by_name(name, classname)
        return win, name
    
    def _find_win_from_input(self, win, classname):
        if win.ClassName == classname:
            return win
        raise NotFoundException()
        
    def _find_win_by_name(self, name, classname):
        wins = wx.GetTopLevelWindows()
        for win in wins:
            if win.ClassName == classname and win.GetLabel() == name:
                return win
        raise NotFoundException()
