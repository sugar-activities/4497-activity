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


from timelinelib.db import db_open
from timelinelib.wxgui.components.timelinepanel import TimelinePanel


class DummyConfig(object):

    def __init__(self):
        self.window_size = (100, 100)
        self.window_pos = (100, 100)
        self.window_maximized = False
        self.show_sidebar = True
        self.show_legend = True
        self.sidebar_width = 200
        self.recently_opened = []
        self.open_recent_at_startup = False
        self.balloon_on_hover = True
        self.week_start = "monday"
        self.use_inertial_scrolling = False

    def get_sidebar_width(self):
        return self.sidebar_width

    def get_show_sidebar(self):
        return self.show_sidebar

    def get_show_legend(self):
        return self.show_legend

    def get_balloon_on_hover(self):
        return self.balloon_on_hover


class DummyStatusBarAdapter(object):

    def set_text(self, text):
        pass

    def set_hidden_event_count_text(self, text):
        pass

    def set_read_only_text(self, text):
        pass


class DummyMainFrame(object):

    def enable_disable_menus(self):
        pass

    def edit_ends(self):
        pass

    def ok_to_edit(self):
        return False


class TimelineComponent(TimelinePanel):

    def __init__(self, parent):
        TimelinePanel.__init__(
            self, parent, DummyConfig(), self.handle_db_error,
            DummyStatusBarAdapter(), DummyMainFrame())
        self.activated()

    def handle_db_error(self, e):
        pass

    def open_timeline(self, path):
        timeline = db_open(path)
        self.timeline_canvas.set_timeline(timeline)
        self.sidebar.category_tree.set_timeline_view(
            self.timeline_canvas.get_timeline(),
            self.timeline_canvas.get_view_properties()
        )

    def clear_timeline(self):
        self.timeline_canvas.set_timeline(None)
        self.sidebar.category_tree.set_no_timeline_view()
