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


from timelinelib.wxgui.framework import Controller
from timelinelib.db.exceptions import TimelineIOError


FORWARD = 0
BACKWARD = 1
BOTH = 2


class DuplicateEventDialogController(Controller):

    def on_init(self, db, event):
        self.db = db
        self.event = event
        self.view.SetCount(1)
        self.view.SetFrequency(1)
        self.view.SetDirection(FORWARD)
        self.view.SelectMovePeriodFnAtIndex(0)

    def on_ok(self, evt):
        self.create_duplicates_and_save()

    def create_duplicates_and_save(self):
        self.view.SetWaitCursor()
        events, nbr_of_missing_dates = self._create_duplicates()
        self._save_duplicates(events, nbr_of_missing_dates)
        self.view.SetDefaultCursor()

    def _create_duplicates(self):
        if self.event.is_container():
            return self._create_container_duplicates(self.event)
        else:
            return self._create_event_duplicates(self.event)

    def _create_container_duplicates(self, container):
        """
        Duplicating a container is a little more complicated than duplicating an ordinary event
        because you have to duplicate all subevents also.
        For each cloned container (period) we calculate the periods of all subevents in this
        container. This makes it possible to create one container and all it's subevents for
        each container period.
        The container must also get e unique id and the subevents has to be rgistered with
        the container.
        """
        periods_with_subperiods, nbr_of_missing_dates = self._repeat_container_period(container)
        events = []
        cid = self.db.get_max_cid()
        for period_with_subperiods in periods_with_subperiods:
            cid += 1
            container_period, sub_periods = period_with_subperiods
            event = self._clone_and_add_event_to_list(container, container_period, events)
            event.set_cid(cid)
            for subevent, subevent_period in sub_periods:
                new_subevent = self._clone_and_add_event_to_list(subevent, subevent_period, events)
                event.register_subevent(new_subevent)
        return events, nbr_of_missing_dates

    def _create_event_duplicates(self, event):
        periods, nbr_of_missing_dates = self._repeat_event_period(event)
        events = []
        for period in periods:
            self._clone_and_add_event_to_list(event, period, events)
        return events, nbr_of_missing_dates

    def _clone_and_add_event_to_list(self, event, period, events):
        evt = event.clone()
        evt.update_period(period.start_time, period.end_time)
        events.append(evt)
        return evt

    def _save_duplicates(self, events, nbr_of_missing_dates):
        try:
            self.db.save_events(events)
            if nbr_of_missing_dates > 0:
                self.view.HandleDateErrors(nbr_of_missing_dates)
            self.view.Close()
        except TimelineIOError, e:
            self.view.HandleDbError(e)

    def _repeat_container_period(self, event):
        period = self.event.get_time_period()
        move_period_fn = self.view.get_move_period_fn()
        frequency = self.view.get_frequency()
        repetitions = self.view.get_count()
        direction = self.view.get_direction()
        periods_with_subperiods = []
        nbr_of_missing_dates = 0
        for index in self._calc_indicies(direction, repetitions):
            sub_periods = []
            for subevent in event.get_subevents():
                sub_period = move_period_fn(subevent.get_time_period(), index * frequency)
                sub_periods.append((subevent, sub_period))
            new_period = move_period_fn(period, index * frequency)
            if new_period is None:
                nbr_of_missing_dates += 1
            else:
                periods_with_subperiods.append((new_period, sub_periods))
        return (periods_with_subperiods, nbr_of_missing_dates)

    def _repeat_event_period(self, event):
        period = event.get_time_period()
        move_period_fn = self.view.GetMovePeriodFn()
        frequency = self.view.GetFrequency()
        repetitions = self.view.GetCount()
        direction = self.view.GetDirection()
        periods = []
        nbr_of_missing_dates = 0
        for index in self._calc_indicies(direction, repetitions):
            new_period = move_period_fn(period, index * frequency)
            if new_period is None:
                nbr_of_missing_dates += 1
            else:
                periods.append(new_period)
        return (periods, nbr_of_missing_dates)

    def _calc_indicies(self, direction, repetitions):
        if direction == FORWARD:
            return range(1, repetitions + 1)
        elif direction == BACKWARD:
            return range(-repetitions, 0)
        elif direction == BOTH:
            indicies = range(-repetitions, repetitions + 1)
            indicies.remove(0)
            return indicies
        else:
            raise Exception("Invalid direction.")
