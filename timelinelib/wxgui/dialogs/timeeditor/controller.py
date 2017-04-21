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
from timelinelib.wxgui.utils import display_error_message
from timelinelib.utils import ex_msg


class TimeEditorDialogController(Controller):

    def on_init(self, time_type, time):
        self.time_type = time_type
        self.view.SetTime(time)
        self.view.ShowTime(False)

    def show_time_checkbox_on_checked(self, evt):
        self.view.ShowTime(evt.IsChecked())

    def ok_button_clicked(self, evt):
        try:
            time = self.view.GetTime()
            if time is None:
                raise ValueError(_("Invalid date"))
            if self.time_type.is_date_time_type():
                if not self.view.ShowTimeIsChecked():
                    gt = self.time_type.get_utils().from_time(time)
                    gt.hour = 12
                    self.view.SetTime(gt.to_time())
        except ValueError, ex:
            display_error_message(ex_msg(ex))
        else:
            self.view.Close()
