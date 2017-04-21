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


from timelinelib.data.timeperiod import TimePeriod


DEFAULT_ERA_COLOR = (200, 200, 200)


class Era(object):
    """
    A clearly defined period of time of arbitrary but well-defined length.

    In addition to the time period attributes (start, end) an Era also has a
    name and a color. The color is used to display the Era period as a
    background color in a timeline.
    """

    def __init__(self, time_type, start_time, end_time, name, color=DEFAULT_ERA_COLOR):
        self.id = None
        self.time_type = time_type
        self.update(start_time, end_time, name, color)

    def __eq__(self, other):
        return (isinstance(other, Era) and
                self.get_time_type() == other.get_time_type() and
                self.get_id() == other.get_id() and
                self.get_time_period() == other.get_time_period() and
                self.get_name() == other.get_name() and
                self.get_color() == other.get_color())

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return self.get_time_period().start_time > other.get_time_period().start_time

    def __lt__(self, other):
        return self.get_time_period().start_time < other.get_time_period().start_time

    def update(self, start_time, end_time, name, color=DEFAULT_ERA_COLOR):
        self.time_period = TimePeriod(self.time_type, start_time, end_time)
        self.name = name.strip()
        self.color = color

    def clone(self):
        new_event = Era(self.time_type, self.time_period.start_time,
                        self.time_period.end_time, self.name, self.color)
        return new_event

    def set_id(self, era_id):
        self.id = era_id
        return self

    def get_id(self):
        return self.id

    def has_id(self):
        return self.id is not None

    def set_time_period(self, time_period):
        self.time_period = time_period
        return self

    def get_time_period(self):
        return self.time_period

    def set_name(self, name):
        self.name = name.strip()
        return self

    def get_name(self):
        return self.name

    def set_color(self, color):
        self.color = color
        return self

    def get_color(self):
        return self.color

    def set_time_type(self, time_type):
        self.time_type = time_type
        return self

    def get_time_type(self):
        return self.time_type

    def inside_period(self, time_period):
        return self.time_period.overlap(time_period)
