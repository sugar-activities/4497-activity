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

from timelinelib.application import TimelineApplication
from timelinelib.config.dotfile import Config
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.wxgui.dialogs.mainframe import MainFrame


class MainFrameSpec(unittest.TestCase):

    def test_used_db_open_factory_method_to_create_timeline(self):
        self.when_timeline_is_opened("foo.timeline")
        self.db_open.assert_called_with("foo.timeline", self.USE_WIDE_DATE_RANGE)

    def test_create_empty_timeline(self):
        self.controller.set_no_timeline()
        self.main_frame._display_timeline.assert_called_with(None)

    def test_adds_opened_timeline_to_recently_opened_list(self):
        self.when_timeline_is_opened("foo.timeline")
        self.config.append_recently_opened.assert_called_with("foo.timeline")
        self.main_frame._update_open_recent_submenu.assert_called_with()

    def test_displays_opened_timeline(self):
        opened_timeline = Mock()
        self.given_opening_returns(opened_timeline)
        self.when_timeline_is_opened()
        self.main_frame._display_timeline.assert_called_with(opened_timeline)

    def test_handles_open_timeline_failure(self):
        error = TimelineIOError("")
        self.given_opening_fails_with_error(error)
        self.when_timeline_is_opened()
        self.main_frame.handle_db_error.assert_called_with(error)

    def test_opens_play_window(self):
        opened_timeline = Mock()
        self.given_opening_returns(opened_timeline)
        self.when_timeline_is_opened()
        self.controller.on_play_clicked()
        self.main_frame.open_play_frame.assert_called_with(opened_timeline)

    def setUp(self):
        self.USE_WIDE_DATE_RANGE = False
        self.main_frame = Mock(MainFrame)
        self.db_open = Mock()
        self.config = Mock(Config)
        self.config.get_use_wide_date_range.return_value = self.USE_WIDE_DATE_RANGE
        self.controller = TimelineApplication(
            self.main_frame, self.db_open, self.config)

    def given_opening_fails_with_error(self, error):
        self.db_open.side_effect = error

    def given_opening_returns(self, timeline):
        self.db_open.return_value = timeline

    def when_timeline_is_opened(self, name=""):
        self.controller.open_timeline(name)
