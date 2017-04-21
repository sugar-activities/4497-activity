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

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Category
from timelinelib.db.objects import Container
from timelinelib.db.objects import Subevent


class ContainerSpec(unittest.TestCase):

    def testContainerCanHaveSubevents(self):
        self.given_period_subevent()
        self.given_default_container()
        self.container.register_subevent(self.event)
        self.assertEqual(1, len(self.container.events))

    def testSubeventsCanBeUnregistered(self):
        self.given_period_subevent()
        self.given_default_container()
        self.container.register_subevent(self.event)
        self.assertEqual(1, len(self.container.events))
        self.container.unregister_subevent(self.event)
        self.assertEqual(0, len(self.container.events))

    def testNameCanBeUpdated(self):
        self.given_default_container()
        new_name = "new text"
        self.container.update_properties(new_name)
        self.assertEqual(new_name, self.container.text)

    def testNameAndCategoryCanBeUpdated(self):
        self.given_default_container()
        new_name = "new text"
        new_category = Category("cat", (255,0,0), (255,0,0), True)
        self.container.update_properties(new_name, new_category)
        self.assertEqual(new_category, self.container.category)

    def testCidCanBeChanged(self):
        self.given_default_container()
        self.container.set_cid(99)
        self.assertEqual(99, self.container.cid())

    def given_default_container(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "container")

    def given_period_subevent(self):
        self.event = Subevent(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                              self.time("2000-01-03 10:01:01"), "evt")

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class ContainerConstructorSpec(unittest.TestCase):

    def testContainerPropertiesDefaultsToFalse(self):
        self.given_default_container()
        self.assertEqual(-1, self.container.cid())
        self.assertEqual(False, self.container.fuzzy)
        self.assertEqual(False, self.container.locked)
        self.assertEqual(False, self.container.ends_today)
        self.assertEqual(True, self.container.is_container())
        self.assertEqual(False, self.container.is_subevent())
        self.assertEqual(None, self.container.category)

    def testContainerPropertyCidCanBeSetAtConstruction(self):
        self.given_container_with_cid()
        self.assertEqual(99, self.container.cid())

    def given_default_container(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "container")

    def given_container_with_cid(self):
        self.container = Container(self.db.get_time_type(), self.now, self.now, "evt", cid=99)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
