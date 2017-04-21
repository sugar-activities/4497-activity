#!/usr/bin/env python
#
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015  Rickard Lindberg, Roger Lindberg
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

import gettext
import locale
import os
import platform
import sys
import ConfigParser


# Make sure that we can import timelinelib
sys.path.insert(0, os.path.dirname(__file__))
try:
    import wx
except:
    if platform.machine().startswith('arm'):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs_arm"))
    else:
        if platform.architecture()[0] == '64bit':
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs64"))
        else:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))
# Make sure that we can import pysvg
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "pysvg-0.2.1"))
# Make sure that we can import pytz which icalendar is dependant on
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "pytz-2012j"))
# Make sure that we can import icalendar
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "icalendar-3.2"))
# Make sure that we can import markdown
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "markdown-2.0.3"))
# Make sure that we can import humblewx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs", "dependencies", "humblewx-master", "source"))

from timelinelib.config.arguments import ApplicationArguments
from timelinelib.config.paths import LOCALE_DIR
from timelinelib.meta.about import APPLICATION_NAME
from timelinelib.wxgui.setup import setup_humblewx
setup_humblewx()
from timelinelib.wxgui.setup import start_wx_application

if platform.system() == "Windows":
    # The appropriate environment variables are set on other systems
    language, encoding = locale.getdefaultlocale()
    os.environ['LANG'] = language

file_activity_info = ConfigParser.ConfigParser()
activity_info_path = os.path.abspath('./activity/activity.info')
file_activity_info.read(activity_info_path)
bundle_id = file_activity_info.get('Activity', 'bundle_id')
path = os.path.abspath('locale')

gettext.install(bundle_id, path, unicode=True)

application_arguments = ApplicationArguments()
application_arguments.parse_from([])

start_wx_application(application_arguments)
