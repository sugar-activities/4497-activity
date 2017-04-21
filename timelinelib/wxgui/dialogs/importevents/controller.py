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


import os.path

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db import db_open
from timelinelib.wxgui.framework import Controller
from timelinelib.wxgui.utils import handle_db_error_by_crashing


class ImportEventsDialogController(Controller):

    def on_init(self, db):
        self._db = db
        self._db_to_import = None
        self._show_preview()

    def on_file_path_changed(self, event):
        self._show_preview()

    def on_ok_clicked(self, event):
        if not self._db_to_import:
            return
        try:
            self._db.import_db(self._db_to_import)
        except TimelineIOError, e:
            handle_db_error_by_crashing(e)
        else:
            self.view.Close()

    def _show_preview(self):
        if not os.path.exists(self.view.GetFilePath()):
            self._set_error(_("File does not exist."))
        else:
            try:
                db_to_import = db_open(self.view.GetFilePath())
            except Exception, e:
                self._set_error(_("Unable to load events: %s.") % str(e))
            else:
                if db_to_import.get_time_type() != self._db.get_time_type():
                    self._set_error(_("The selected timeline has a different time type."))
                else:
                    self._set_success(db_to_import, _("%d events will be imported." % len(db_to_import.get_all_events())))

    def _set_success(self, db_to_import, text):
        self._db_to_import = db_to_import
        self.view.SetSuccess(text)

    def _set_error(self, text):
        self._db_to_import = None
        self.view.SetError(text)
