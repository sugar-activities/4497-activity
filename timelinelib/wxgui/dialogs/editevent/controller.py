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


import wx

from timelinelib.data import Event
from timelinelib.data import PeriodTooLongError
from timelinelib.data import Subevent
from timelinelib.data import TimePeriod
from timelinelib.time.timeline import delta_from_days
from timelinelib.utils import ex_msg
from timelinelib.wxgui.framework import Controller


class EditEventDialogController(Controller):

    def on_init(self, config, time_type, event_repository, timeline, start, end, event):
        self.config = config
        self.timeline = timeline
        self.time_type = time_type
        self.event_repository = event_repository
        self._set_values(start, end, event)
        self._set_view_content()
        self.view.SetFocusOnFirstControl()

    def on_period_checkbox_changed(self, event):
        end = self.view.GetEnd()
        start = self.view.GetStart()
        if start is not None and end is not None:
            if (event.IsChecked() and start >= end):
                if self.timeline.get_time_type().is_date_time_type():
                    delta = delta_from_days(1)
                else:
                    delta = 1
                try:
                    self.view.SetEnd(start + delta)
                except TypeError:
                    pass
        self.view.ShowToTime(event.IsChecked())

    def on_show_time_checkbox_changed(self, event):
        self.view.SetShowTime(event.IsChecked())

    def on_locked_checkbox_changed(self, event):
        self._enable_disable_ends_today()

    def on_container_changed(self, event):
        self._enable_disable_ends_today()
        self._enable_disable_locked()

    def on_enlarge_click(self, event):
        self.reduced_size = self.view.GetSize()
        self.reduced_pos = self.view.GetPosition()
        screen_width, screen_height = wx.DisplaySize()
        dialog_size = (screen_width * 0.9, screen_height * 0.8)
        dialog_pos = (screen_width * 0.05, screen_height * 0.05)
        self._set_position_and_size(dialog_pos, dialog_size)

    def on_reduce_click(self, event):
        self._set_position_and_size(self.reduced_pos, self.reduced_size)

    def on_ok_clicked(self, event):
        try:
            self._create_or_update_event()
        except ValueError:
            self.view.DisplayErrorMessage(_("Invalid Date or Time"))

    def _create_or_update_event(self):
        try:
            self._get_and_verify_input()
            self._save_event()
            if self.view.IsAddMoreChecked():
                self.name = ""
                self.event = None
                self.view.SetName(self.name)
                self.view.ClearEventData()
                self.view.SetFocusOnFirstControl()
            else:
                if self.opened_from_menu:
                    self.config.event_editor_show_period = self.view.GetShowPeriod()
                    self.config.event_editor_show_time = self.view.GetShowTime()
                self.view.EndModalOk()
        except ValueError:
            pass

    def _set_values(self, start, end, event):
        self.event = event
        self.opened_from_menu = self.event is None and start is None
        if self.event is not None:
            self.start = self.event.get_time_period().start_time
            self.end = self.event.get_time_period().end_time
            self.name = self.event.get_text()
            self.category = self.event.get_category()
            self.fuzzy = self.event.get_fuzzy()
            self.locked = self.event.get_locked()
            self.ends_today = self.event.get_ends_today()
        else:
            self.start = start
            self.end = end
            self.name = ""
            self.category = None
            self.fuzzy = False
            self.locked = False
            self.ends_today = False

    def _set_view_content(self):
        if self.event is not None:
            self.view.SetEventData(self.event.data)
            if self.event.is_subevent():
                self.view.SetContainer(self.event.container)
            else:
                self.view.SetContainer(None)
        else:
            self.view.SetContainer(None)
        self.view.SetStart(self.start)
        self.view.SetEnd(self.end)
        self.view.SetName(self.name)
        self.view.SetCategory(self.category)
        if self.event:
            self.view.SetShowPeriod(self.end > self.start)
            self.view.SetShowTime(self._event_has_nonzero_time())
        else:
            if self.opened_from_menu:
                self.view.SetShowPeriod(self.config.event_editor_show_period)
                self.view.SetShowTime(self.config.event_editor_show_time)
            else:
                self.view.SetShowPeriod(self.end > self.start)
                self.view.SetShowTime(self._event_has_nonzero_time())
        self.view.SetShowAddMoreCheckbox(self.event is None)
        self.view.SetFuzzy(self.fuzzy)
        self.view.SetLocked(self.locked)
        self.view.SetEndsToday(self.ends_today)

    def _get_and_verify_input(self):
        self.name = self.view.GetName()
        self.fuzzy = self.view.GetFuzzy()
        self.locked = self.view.GetLocked()
        self.ends_today = self.view.GetEndsToday()
        self.category = self.view.GetCategory()
        start = self._get_start_from_view()
        if self._dialog_has_signalled_invalid_input(start):
            self.view.DisplayInvalidStart(_("Invalid Start- date or time"))
            raise ValueError()
        end = self._get_end_from_view()
        if self._dialog_has_signalled_invalid_input(end):
            self.view.DisplayInvalidStart(_("Invalid End- date or time"))
            raise ValueError()
        if self.event is not None and self.locked:
            self._verify_that_time_has_not_been_changed(start, end)
        self.start = self._validate_and_save_start(self._get_start_from_view())
        self.end = self._validate_and_save_end(self._get_end_from_view())
        self._validate_period()
        self._validate_ends_today()
        self.container = self.view.GetContainer()

    def _get_start_from_view(self):
        try:
            return self.view.GetStart()
        except ValueError, ex:
            self.view.DisplayInvalidStart("%s" % ex_msg(ex))

    def _get_end_from_view(self):
        if self.view.GetShowPeriod():
            try:
                return self.view.GetEnd()
            except ValueError, ex:
                self.view.DisplayInvalidEnd("%s" % ex_msg(ex))
        else:
            return self._get_start_from_view()

    def _dialog_has_signalled_invalid_input(self, time):
        return time is None

    def _verify_that_time_has_not_been_changed(self, start, end):
        self._exception_if_start_has_changed(start)
        if not self.ends_today:
            self._exception_if_end_has_changed(end)

    def _exception_if_start_has_changed(self, start):
        if not self.time_type.eventtimes_equals(self.start, start):
            self.view.SetStart(self.start)
            self._exception_when_start_or_end_has_changed()

    def _exception_if_end_has_changed(self, end):
        if not self.time_type.eventtimes_equals(self.end, end):
            self.view.SetEnd(self.end)
            self._exception_when_start_or_end_has_changed()

    def _exception_when_start_or_end_has_changed(self):
        error_message = _("You can't change time when the Event is locked")
        self.view.DisplayInvalidStart(error_message)
        raise ValueError()

    def _save_event(self):
        if self.event is None:
            self._create_new_event()
        else:
            self._update_event()
        self.event.data = self.view.GetEventData()
        self._save_event_to_db()

    def _update_event(self):
        container_selected = (self.container is not None)
        if container_selected:
            if self.event.is_subevent():
                if self.event.container == self.container:
                    self.event.update(self.start, self.end, self.name,
                                      self.category, self.fuzzy, self.locked,
                                      self.ends_today)
                else:
                    self._change_container()
            else:
                self._add_event_to_container()
        else:
            if self.event.is_subevent():
                self._remove_event_from_container()
                pass
            else:
                self.event.update(self.start, self.end, self.name,
                                  self.category, self.fuzzy, self.locked,
                                  self.ends_today)

    def _remove_event_from_container(self):
        self.event.container.unregister_subevent(self.event)
        self.timeline.delete_event(self.event)
        self._create_new_event()

    def _add_event_to_container(self):
        self.timeline.delete_event(self.event)
        self._create_subevent()

    def _change_container(self):
        self.event.container.unregister_subevent(self.event)
        self.container.register_subevent(self.event)

    def _create_new_event(self):
        if self.container is not None:
            self._create_subevent()
        else:
            self.event = Event(self.time_type, self.start, self.end, self.name,
                               self.category, self.fuzzy, self.locked,
                               self.ends_today)

    def _create_subevent(self):
        if self._is_new_container(self.container):
            self._add_new_container()
        self.event = Subevent(self.time_type, self.start, self.end, self.name,
                              self.category, self.container)

    def _is_new_container(self, container):
        return container not in self.timeline.get_containers()

    def _add_new_container(self):
        max_id = 0
        for container in self.timeline.get_containers():
            if container.cid() > max_id:
                max_id = container.cid()
        max_id += 1
        self.container.set_cid(max_id)
        self._save_container_to_db()

    def _validate_and_save_start(self, start):
        if start is None:
            raise ValueError()
        return start

    def _validate_and_save_end(self, end):
        if end is None:
            raise ValueError()
        if self.ends_today:
            end_time = self.time_type.now()
        else:
            end_time = end
        if end_time < self.start:
            self.view.DisplayInvalidStart(_("End must be > Start"))
            raise ValueError()
        return end_time

    def _validate_period(self):
        try:
            TimePeriod(self.time_type, self.start, self.end)
        except PeriodTooLongError:
            self.view.DisplayErrorMessage(_("Entered period is too long."))
            raise ValueError()

    def _validate_ends_today(self):
        if self.ends_today and self.start > self.time_type.now():
            self.view.DisplayErrorMessage(_("Start time > Now."))
            raise ValueError()

    def _save_event_to_db(self):
        try:
            self.event_repository.save(self.event)
        except Exception, e:
            self.view.display_db_exception(e)

    def _save_container_to_db(self):
        try:
            self.event_repository.save(self.container)
        except Exception, e:
            self.view.display_db_exception(e)

    def _event_has_nonzero_time(self):
        try:
            time_type = self.time_type
            time_period = TimePeriod(time_type, self.start, self.end)
            return time_period.has_nonzero_time()
        except Exception:
            return False

    def _enable_disable_ends_today(self):
        enable = (self._container_not_selected() and
                  not self.view.GetLocked() and
                  self._start_is_in_history())
        self.view.EnableEndsToday(enable)

    def _enable_disable_locked(self):
        enable = self._container_not_selected()
        self.view.EnableLocked(enable)

    def _container_not_selected(self):
        return self.view.GetContainer() is None

    def _start_is_in_history(self):
        if self.start is None:
            return False
        return self.start < self.timeline.time_type.now()

    def _set_position_and_size(self, pos, size):
        self.view.SetPosition(pos)
        self.view.SetSize(size)
