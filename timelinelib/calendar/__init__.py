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


from timelinelib.calendar.defaultdateformatter import DefaultDateFormatter
from timelinelib.calendar.bosparaniandateformatter import BosparanianDateFormatter


date_formatter = None


def set_date_formatter(formatter):
    global date_formatter
    date_formatter = formatter


def get_date_formatter():
    global date_formatter
    if date_formatter is None:
        date_formatter = DefaultDateFormatter()
    return date_formatter
