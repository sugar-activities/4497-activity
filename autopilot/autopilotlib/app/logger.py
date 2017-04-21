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


INSTRUCTION = 0
RESULT = 1
ERROR = 2
LABELS = {
    INSTRUCTION : "INSTRUCTION:",
    RESULT:       "RESULT     :",
    ERROR:        "ERROR      :",
}


class Logger():

    path = None
    log_dialog_descriptions = False
    
    @classmethod
    def set_path(self, path_to_logfile):
        Logger.path = path_to_logfile
        fp = open(Logger.path, "w")
        fp.close    

    @classmethod
    def add(self, message):
        fp = open(Logger.path, "a")
        fp.write("%s\n" % message)
        fp.close        

    @classmethod
    def line(self):
        self.add("-------------------------------------------------")
            
    @classmethod
    def line2(self):
        self.add("   ----------------------------------------------")

    @classmethod
    def newline(self):
        self.add("")
            
    @classmethod
    def header(self, label):
        self.line()
        self.add(" %s" % label)
        self.line()

    @classmethod
    def header2(self, label):
        self.line2()
        self.add("    %s" % label)
        self.line2()

    @classmethod
    def add_section(self, header, text):
        self.header(header)
        lines = text.split("\n")
        for line in lines:
            self.add("   %s" % line)
        self.newline()
          
    @classmethod
    def add_instruction(self, result):
        self._add_log(INSTRUCTION, result)
          
    @classmethod
    def add_result(self, result):
        self._add_log(RESULT, result)

    @classmethod
    def add_open(self, win):
        self._add_log(RESULT, "%s '%s' opened" % (win.classname(), win.name()))
          
    @classmethod
    def add_close(self, win):
        self._add_log(RESULT, "%s '%s' closed" % (win.classname(), win.name()))
        
    @classmethod
    def add_error(self, result):
        self._add_log(ERROR, result)
          
    @classmethod
    def _add_log(self, logtype, result):
        self.add("%s %s" % (LABELS[logtype], result))
          
    @classmethod
    def set_log_dialog_descriptions(self, log_descriptions):
        Logger.log_dialog_descriptions = log_descriptions
