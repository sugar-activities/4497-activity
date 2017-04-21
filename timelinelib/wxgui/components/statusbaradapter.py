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


class StatusBarAdapter(object):

    HIDDEN_EVENT_COUNT_COLUMN = 1
    READ_ONLY_COLUMN = 2

    def __init__(self, wx_status_bar):
        self.wx_status_bar = wx_status_bar
        self.wx_status_bar.SetFieldsCount(3)
        self.wx_status_bar.SetStatusWidths([-1, 200, 150])

    def set_text(self, text):
        self.wx_status_bar.SetStatusText(text)

    def set_hidden_event_count_text(self, text):
        self.wx_status_bar.SetStatusText(text, self.HIDDEN_EVENT_COUNT_COLUMN)

    def set_read_only_text(self, text):
        self.wx_status_bar.SetStatusText(text, self.READ_ONLY_COLUMN)
