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


import time
import wx

from timelinelib.data.era import Era
from timelinelib.wxgui.dialogs.eraeditor.view import EraEditorDialog
from timelinelib.wxgui.framework import Controller


class ErasEditorDialogController(Controller):

    def on_init(self, db, config):
        self.db = db
        self.config = config
        self.eras = db.get_all_eras()
        self.view.SetEras(self.eras)

    def on_edit(self, evt):
        era = self.view.GetSelectedEra()
        dlg = EraEditorDialog(self.view, _("Edit an Era"), self.db.time_type, self.config, era)
        if dlg.ShowModal() == wx.ID_OK:
            self.view.UpdateEra(era)
        dlg.Destroy()

    def on_add(self, evt):
        era = self._create_era()
        dlg = EraEditorDialog(self.view, _("Add an Era"), self.db.time_type, self.config, era)
        if dlg.ShowModal() == wx.ID_OK:
            self.eras.append(era)
            self.view.AppendEra(era)
            self.db.save_era(era)
        dlg.Destroy()

    def on_remove(self, evt):
        era = self.view.GetSelectedEra()
        if era in self.eras:
            self.eras.remove(era)
            self.view.RemoveEra(era)

    def on_dclick(self, evt):
        self._edit(self.view.GetSelectedEra())

    def _edit(self, era):
        dlg = EraEditorDialog(self.view, _("Edit an Era"), self.db.time_type, self.config, era)
        if dlg.ShowModal() == wx.ID_OK:
            self.view.UpdateEra(era)
        dlg.Destroy()

    def _create_era(self):
        if self.db.time_type.is_date_time_type():
            start = self.db.time_type.parse_time("%s 00:00:00" % time.strftime("%Y-%m-%d"))
        else:
            start = self.db.time_type.now()
        end = start
        return Era(self.db.time_type, start, end, "New Era")
