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
from timelinelib.proxies.sidebar import SidebarProxy


class CategoryFinderDialogController(Controller):

    def on_init(self, db, mainframe):
        self.db = db
        self.mainframe = mainframe
        self.view.SetCategories(self._get_categories_names())

    def on_char(self, evt):
        target = self.view.GetTarget()
        self.view.SetCategories(self._get_categories_names())

    def on_check(self, evt):
        SidebarProxy(self.mainframe).check_categories(self._get_categories())

    def on_uncheck(self, evt):
        SidebarProxy(self.mainframe).uncheck_categories(self._get_categories())

    def _get_categories_names(self):
        target = self.view.GetTarget()
        return sorted([category.name for category in self.db.get_categories()
                      if category.name.upper().startswith(target.upper())])

    def _get_categories(self):
        target = self.view.GetTarget()
        return sorted([category for category in self.db.get_categories()
                      if category.name.upper().startswith(target.upper())])
