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


from specs.utils import WxEndToEndTestCase


class WxEndToEndSpec(WxEndToEndTestCase):

    GUI = True
    IO = True

    def test_sidebar_gets_same_width_as_in_config(self):
        self.config.set_show_sidebar(True)
        self.config.set_sidebar_width(234)
        self.start_timeline_and([
            self.check_that_sidebar_width_equals(234),
        ])

    def check_that_sidebar_width_equals(self, expected_width):
        def check():
            self.assertEqual(
                expected_width,
                self.find_component("main_frame -> splitter").GetSashPosition())
        return check

    def test_can_create_new_event(self):
        self.start_timeline_and([
            self.click_menu_item("Timeline -> Create Event..."), [
                self.enter_text("event_editor -> text", "event text"),
                self.click_button("event_editor -> wxID_OK"),
            ],
        ])
        self.assert_written_timeline_has_one_event_with_text("event text")

    def assert_written_timeline_has_one_event_with_text(self, text):
        timeline = self.read_written_timeline()
        self.assertEqual(1, len(timeline.get_all_events()))
        self.assertEqual(text, timeline.get_all_events()[0].text)
