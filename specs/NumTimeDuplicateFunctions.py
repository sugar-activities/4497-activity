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

from timelinelib.db.objects import TimePeriod
from timelinelib.time import NumTimeType
from timelinelib.time.numtime import move_period


class NumTimeDuplicateFunctionsSpec(unittest.TestCase):

    def setUp(self):
        self.period = TimePeriod(NumTimeType(), 1, 2)

    def test_move_period_adds_given_number_of_delta(self):
        new_period = move_period(self.period, 6)
        self.assertEquals(TimePeriod(NumTimeType(), 7, 8), new_period)
