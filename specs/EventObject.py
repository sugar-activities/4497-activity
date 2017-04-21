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

from timelinelib.db.objects import Event
from timelinelib.db.backends.memory import MemoryDB


class EventSpec(unittest.TestCase):

    def testEventPropertyEndsTodayCanBeUpdated(self):
        self.given_default_point_event()
        self.event.update(self.now, self.now, "evt", ends_today=True)
        self.assertEqual(True, self.event.ends_today)

    def testEventPropertyFuzzyCanBeUpdated(self):
        self.given_default_point_event()
        self.event.update(self.now, self.now, "evt", fuzzy=True)
        self.assertEqual(True, self.event.fuzzy)

    def testEventPropertyLockedCanBeUpdated(self):
        self.given_default_point_event()
        self.event.update(self.now, self.now, "evt", locked=True)
        self.assertEqual(True, self.event.locked)

    def testEventPropertyEndsTodayCantBeSetOnLockedEvent(self):
        self.given_default_point_event()
        self.event.update(self.now, self.now, "evt", locked=True)
        self.event.update(self.now, self.now, "evt", ends_today=True)
        self.assertEqual(False, self.event.ends_today)

    def testEventPropertyEndsTodayCantBeUnsetOnLockedEvent(self):
        self.given_default_point_event()
        self.event.update(self.now, self.now, "evt", locked=True, ends_today=True)
        self.assertEqual(True, self.event.ends_today)
        self.event.update(self.now, self.now, "evt", ends_today=False)
        self.assertEqual(True, self.event.ends_today)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def given_default_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt")

    def given_point_event(self):
        self.event = Event(self.db.get_time_type(), self.time("2000-01-01 10:01:01"),
                           self.time("2000-01-01 10:01:01"), "evt")


class EventCosntructorSpec(unittest.TestCase):

    def testEventPropertiesDefaultsToFalse(self):
        self.given_default_point_event()
        self.assertEqual(False, self.event.fuzzy)
        self.assertEqual(False, self.event.locked)
        self.assertEqual(False, self.event.ends_today)
        self.assertEqual(False, self.event.is_container())
        self.assertEqual(False, self.event.is_subevent())

    def testEventPropertyFuzzyCanBeSetAtConstruction(self):
        self.given_fuzzy_point_event()
        self.assertEqual(True, self.event.fuzzy)

    def testEventPropertyLockedCanBeSetAtConstruction(self):
        self.given_locked_point_event()
        self.assertEqual(True, self.event.locked)

    def testEventPropertyEndsTodayCanBeSetAtConstruction(self):
        self.given_point_event_wich_ends_today()
        self.assertEqual(True, self.event.ends_today)

    def given_default_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt")

    def given_point_event_wich_ends_today(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", ends_today=True)

    def given_fuzzy_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", fuzzy=True)

    def given_locked_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt", locked=True)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()


class EventFunctionsSpec(unittest.TestCase):

    def test_zero_time_span(self):
        self.given_default_point_event()
        self.assertEqual(self.event.time_type.get_zero_delta(), self.event.time_span())

    def given_default_point_event(self):
        self.event = Event(self.db.get_time_type(), self.now, self.now, "evt")

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
