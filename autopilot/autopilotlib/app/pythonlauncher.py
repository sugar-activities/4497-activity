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


import sys
import os
import imp
   
    
def run_python_file(args):
        """Run a python file as if it were the main program on the command line.

        `args` is the argument array to present as sys.argv, including the first
        element representing the file being executed.

        Lifted straight from coverage.py by Ned Batchelder

        """
        try:
            # In Py 2.x, the builtins were in __builtin__
            BUILTINS = sys.modules['__builtin__']
        except KeyError: # pragma: no cover - not worried about Python 3 yet...
            # In Py 3.x, they're in builtins
            BUILTINS = sys.modules['builtins']

        filename = args[0]
        
        # Create a module to serve as __main__
        old_main_mod = sys.modules['__main__']
        main_mod = imp.new_module('__main__')
        sys.modules['__main__'] = main_mod
        main_mod.__file__ = filename
        main_mod.__builtins__ = BUILTINS

        # Set sys.argv and the first path element properly.
        old_argv = sys.argv
        old_path0 = sys.path[0]
        sys.argv = args
        sys.path[0] = os.path.dirname(filename)

        try:
            source = open(filename, 'rU').read()
            exec compile(source, filename, "exec") in main_mod.__dict__
        finally:
            # Restore the old __main__
            sys.modules['__main__'] = old_main_mod

            # Restore the old argv and path
            sys.argv = old_argv
            sys.path[0] = old_path0
            