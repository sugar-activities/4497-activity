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


import unittest

from mock import Mock

from timelinelib.config.dotfile import Config
from timelinelib.config.preferences import PreferencesEditor
from timelinelib.wxgui.dialogs.preferences import PreferencesDialog


class PreferencesDialogSpec(unittest.TestCase):

    def setUp(self):
        self.preferences_dialog = Mock(PreferencesDialog)
        self.config = Mock(Config)
        self.config.week_start = "monday"
        self.controller = PreferencesEditor(self.preferences_dialog, self.config)

    def test_opens_with_wide_date_range_if_set_in_config(self):
        self.config.get_use_wide_date_range.return_value = True
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_enable_wide_date_range.assert_called_with(True)

    def test_opens_with_nonwide_date_range_if_not_set_in_config(self):
        self.config.get_use_wide_date_range.return_value = False
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_enable_wide_date_range.assert_called_with(False)

    def test_config_changes_when_wide_date_range_changes(self):
        self.controller.on_use_wide_date_range_changed(False)
        self.config.set_use_wide_date_range.assert_called_with(False)

    def test_opens_with_inertial_scrolling_if_set_in_config(self):
        self.config.get_use_inertial_scrolling.return_value = True
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_use_inertial_scrolling.assert_called_with(True)

    def test_opens_with_no_inertial_scrolling_if_not_set_in_config(self):
        self.config.get_use_inertial_scrolling.return_value = False
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_use_inertial_scrolling.assert_called_with(False)

    def test_config_changes_when_inertial_scrolling_changes(self):
        self.controller.on_use_inertial_scrolling_changed(False)
        self.config.set_use_inertial_scrolling.assert_called_with(False)

    def test_opens_with_open_recent_if_set_in_config(self):
        self.config.get_open_recent_at_startup.return_value = True
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_open_recent_at_startup.assert_called_with(True)

    def test_opens_with_no_open_recent_if_not_set_in_config(self):
        self.config.get_open_recent_at_startup.return_value = False
        self.controller.initialize_controls()
        self.preferences_dialog.set_checkbox_open_recent_at_startup.assert_called_with(False)

    def test_config_changes_when_open_recent_changes(self):
        self.controller.on_open_recent_changed(False)
        self.config.set_use_inertial_scrolling.set_open_recent_at_startup(False)

    def test_opens_week_start_in_config(self):
        self.controller.initialize_controls()
        self.preferences_dialog.set_week_start.assert_called_with(0)

    def test_config_changes_when_week_start_changes(self):
        self.controller.on_week_start_changed(1)
        self.assertEqual("sunday", self.config.week_start)
