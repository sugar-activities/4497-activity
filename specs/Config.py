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


from os.path import abspath
import unittest

from timelinelib.config.dotfile import Config


class ConfigSpec(unittest.TestCase):

    def test_should_have_default_values_before_config_has_been_read(self):
        self.assertEquals(self.config.window_size, (900, 500))
        self.assertEquals(self.config.window_maximized, False)
        self.assertEquals(self.config.show_sidebar, True)
        self.assertEquals(self.config.show_legend, True)
        self.assertEquals(self.config.sidebar_width, 200)
        self.assertEquals(self.config.recently_opened, [])
        self.assertEquals(self.config.open_recent_at_startup, True)
        self.assertEquals(self.config.balloon_on_hover, True)
        self.assertEquals(self.config.week_start, "monday")
        self.assertEquals(self.config.get_use_wide_date_range(), False)
        self.assertEquals(self.config.get_use_inertial_scrolling(), False)

    def test_window_size_can_be_read_after_stored(self):
        self.config.window_size = (3, 20)
        self.assertEquals(self.config.window_size, (3, 20))

    def test_window_maximized_can_be_read_after_stored(self):
        self.config.window_maximized = True
        self.assertEquals(self.config.window_maximized, True)

    def test_show_sidebar_can_be_read_after_stored(self):
        self.config.show_sidebar = False
        self.assertEquals(self.config.show_sidebar, False)

    def test_show_legend_can_be_read_after_stored(self):
        self.config.show_legend = False
        self.assertEquals(self.config.show_legend, False)

    def test_sidebar_width_can_be_read_after_stored(self):
        self.config.sidebar_width = 20
        self.assertEquals(self.config.sidebar_width, 20)

    def test_recently_opened_can_be_read_after_stored(self):
        self.config.append_recently_opened(u"foo")
        self.assertEquals(self.config.recently_opened, [abspath(u"foo")])

    def test_open_recent_at_startup_can_be_read_after_stored(self):
        self.config.open_recent_at_startup = False
        self.assertEquals(self.config.open_recent_at_startup, False)

    def test_balloon_on_hover_can_be_read_after_stored(self):
        self.config.balloon_on_hover = False
        self.assertEquals(self.config.balloon_on_hover, False)

    def test_week_start_can_be_read_after_stored(self):
        self.config.week_start = "sunday"
        self.assertEquals(self.config.week_start, "sunday")

    def test_inertial_scrolling_can_be_read_after_stored(self):
        self.config.use_inertial_scrolling = False
        self.assertEquals(self.config.use_inertial_scrolling, False)

    def test_config_returns_wide_date_range_is_true_when_set_to_true(self):
        self.config.set_use_wide_date_range(True)
        self.assertTrue(self.config.get_use_wide_date_range())

    def test_config_returns_wide_date_range_is_false_when_set_to_false(self):
        self.config.set_use_wide_date_range(False)
        self.assertFalse(self.config.get_use_wide_date_range())

    def test_config_returns_use_inertial_scrolling_is_true_when_set_to_true(self):
        self.config.set_use_inertial_scrolling(True)
        self.assertTrue(self.config.get_use_inertial_scrolling())

    def test_config_returns_use_inertial_scrolling_is_false_when_set_to_false(self):
        self.config.set_use_inertial_scrolling(False)
        self.assertFalse(self.config.get_use_inertial_scrolling())

    def test_config_returns_wide_date_range_is_false_when_set_to_false_as_propety(self):
        self.config.use_wide_date_range = False
        self.assertFalse(self.config.use_wide_date_range)

    def test_config_returns_wide_date_range_is_true_when_set_to_true_as_propety(self):
        self.config.use_wide_date_range = True
        self.assertTrue(self.config.use_wide_date_range)

    def test_recently_opened_contains_last_5_entries(self):
        self.config.append_recently_opened("1")
        self.config.append_recently_opened("2")
        self.config.append_recently_opened("3")
        self.config.append_recently_opened("4")
        self.config.append_recently_opened("5")
        self.config.append_recently_opened("6")
        self.config.append_recently_opened("7")
        last_five = [abspath(entry) for entry in ["7", "6", "5", "4", "3"]]
        self.assertEquals(self.config.recently_opened, last_five)

    def test_recently_opened_list_does_not_contain_duplicates(self):
        self.config.append_recently_opened("foo")
        self.config.append_recently_opened("bar")
        self.config.append_recently_opened("foo")
        self.assertEquals(
            self.config.recently_opened,
            [abspath("foo"), abspath("bar")])

    def test_converts_recently_opened_path_to_unicode(self):
        self.config.append_recently_opened("non-unicode-path")
        self.assertTrue(isinstance(self.config.recently_opened[0], unicode))

    def test_recently_opened_does_not_store_special_tutorial_file(self):
        self.config.append_recently_opened(":tutorial:")
        self.assertEquals([], self.config.recently_opened)

    def test_setting_invalid_week_start_raises_value_error(self):
        def set_invalid_week():
            self.config.week_start = "friday"
        self.assertRaises(ValueError, set_invalid_week)

    def setUp(self):
        self.config = Config("")
