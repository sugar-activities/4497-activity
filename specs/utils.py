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


import datetime
import os.path
import shutil
import sys
import tempfile
import traceback
import unittest

import wx
import wx.lib.inspection

from timelinelib.calendar.monthnames import ABBREVIATED_ENGLISH_MONTH_NAMES
from timelinelib.config.arguments import ApplicationArguments
from timelinelib.config.dotfile import read_config
from timelinelib.db import db_open
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.time.pytime import PyTimeType
from timelinelib.time.wxtime import WxTimeType
from timelinelib.wxgui.setup import start_wx_application


ANY_TIME = "1 Jan 2010"


def py_period(start, end):
    return TimePeriod(PyTimeType(), human_time_to_py(start), human_time_to_py(end))


def wx_period(start, end):
    return TimePeriod(WxTimeType(), human_time_to_wx(start), human_time_to_wx(end))


def human_time_to_py(human_time):
    (year, month, day, hour, minute) = human_time_to_ymdhm(human_time)
    return py_time(year, month, day, hour, minute)


def human_time_to_wx(human_time):
    (year, month, day, hour, minute) = human_time_to_ymdhm(human_time)
    return wx_time(year, month, day, hour, minute)


def human_time_to_ymdhm(human_time):
    parts = human_time.split(" ")
    day_part, month_part, year_part = parts[0], parts[1], parts[2]
    day = int(day_part)
    month = ABBREVIATED_ENGLISH_MONTH_NAMES.index(month_part) + 1
    year = int(year_part)
    if len(parts) == 4:
        hour = int(parts[3][:2])
        minute = int(parts[3][3:])
    else:
        hour = 0
        minute = 0
    return (year, month, day, hour, minute)


def py_time(year, month, day, hour=0, minute=0, second=0):
    return datetime.datetime(year, month, day, hour, minute, second)


def wx_time(year, month, day, hour=0, minute=0, second=0):
    return wx.DateTimeFromDMY(day, month-1, year, hour, minute, second)


def an_event():
    return an_event_with(time=ANY_TIME)


def an_event_with(start=None, end=None, time=ANY_TIME, text="foo", fuzzy=False,
                  locked=False, ends_today=False):
    if start and end:
        start = human_time_to_py(start)
        end = human_time_to_py(end)
    else:
        start = human_time_to_py(time)
        end = human_time_to_py(time)
    return Event(
        PyTimeType(), start, end, text, Category("bar", None, None, True),
        fuzzy=fuzzy, locked=locked, ends_today=ends_today)


class TmpDirTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="timeline-test")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def get_tmp_path(self, name):
        return os.path.join(self.tmp_dir, name)


class WxEndToEndTestCase(TmpDirTestCase):

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.timeline_path = self.get_tmp_path("test.timeline")
        self.config_file_path = self.get_tmp_path("thetimelineproj.cfg")
        self.config = read_config(self.config_file_path)
        self.standard_excepthook = sys.excepthook
        self.error_in_gui_thread = None

    def tearDown(self):
        TmpDirTestCase.tearDown(self)
        sys.excepthook = self.standard_excepthook

    def start_timeline_and(self, steps_to_perform_in_gui):
        self.config.write()
        self.steps_to_perform_in_gui = steps_to_perform_in_gui
        application_arguments = ApplicationArguments()
        application_arguments.parse_from(
            ["--config-file", self.config_file_path, self.timeline_path])
        start_wx_application(application_arguments, self._before_main_loop_hook)
        if self.error_in_gui_thread:
            exc_type, exc_value, exc_traceback = self.error_in_gui_thread
            a = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.fail("Exception in GUI thread: %s" % "".join(a))

    def read_written_timeline(self):
        return db_open(self.timeline_path)

    def _before_main_loop_hook(self):
        sys.excepthook = self.standard_excepthook
        self._setup_steps_to_perform_in_gui(self.steps_to_perform_in_gui)

    def _setup_steps_to_perform_in_gui(self, steps, in_sub_step_mode=False):
        def perform_current_step_and_queue_next():
            if len(steps) >= 2 and isinstance(steps[1], list):
                self._setup_steps_to_perform_in_gui(steps[1], True)
                next_step_index = 2
            else:
                next_step_index = 1
            try:
                steps[0]()
            except Exception:
                wx.GetApp().GetTopWindow().Close()
                self.error_in_gui_thread = sys.exc_info()
            else:
                if steps[0] != self.show_widget_inspector:
                    self._setup_steps_to_perform_in_gui(steps[next_step_index:], in_sub_step_mode)
        if len(steps) > 0:
            wx.CallAfter(perform_current_step_and_queue_next)
        elif not in_sub_step_mode:
            wx.CallAfter(wx.GetApp().GetTopWindow().Close)

    def show_widget_inspector(self):
        wx.lib.inspection.InspectionTool().Show()

    def click_menu_item(self, item_path):
        def click():
            item_names = [_(x) for x in item_path.split(" -> ")]
            menu_bar = wx.GetApp().GetTopWindow().GetMenuBar()
            menu = menu_bar.GetMenu(menu_bar.FindMenu(item_names[0]))
            for sub in item_names[1:]:
                menu = menu_bar.FindItemById(menu.FindItem(sub))
            wx.GetApp().GetTopWindow().ProcessEvent(
                wx.CommandEvent(wx.EVT_MENU.typeId, menu.GetId()))
        return click

    def click_button(self, component_path):
        def click():
            component = self.find_component(component_path)
            component.ProcessEvent(wx.CommandEvent(wx.EVT_BUTTON.typeId, component.GetId()))
        return click

    def enter_text(self, component_path, text):
        def enter():
            self.find_component(component_path).SetValue(text)
        return enter

    def find_component(self, component_path):
        components_to_search_in = wx.GetTopLevelWindows()
        for component_name in component_path.split(" -> "):
            component = self._find_component_with_name_in(
                components_to_search_in, component_name)
            if component == None:
                self.fail("Could not find component with path '%s'." % component_path)
            else:
                components_to_search_in = component.GetChildren()
        return component

    def _find_component_with_name_in(self, components, seeked_name):
        for component in components:
            if self._matches_seeked_name(component, seeked_name):
                return component
        for component in components:
            sub = self._find_component_with_name_in(component.GetChildren(), seeked_name)
            if sub:
                return sub
        return None

    def _matches_seeked_name(self, component, seeked_name):
        if component.GetName() == seeked_name:
            return True
        elif component.GetId() == self._wx_id_from_name(seeked_name):
            return True
        elif hasattr(component, "GetLabelText") and component.GetLabelText() == _(seeked_name):
            return True
        elif component.GetLabel() == _(seeked_name):
            return True
        return False

    def _wx_id_from_name(self, name):
        if name.startswith("wxID_"):
            return getattr(wx, name[2:])
        return None


class ObjectWithTruthValue(object):

    def __init__(self, truth_value):
        self.truth_value = truth_value

    def __nonzero__(self):
        return self.truth_value
