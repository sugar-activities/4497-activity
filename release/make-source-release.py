#!/usr/bin/env python
#
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
import os.path
from subprocess import call

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# So that the we can write 'import timelinelib.xxx'
sys.path.insert(0, ROOT_DIR)

import timelinelib.meta.version

def make_source_release():
    zip_file_name = "timeline-%s.zip" % timelinelib.meta.version.get_version()
    warn_if_file_exists(zip_file_name)
    warn_if_dev_version()
    warn_if_specs_fail()
    export_from_hg_to(zip_file_name)

def warn_if_file_exists(zip_file_name):
    if os.path.exists(zip_file_name):
        continue_despite_warning("Archive '%s' already exists." % zip_file_name)

def warn_if_dev_version():
    if timelinelib.meta.version.DEV:
        continue_despite_warning("This is a development version.")

def warn_if_specs_fail():
    if call(["python", "%s/execute-specs.py" % (ROOT_DIR or ".")]) != 0:
        continue_despite_warning("Spec failure.")

def continue_despite_warning(warning_text):
    while True:
        answer = raw_input("%s Continue anyway? [y/N] " % warning_text)
        if answer == "n" or answer == "":
            sys.exit(1)
        elif answer == "y":
            return

def export_from_hg_to(zip_file_name):
    cmd = ["hg", "archive",
           "-R", ROOT_DIR,
           "-t", "zip", "--no-decode",
           "--exclude", "%s/.hgignore" % (ROOT_DIR or "."),
           "--exclude", "%s/.hgtags" % (ROOT_DIR or "."),
           "--exclude", "%s/.hg_archival.txt" % (ROOT_DIR or "."),
           zip_file_name]
    if call(cmd) != 0:
        print("Could not export from Mercurial")
        sys.exit(1)

if __name__ == '__main__':
    make_source_release()
