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
from timelinelib.data import TimePeriod
from timelinelib.data import PeriodTooLongError


class EraEditorDialogController(Controller):

    def on_init(self, era, time_type):
        self.era = era
        self.time_type = time_type
        self._populate_view()

    def show_time_checkbox_on_checked(self, evt):
        self.view.SetShowTime(evt.IsChecked())

    def on_ok(self, evt):
        try:
            self._validate_input()
            self._update_era()
            self.view.Close()
        except ValueError:
            pass

    def _populate_view(self):
        self.view.SetStart(self.era.get_time_period().start_time)
        self.view.SetEnd(self.era.get_time_period().end_time)
        self.view.SetName(self.era.get_name())
        self.view.SetColor(self.era.get_color())
        self.view.SetShowTime(self._era_has_nonzero_time())

    def _era_has_nonzero_time(self):
        try:
            return self.era.get_time_period().has_nonzero_time()
        except Exception:
            return False

    def _validate_input(self):
        self._validate_name()
        self._validate_start()
        self._validate_end()
        self._validate_period()
        self._validate_period_length()

    def _validate_name(self):
        name = self.view.GetName()
        if name == "":
            msg = _("Field '%s' can't be empty.") % _("Name")
            self.view.DisplayInvalidName(msg)
            raise ValueError()

    def _validate_start(self):
        x = self.view.GetStart()
        if self.view.GetStart() is None:
            msg = _("Invalid start time.")
            self.view.DisplayInvalidStart(msg)
            raise ValueError(msg)

    def _validate_end(self):
        if self.view.GetEnd() is None:
            msg = _("Invalid end time.")
            self.view.DisplayInvalidEnd(msg)
            raise ValueError(msg)

    def _validate_period(self):
        start = self.view.GetStart()
        end = self.view.GetEnd()
        if start > end:
            msg = _("End must be > Start")
            self.view.DisplayInvalidStart(msg)
            raise ValueError(msg)

    def _validate_period_length(self):
        try:
            start = self.view.GetStart()
            end = self.view.GetEnd()
            TimePeriod(self.time_type, start, end)
        except PeriodTooLongError:
            msg = _("Entered period is too long.")
            self.view.DisplayInvalidPeriod(msg)
            raise ValueError(msg)

    def _update_era(self):
        w = self.view
        self.era.update(w.GetStart(), w.GetEnd(), w.GetName(), w.GetColor()[:3])
