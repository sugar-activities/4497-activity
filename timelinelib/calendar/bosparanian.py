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


import timelinelib.time.timeline as timeline
from timelinelib.calendar.gregorian import Gregorian, GregorianUtils

class Bosparanian(Gregorian):

    def __init__(self, year, month, day, hour, minute, second):
        self.utils = BosparanianUtils
        self.timeclass = timeline.BosparanianTime
        if not self.utils.is_valid(year, month, day):
            raise ValueError("Invalid bosparanian date %s-%s-%s" % (year, month, day))
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __repr__(self):
        return "Bosparanian<%d-%02d-%02d %02d:%02d:%02d>" % self.to_tuple()


class BosparanianUtils(GregorianUtils):
    @classmethod
    def is_valid(cls, year, month, day):
        return (month >= 1 and month <= 13 and day >= 1 and day <= cls.days_in_month(year, month))
    
    @classmethod    
    def days_in_month(cls, year, month):
        if month in [13]:
            return 5
        return 30
    
    @classmethod
    def is_leap_year(cls, year):
        return False
    
    @classmethod
    def from_absolute_day(cls, bosparanian_day):
        """
        Converts a day number, counted from 1st PRA, 0 BF to standard bosparanian calendar date
        """
        bosp_day=bosparanian_day-(365*100*73)+3 # shift by 73 centuries and align week
        year = bosp_day // 365
        d = bosp_day - (year * 365)
        if d >= 360:
            month = 13
            day = d-359
            return (year,month,day)
        month = d // 30 + 1
        day = d % 30 + 1
        return (year,month,day)
    
    @classmethod    
    def to_absolute_day(cls, year, month, day):
        """
        Converts a bosparanian date given as year, month, and day, to a day number counted from 1st PRA 0 BF
        """
        bosp_day = year * 365
        bosp_day += ((month - 1) // 13) * 365
        m = (month - 1) % 13 
        bosp_day += m * 30
        bosp_day += day - 1
        bosparanian_day=bosp_day+(365*100*73)-3 # shift by 73 centuries and align week
        return bosparanian_day
    
    @classmethod
    def calendar_week(cls, time):
        """
        returns number of week in year
        """
        def windsday_week_1(year):
            pra_4 = cls.from_date(year, 1, 4).to_time()
            return pra_4 - timeline.delta_from_days(pra_4.get_day_of_week())
        def days_between(end, start):
            return end.julian_day - start.julian_day
        def days_since_windsday_week_1(time):
            year = cls.from_time(time).year
            diff = days_between(end=time, start=windsday_week_1(year + 1))
            if diff >= 0:
                return diff
            diff = days_between(end=time, start=windsday_week_1(year))
            if diff >= 0:
                return diff
            diff = days_between(end=time, start=windsday_week_1(year - 1))
            if diff >= 0:
                return diff
            raise ValueError("should not end up here")
        return days_since_windsday_week_1(time) / 7 + 1
    
    @classmethod
    def from_time(cls, time):
        (year, month, day) = cls.from_absolute_day(time.julian_day)
        (hour, minute, second) = time.get_time_of_day()
        return Bosparanian(year, month, day, hour, minute, second)
    
    @classmethod
    def from_date(cls, year, month, day):
        return Bosparanian(year, month, day, 0, 0, 0)
