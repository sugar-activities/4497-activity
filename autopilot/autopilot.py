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
import sys

from autopilotlib.app.appargs import ApplicationArguments
from autopilotlib.manuscript.manuscript import Manuscript
from autopilotlib.app.logger import Logger
from autopilotlib.app.bootstrap import start_app


def print_investigation(args, manuscript):
    print "%s %s\n" % (args.myname(), args.myversion()) 
    print "Application under test  : %s" % args.program()
    if len(manuscript.filepaths) == 0:
        print "The start script can't be found"
    else:
        print "Loggfile used for output: %s" % get_logpath(manuscript.filepaths[0])  
        print "File with start script  : %s" % manuscript.filepaths[0]
    print "\nEffective manuscript:\n%s" % manuscript

    
def start_test(args, manuscript):
    if len(manuscript.filepaths) > 0:
        Logger.set_path(get_logpath(manuscript.filepaths[0]))
        Logger.set_log_dialog_descriptions(args.descriptions())
        Logger.add_section("Manuscript", str(manuscript))
        start_app(manuscript, args.program())
    else:
        print "The start script can't be found"

     
def get_logpath(scriptpath):
    """
    The log is always written to a file named autopilot.log.
    The logfile is always placed in the same directory as the
    first found manuscript file.
    """
    logdir = os.path.dirname(scriptpath)
    logname = "autopilot.log"
    return os.path.join(logdir, logname)

    
def main():
    args = ApplicationArguments(sys.argv)
    manuscript = Manuscript(args)
    if not args.investigate():
        start_test(args, manuscript)
    else:
        print_investigation(args, manuscript)
          

if __name__ == "__main__":
    main()
