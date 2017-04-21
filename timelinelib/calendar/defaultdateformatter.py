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


from timelinelib.calendar.dateformatter import DateFormatter


class DefaultDateFormatter(DateFormatter):

    def __init__(self):
        self._separator = "-"

    def format(self, year, month, day):
        return "%04d-%02d-%02d" % (year, month, day)

    def parse(self, dt):
        try:
            year, month, day = dt.rsplit(self._separator, 2)
        except:
            raise ValueError()
        return int(year), int(month), int(day)

    def separator(self):
        return self._separator

    def get_regions(self):
        year = 0
        month = 1
        day = 2
        return year, month, day
