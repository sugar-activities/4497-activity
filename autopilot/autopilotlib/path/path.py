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


ENV_AUTOPILOT_PATH = "AUTOPILOT_PATH"


class PathNotFoundException(Exception):
    pass


class Path():
    """
    This class holds the list of all directory paths in which Manuscript
    instruction files may be found.
    """
    
    def __init__(self, user_defined_paths):
        self.paths = user_defined_paths
        self._add_working_dir_to_paths()
        self._add_paths_from_environment_variable()
        self._add_users_home_path()
    
    def get_filepath(self, filename):
        """
        Returns the absolute path to the given file if it is found in any
        of the known paths.
        If not found an PathNotFoundException exception is raised.
        """
        for path in self.paths:
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                return filepath
        raise PathNotFoundException("Can't find file '%s'" % filename)

    def _add_working_dir_to_paths(self):
        self.paths.append(os.getcwd())

    def _add_paths_from_environment_variable(self):
        try:
            pathspec = os.getenv(ENV_AUTOPILOT_PATH)
            paths = [path for path in pathspec.split(";") 
                     if len(path.strip()) > 0]
            self.paths.extend(paths)
        except:
            pass
            
    def _add_users_home_path(self):
        self.paths.append(os.path.join(os.path.expanduser("~"), "autopilot"))
        
    def get_paths(self):
        return self.paths
    