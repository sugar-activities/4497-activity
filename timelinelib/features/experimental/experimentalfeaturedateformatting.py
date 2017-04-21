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


import locale
import datetime
import re

from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature
from timelinelib.calendar.dateformatter import DateFormatter
from timelinelib.calendar import set_date_formatter


DISPLAY_NAME = "Locale date formats"
DESCRIPTION = """
              Use a date format specific for the locale setting of the host.
              """
YEAR = "3333"
MONTH = "11"
DAY = "22"


class ExperimentalFeatureDateFormatting(ExperimentalFeature, DateFormatter):

    def __init__(self):
        ExperimentalFeature.__init__(self, DISPLAY_NAME, DESCRIPTION)
        self.century = 0
        dt = create_locale_sample_date()
        self._construct_format(dt)

    def set_active(self, value):
        self.active = value
        if self.active:
            set_date_formatter(self)
        else:
            set_date_formatter(None)

    def format(self, year, month, day):
        lst = self._get_data_tuple(year, month, day)
        return self._dateformat % lst

    def parse(self, dt):
        MAP = {YEAR: (YEAR, YEAR[2:]), MONTH: (MONTH, MONTH[1:]), DAY: (DAY, DAY[1:])}

        def get_value(field):
            key1, key2 = MAP[field]
            try:
                return int(fields[self._field_positions[key1]])
            except:
                return int(fields[self._field_positions[key2]])
        try:
            bc = False
            if dt.startswith("-"):
                bc = True
                dt = dt[1:]
            fields = dt.split(self._separator)
            year = get_value(YEAR)
            if bc:
                year = -year
            return year, get_value(MONTH), get_value(DAY)
        except:
            raise ValueError()

    def separator(self):
        return self._separator

    def get_regions(self):
        try:
            year = self._field_positions[YEAR]
        except:
            year = self._field_positions[YEAR[2:]]
        return year, self._field_positions[MONTH], self._field_positions[DAY]

    def _construct_format(self, dt):
        self._separator = self._find_separator(dt)
        self._field_positions = self._get_field_positions(dt)
        self._dateformat = self._get_date_format_string(dt)

    def _find_separator(self, dt):
        return re.search('\D', dt[1:]).group()

    def _get_field_positions(self, dt):
        keys = dt.split(self._separator)
        return {keys[0]: 0, keys[1]: 1, keys[2]: 2}

    def _get_date_format_string(self, dt):
        try:
            MAP = {"3333": "%04d", "33": "%02d", "11": "%02d", "1": "%1d", "22": "%02d", "2": "%01d"}
            return self.separator().join([MAP[part] for part in dt.split(self.separator())])
        except:
            return "%04d-%02d-%02d"

    def _get_data_tuple(self, year, month, day):
        result = [0, 0, 0]
        try:
            result[self._field_positions[YEAR]] = year
            self.century = 0
        except:
            result[self._field_positions[YEAR[2:]]] = year % 100
            self.century = int(year / 100) * 100
        result[self._field_positions[MONTH]] = month
        result[self._field_positions[DAY]] = day
        return tuple(result)


def create_locale_sample_date():
    _set_default_time_locale()
    return _create_sample_datestring_using_locale_formatting()


def _set_default_time_locale():
    locale.setlocale(locale.LC_TIME, "")


def _create_sample_datestring_using_locale_formatting():
    return datetime.datetime(int(YEAR), int(MONTH), int(DAY)).strftime('%x')
