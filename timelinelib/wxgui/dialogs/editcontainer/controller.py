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


from timelinelib.data import Container
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.wxgui.framework import Controller


class EditContainerDialogController(Controller):

    """
    This controller is responsible for two things:

    1. creating a new Container event
    2. updating properties of an existing Container event

    When creating a new Container event the result is NOT stored in the
    timeline database. This happens later when the first event added to the
    container is saved to the database.

    The reason for this behavior is that we don't want to have empty containers
    in the database. When updating the properties of an existing Container
    event the changes are stored in the timeline database.
    """

    def on_init(self, db, container):
        self.view.PopulateCategories()
        self._set_initial_values_to_member_variables(db, container)
        self._set_view_initial_values()

    def on_ok_clicked(self, event):
        self.name = self.view.GetName()
        self.category = self.view.GetCategory()
        try:
            try:
                self._verify_name()
                if self.container_exists:
                    self._update_container()
                else:
                    self._create_container()
                self.view.EndModalOk()
            except ValueError:
                pass
        except TimelineIOError, e:
            self.view.HandleDbError(e)

    def get_container(self):
        return self.container

    def _set_initial_values_to_member_variables(self, db, container):
        self.db = db
        self.container = container
        self.container_exists = (self.container is not None)
        if self.container_exists:
            self.name = self.container.get_text()
            self.category = self.container.get_category()
        else:
            self.name = ""
            self.category = None

    def _set_view_initial_values(self):
        self.view.SetName(self.name)
        self.view.SetCategory(self.category)

    def _verify_name(self):
        name_is_invalid = (self.name == "")
        if name_is_invalid:
            msg = _("Field '%s' can't be empty.") % _("Name")
            self.view.DisplayInvalidName(msg)
            raise ValueError()

    def _update_container(self):
        self.container.update_properties(self.name, self.category)
        self.db.save_event(self.container)

    def _create_container(self):
        time_type = self.db.get_time_type()
        start = time_type.now()
        end = start
        self.container = Container(time_type, start, end, self.name,
                                   self.category)
