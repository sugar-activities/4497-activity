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


import os.path

from optparse import OptionParser


USAGE = """%prog [options] filename

filename:  The name of the python program to test.

The program starts the program to test (PUT) and executes instructions
read from one or more manuscript files. The instructions executed
and their result are written to an output log file.

The program searches for the program to test in the following ways:
 1. As given on the command line
 2. In the current working directory
 3. In the directory %USER_HOME%/autopilot
 4. In the ditrectories given by AUTOPILOT_HOME environment variable
 
 The log file is written to the same directory where the first start
 script is found and will have the name autopilot.log.
 
 If no script file is given as an option the default start script is
 %USER_HOME%/autopilot/autopilot.manuscript.txt. Scriptfiles are
 searched for in the same order as for the program to test as described
 above.
  
"""


VERSION = "1.0"
HELP = {
    "p" : "extra path for search of files",
    "m" : "start manuscript file(s)",
    "d" : "log dialog descriptions or not",
    "t" : "time delay between instructions in seconds",
    "i" : "don't run test just display effective paths to program, script and log files",
}


class ApplicationArguments(object):

    def __init__(self, arguments):
        self.parser = self.define()
        (self.options, self.arguments) = self.parser.parse_args(arguments[1:])
        self.validate()
        
    def define(self):
        version_string = "Ver. %s" % VERSION
        parser = OptionParser(usage=USAGE, version=version_string)
        parser.add_option(
            "-p", "--path", dest="path", default=None, help=HELP["p"])
        parser.add_option(
            "-m", "--manuscript", dest="manuscript", default="autopilot.manuscript.txt", help=HELP["m"])
        parser.add_option(
            "-d", "--descriptions", dest="descriptions", action="store_true", default=False, help=HELP["d"])
        parser.add_option(
            "-i", "--investigate", dest="investigate", action="store_true", default=False, help=HELP["i"])
        parser.add_option(
            "-t", "--time-delay", dest="timedelay", type="int", default=4, help=HELP["t"])
        return parser
        
    def validate(self):
        self.validate_nbr_of_args()
        self.validate_program()
        
    def validate_nbr_of_args(self):
        if len(self.arguments) != 1:
            self.parser.error("One and only one python-program must be given")
            
    def validate_program(self):
        filename = self.arguments[0]
        self.valisdate_file_existance(filename, "Can't find the program %s" % filename)

    def valisdate_file_existance(self, filename, error_text):
        path = self._get_file_path(filename)
        if path is None:
            self.parser.error(error_text)

    def myname(self):
        return self.parser.get_prog_name()
    
    def myversion(self):
        return self.parser.get_version()
        
    def program(self):
        return self._get_file_path(self.arguments[0])

    def descriptions(self):
        return self.options.descriptions
    
    def investigate(self):
        return self.options.investigate
    
    def timedelay(self):
        # TODO: The system can't handle 0 time! 
        return max(0, self.options.timedelay)
    
    def manuscript(self):
        return self.options.manuscript

    def _get_file_path(self, filename):
        if os.path.exists(filename):
            return filename
        else:
            if self.paths() is not None:
                for path in self.paths():
                    pgmpath = os.path.join(path, filename)
                    if os.path.exists(pgmpath):
                        return pgmpath
        return None
    
    def paths(self):
        if self.options.path is not None:
            path_string = self.options.path.strip()
            if path_string.endswith(";"):
                path_string = path_string[:-1]
            paths = path_string.split(";")
            return paths
    