# Copyright (C) 2009, 2010, 2011  Roger Lindberg
#
# This program is part of Autopilot.
#
# Autopilot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Autopilot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Autopilot.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os.path
import unittest

def execute_all_specs():
    suite = create_suite()
    return execute_suite(suite)

def create_suite():
    path = "specs"
    module = "specs"
    suite = unittest.TestSuite()
    add_specs(suite, path, module)
    return suite

def execute_suite(suite):
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    return res.wasSuccessful()

def add_specs(suite, path, module):
    for program in os.listdir(path):
        if is_testscript(program):
            module_name = "%s.%s" % (module, os.path.basename(program)[:-3])
            load_test_cases_from_module_name(suite, module_name)
        elif os.path.isdir(os.path.join(path, program)):
            add_specs(suite, "%s\\%s" % (path, program), "%s.%s" % (path, program))

def is_testscript(filename):
    return filename.endswith(".py") and filename != "__init__.py"
    
def load_test_cases_from_module_name(suite, module_name):
    __import__(module_name)
    module = sys.modules[module_name]
    module_suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    filtered = filter_suite(module_suite)
    suite.addTest(filtered)

def filter_suite(test):
    new_suite = unittest.TestSuite()
    if isinstance(test, unittest.TestCase):
        if include_test(test):
            new_suite.addTest(test)
    else:
        for subtest in test:
            new_suite.addTest(filter_suite(subtest))
    return new_suite

def include_test(test):
    if hasattr(test, "GUI") and "--skip-gui" in sys.argv:
        return False
    if hasattr(test, "IO") and "--skip-io" in sys.argv:
        return False
    return True

if __name__ == '__main__':
    all_pass = execute_all_specs()
    if all_pass:
        sys.exit(0)
    else:
        sys.exit(1)
