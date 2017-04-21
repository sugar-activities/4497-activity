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


from sys import version as python_version
import platform
import sys
import traceback
import locale

import wx

from timelinelib.meta.version import get_version
from timelinelib.wxgui.frames.mainframe.mainframe import MainFrame
from timelinelib.wxgui.dialogs.feedback.view import show_feedback_dialog
from timelinelib.features.experimental.experimentalfeaturedateformatting import create_locale_sample_date


def setup_humblewx():
    import timelinelib.wxgui.components
    import humblewx
    humblewx.COMPONENT_MODULES.insert(0, timelinelib.wxgui.components)


def start_wx_application(application_arguments, before_main_loop_hook=None):
    app = wx.App(False)
    main_frame = MainFrame(application_arguments)
    main_frame.Show()
    sys.excepthook = unhandled_exception_hook
    if before_main_loop_hook:
        before_main_loop_hook()
    app.MainLoop()


def unhandled_exception_hook(exception_type, value, tb):
    show_feedback_dialog(
        parent=None,
        info=create_info_message(),
        subject=create_subject(exception_type, value),
        body=create_error_message(exception_type, value, tb))


def create_info_message():
    return ("An unexpected error has occurred. Help us fix it by reporting "
            "the error through this form. ")


def create_subject(exception_type, value):
    return "".join(traceback.format_exception_only(exception_type, value)).strip()


def create_error_message(exception_type, value, tb):
    return "\n".join([
        "Stacktrace:",
        "",
        indent(("".join(traceback.format_exception(exception_type, value, tb))).strip()),
        "",
        "Environment:",
        "",
        indent(create_versions_message()),
        indent(create_locale_message()),
    ])


def create_versions_message():
    return "\n".join([
        "Timeline version: %s" % get_version(),
        "System version: %s" % ", ".join(platform.uname()),
        "Python version: %s" % python_version.replace("\n", ""),
        "wxPython version: %s" % wx.version(),
    ])


def create_locale_message():
    return "\n".join([
        "Locale setting: %s" % " ".join(locale.getlocale(locale.LC_TIME)),
        "Locale sample date: %s" % create_locale_sample_date(),
    ])


def indent(text):
    return "\n".join("    " + x for x in text.split("\n"))
