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


import datetime
import unittest

from mock import Mock

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.editors.duplicateevent import BACKWARD
from timelinelib.editors.duplicateevent import BOTH
from timelinelib.editors.duplicateevent import DuplicateEventEditor
from timelinelib.editors.duplicateevent import FORWARD
from timelinelib.time import PyTimeType
from timelinelib.wxgui.dialogs.duplicateevent import DuplicateEventDialog


class duplicate_event_dialog_spec_base(unittest.TestCase):

    def setUp(self):
        self.controller = DuplicateEventEditor(
            self._create_view_mock(),
            self._create_db_mock(),
            self._create_event())

    def _create_view_mock(self):
        self.view = Mock(DuplicateEventDialog)
        self.view.get_move_period_fn.return_value = self._create_move_period_fn_mock()
        return self.view

    def _create_move_period_fn_mock(self):
        self.move_period_fn = Mock()
        self.move_period_fn.return_value = TimePeriod(
            PyTimeType(),
            datetime.datetime(2010, 8, 1),
            datetime.datetime(2010, 8, 1))
        return self.move_period_fn

    def _create_db_mock(self):
        self.db = Mock(MemoryDB)
        self.db.get_time_type.return_value = PyTimeType()
        return self.db

    def _create_event(self):
        self.event = Event(
            self.db.get_time_type(),
            datetime.datetime(2010, 1, 1),
            datetime.datetime(2010, 1, 1),
            "foo",
            category=None)
        return self.event

    def _duplicate_with(self, count, freq, direction):
        self.view.get_count.return_value = count
        self.view.get_frequency.return_value = freq
        self.view.get_direction.return_value = direction
        self.controller.create_duplicates_and_save()


class a_newly_initialized_dialog(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.controller.initialize()

    def test_number_of_duplicates_should_be_1(self):
        self.view.set_count.assert_called_with(1)

    def test_first_period_should_be_selected(self):
        self.view.select_move_period_fn_at_index.assert_called_with(0)

    def test_frequency_should_be_one(self):
        self.view.set_frequency.assert_called_with(1)

    def test_direction_should_be_forward(self):
        self.view.set_direction.assert_called_with(FORWARD)


class when_duplicating_event_with_default_settings(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self._duplicate_with(count=1, freq=1, direction=FORWARD)

    def test_one_new_event_is_saved(self):
        self.assertEquals(1, self.db.save_event.call_count)

    def test_the_new_event_gets_period_from_move_period_fn(self):
        new_event = self.db.save_event.call_args[0][0]
        new_period = new_event.time_period
        expected_period = TimePeriod(
            PyTimeType(),
            datetime.datetime(2010, 8, 1),
            datetime.datetime(2010, 8, 1))
        self.assertEquals(expected_period, new_period)

    def test_the_new_event_should_not_be_the_same_as_the_existing(self):
        new_event = self.db.save_event.call_args[0][0]
        self.assertNotEquals(self.event, new_event)

    def test_the_dialog_should_close(self):
        self.assertTrue(self.view.close.assert_called)


class when_saving_duplicated_event_fails(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.db.save_event.side_effect = TimelineIOError
        self._duplicate_with(count=1, freq=1, direction=FORWARD)

    def test_the_failure_is_handled(self):
        self.assertTrue(self.view.handle_db_error.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)


class when_event_can_not_be_duplicated(duplicate_event_dialog_spec_base):

    def setUp(self):
        duplicate_event_dialog_spec_base.setUp(self)
        self.move_period_fn.return_value = None
        self._duplicate_with(count=1, freq=1, direction=FORWARD)

    def test_the_failure_is_handled(self):
        self.view.handle_date_errors.assert_called_with(1)

    def test_the_dialog_is_closed(self):
        self.assertTrue(self.view.close.called)


class a_diloag_with_different_settings(duplicate_event_dialog_spec_base):

    def _assert_move_period_called_with(self, num_list):
        self.assertEquals(
            [((self.event.time_period, num), {}) for num in num_list],
            self.move_period_fn.call_args_list)

    def test_count_1_freq_1_direction_forward(self):
        self._duplicate_with(count=1, freq=1, direction=FORWARD)
        self._assert_move_period_called_with([1])

    def test_count_1_freq_1_direction_backward(self):
        self._duplicate_with(count=1, freq=1, direction=BACKWARD)
        self._assert_move_period_called_with([-1])

    def test_count_1_freq_1_direction_both(self):
        self._duplicate_with(count=1, freq=1, direction=BOTH)
        self._assert_move_period_called_with([-1, 1])

    def test_count_2_freq_1_direction_forward(self):
        self._duplicate_with(count=2, freq=1, direction=FORWARD)
        self._assert_move_period_called_with([1, 2])

    def test_count_2_freq_1_direction_backward(self):
        self._duplicate_with(count=2, freq=1, direction=BACKWARD)
        self._assert_move_period_called_with([-2, -1])

    def test_count_2_freq_1_direction_both(self):
        self._duplicate_with(count=2, freq=1, direction=BOTH)
        self._assert_move_period_called_with([-2, -1, 1, 2])

    def test_count_1_freq_2_direction_forward(self):
        self._duplicate_with(count=1, freq=2, direction=FORWARD)
        self._assert_move_period_called_with([2])

    def test_count_1_freq_2_direction_backward(self):
        self._duplicate_with(count=1, freq=2, direction=BACKWARD)
        self._assert_move_period_called_with([-2])

    def test_count_1_freq_2_direction_both(self):
        self._duplicate_with(count=1, freq=2, direction=BOTH)
        self._assert_move_period_called_with([-2, 2])
