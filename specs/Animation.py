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

from timelinelib.play.playcontroller import Animation
from timelinelib.db.backends.memory import MemoryDB
from specs.utils import py_period


class AnimationTest(unittest.TestCase):

    def setUp(self):
        self.timeline = MemoryDB()

    def test_can_move_period_without_zooming(self):
        a = Animation(self.timeline,
                py_period("1 Jan 2010", "2 Jan 2010"),
                2,
                py_period("3 Jan 2010", "4 Jan 2010"))
        a.change_current_period(1)
        self.assertEquals(a.current_period, py_period("2 Jan 2010", "3 Jan 2010"))
