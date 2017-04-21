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
from timelinelib.db.objects import Container
from timelinelib.db.objects import Subevent
from timelinelib.db.strategies import DefaultContainerStrategy


class DefaultContainerStartegySpec(unittest.TestCase):

    def test_construction(self):
        self.given_strategy_with_container()
        self.assertEqual(self.container, self.strategy.container)

    def test_first_registered_event_decides_container_period(self):
        self.given_strategy_with_container()
        self.given_subevent1()
        self.strategy.register_subevent(self.subevent1)
        self.assert_equal_start(self.container, self.subevent1)
        self.assert_equal_end(self.container, self.subevent1)

    def test_second_registered_event_expands_container_period(self):
        # Container event:   +-------+
        # New sub-event:                 +-------+
        self.given_container_with_two_events_with_nonoverlapping_periods()
        self.assert_equal_start(self.container, self.subevent1)
        self.assert_equal_end(self.container, self.subevent2)

    def test_removing_one_event_contracts_container_period(self):
        # Container event:   +-------+
        # New sub-event:                 +-------+
        self.given_container_with_two_events_with_nonoverlapping_periods()
        self.strategy.unregister_subevent(self.subevent1)
        self.assert_equal_start(self.container, self.subevent2)
        self.assert_equal_end(self.container, self.subevent2)

    def test_updating_subevent_expands_container_period(self):
        # Container event:   +-------+
        # New sub-event:                 +-------+
        self.given_container_with_two_events_with_nonoverlapping_periods()
        self.subevent2.time_period.end_time = self.time("2000-05-01 10:01:01")
        self.strategy.update(self.subevent2)
        self.assert_equal_start(self.container, self.subevent1)
        self.assert_equal_end(self.container, self.subevent2)

    def test_adding_partial_overlapping_event_moves_overlapped_event_backwards(self):
        # Container event:   +-------+
        # New sub-event:          +-------+
        self.given_container_with_two_events_with_overlapping_periods()
        self.assert_start_equals_end(self.subevent2, self.subevent1)

    def test_adding_partial_overlapping_event_moves_overlapped_event_forward(self):
        # Container event:        +-------+
        # New sub-event:     +-------+
        self.given_container_with_two_events_with_overlapping_periods_reversed_order()
        self.assert_start_equals_end(self.subevent2, self.subevent1)

    def test_adding_event_with_same_period_moves_overlapped_event_forward(self):
        # Container event:   +-------+
        # New sub-event:     +-------+
        self.given_container_with_two_events_with_same_periods()
        self.assert_start_equals_end(self.subevent1, self.subevent2)

    def test_adding_event_with_same_start_moves_overlapped_event_forward(self):
        # Container event:   +-------+
        # New sub-event:     +---+
        self.given_container_with_two_events_with_same_start_time()
        self.assert_start_equals_end(self.subevent1, self.subevent2)

    def test_overlapping_nonperiod_event_at_begining_moves_nonperiod_event_backwards(self):
        # Container event:    +
        # New sub-event:     +----------+
        self.given_strategy_with_container()
        self.given_event_overlapping_point_event()
        self.assert_start_equals_start(self.subevent1, self.subevent2)

    def test_overlapping_nonperiod_event_at_end_moves_nonperiod_event_forward(self):
        # Container event:             +
        # New sub-event:     +----------+
        self.given_strategy_with_container()
        self.given_event_overlapping_point_event2()
        self.assert_start_equals_end(self.subevent1, self.subevent2)

    def given_container_with_two_events_with_nonoverlapping_periods(self):
        self.given_strategy_with_container()
        self.given_two_events_with_nonoverlapping_periods()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_container_with_two_events_with_overlapping_periods(self):
        self.given_strategy_with_container()
        self.given_two_overlapping_events()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_container_with_two_events_with_overlapping_periods_reversed_order(self):
        self.given_strategy_with_container()
        self.given_two_overlapping_events()
        self.strategy.register_subevent(self.subevent2)
        self.strategy.register_subevent(self.subevent1)

    def given_container_with_two_events_with_same_periods(self):
        self.given_strategy_with_container()
        self.given_two_events_with_same_period()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_container_with_two_events_with_same_start_time(self):
        self.given_strategy_with_container()
        self.given_two_events_with_same_start_time()
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_strategy_with_container(self):
        self.container = Container(self.db.get_time_type(),
                                   self.time("2000-01-01 10:01:01"),
                                   self.time("2000-01-01 10:01:01"), "Container1")
        self.strategy = DefaultContainerStrategy(self.container)

    def given_event_overlapping_point_event(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-05-01 10:02:01"),
                                  self.time("2000-05-01 10:02:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-05-01 10:01:01"),
                                  self.time("2000-07-01 10:01:01"), "Container1")
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_event_overlapping_point_event2(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-07-01 10:00:01"),
                                  self.time("2000-07-01 10:00:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-05-01 10:01:01"),
                                  self.time("2000-07-01 10:01:01"), "Container1")
        self.strategy.register_subevent(self.subevent1)
        self.strategy.register_subevent(self.subevent2)

    def given_two_overlapping_events(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-06-01 10:01:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-05-01 10:01:01"),
                                  self.time("2000-07-01 10:01:01"), "Container1")

    def given_two_events_with_same_period(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-06-01 10:01:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-06-01 10:01:01"), "Container1")

    def given_two_events_with_same_start_time(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-06-01 10:01:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-04-01 10:01:01"), "Container1")

    def given_two_events_with_nonoverlapping_periods(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-01-01 10:01:01"),
                                  self.time("2000-02-01 10:01:01"), "Container1")
        self.subevent2 = Subevent(self.db.get_time_type(),
                                  self.time("2000-03-01 10:01:01"),
                                  self.time("2000-04-01 10:01:01"), "Container1")

    def given_subevent1(self):
        self.subevent1 = Subevent(self.db.get_time_type(),
                                  self.time("2000-01-01 10:01:01"),
                                  self.time("2000-02-01 10:01:01"), "Container1")

    def assert_equal_start(self, obj1, obj2):
        self.assertEqual(obj1.time_period.start_time, obj2.time_period.start_time)

    def assert_equal_end(self, obj1, obj2):
        self.assertEqual(obj1.time_period.end_time, obj2.time_period.end_time)

    def assert_start_equals_end(self, obj1, obj2):
        self.assertEqual(obj1.time_period.start_time, obj2.time_period.end_time)

    def assert_start_equals_start(self, obj1, obj2):
        self.assertEqual(obj1.time_period.start_time, obj2.time_period.start_time)

    def time(self, tm):
        return self.db.get_time_type().parse_time(tm)

    def setUp(self):
        self.db = MemoryDB()
        self.now = self.db.get_time_type().now()
        self.time_type = self.db.get_time_type()
