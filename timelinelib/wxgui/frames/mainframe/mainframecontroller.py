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


import getpass
import os

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.wxgui.utils import display_error_message
from timelinelib.wxgui.utils import display_warning_message
from timelinelib.wxgui.utils import get_user_ack


class LockedException(Exception):
    pass


class MainFrameController(object):

    def __init__(self, main_frame, db_open_fn, config):
        self.main_frame = main_frame
        self.db_open_fn = db_open_fn
        self.config = config
        self.timeline = None

    def on_started(self, application_arguments):
        if application_arguments.has_files():
            self.open_or_create_timeline(application_arguments.get_first_file())
        elif self.config.has_recently_opened_files():
            self.open_timeline_if_exists(self.config.get_latest_recently_opened_file())

    def open_or_create_timeline(self, path):
        self.open_timeline(path)

    def open_timeline_if_exists(self, path):
        if os.path.exists(path):
            self.open_timeline(path)
        else:
            display_error_message(_("File '%s' does not exist.") % path, self.main_frame)

    def open_timeline(self, path, timetype=None, save_current_data=True):
        if save_current_data:
            self.main_frame.save_current_timeline_data()
        try:
            new_db = self.db_open_fn(path, timetype=timetype)
            self.timeline = new_db
            self.timeline.loaded()
        except TimelineIOError, e:
            self.main_frame.handle_db_error(e)
            self.timelinepath = None
        else:
            self.config.append_recently_opened(path)
            self.main_frame.update_open_recent_submenu()
            self.timeline.path = path
            self.main_frame.display_timeline(self.timeline)
            self.timelinepath = path
            self.last_changed = self._get_modification_date()
        self.main_frame.update_navigation_menu_items()
        self.main_frame.enable_disable_menus()

    def set_no_timeline(self):
        self.timeline = None
        self.main_frame.display_timeline(None)

    def set_timeline_in_readonly_mode(self):
        try:
            self.timeline.set_readonly()
            self.main_frame.set_timeline_readonly()
        except:
            pass

    def week_starts_on_monday(self):
        return self.config.week_start == "monday"

    def ok_to_edit(self):
        if self.timeline is None:
            return True
        if self.timeline.is_read_only():
            return False
        if self._locked():
            display_warning_message("The Timeline is Locked by someone else.\nTry again later")
            return False
        if self._timeline_path_doesnt_exists_yet():
            self._lock()
            return True
        last_changed = self._get_modification_date()
        if last_changed > self.last_changed:
            ack = get_user_ack(_("Someoneelse has changed the Timeline.\nYou have two choices!\n  1. Set Timeline in Read-Only mode.\n  2. Synchronize Timeline.\n\nDo you want to Synchronize?"))
            if ack:
                self.reload_from_disk()
            else:
                self.set_timeline_in_readonly_mode()
            return False
        if last_changed > 0:
            self._lock()
        return True

    def calc_events_distance(self, event1, event2):
        if event1.time_period.start_time <= event2.time_period.start_time:
            distance = (event2.time_period.start_time -
                        event1.time_period.end_time)
        else:
            distance = (event1.time_period.start_time -
                        event2.time_period.end_time)
        return distance

    def _timeline_path_doesnt_exists_yet(self):
        return not os.path.exists(self.timelinepath)

    def edit_ends(self):
        if self.timeline is not None:
            if self._the_lock_is_mine():
                self.last_changed = self._get_modification_date()
                self._unlock()

    def timeline_is_readonly(self):
        return self.timeline is not None and self.timeline.is_read_only()

    def _get_modification_date(self):
        try:
            return os.path.getmtime(self.timelinepath)
        except:
            return 0

    def reload_from_disk(self):
        timeline_canvas = self.main_frame.main_panel.timeline_panel.timeline_canvas
        vp = timeline_canvas.get_view_properties()
        displayed_period = vp.get_displayed_period()
        self.open_timeline(self.timelinepath, save_current_data=False)
        vp.set_displayed_period(displayed_period)
        timeline_canvas.redraw_timeline()

    def _lock(self):
        fp = None
        if not self.timeline.get_should_lock():
            return
        try:
            ts = self._get_timestamp_string()
            path = self._get_lockpath()
            fp = open(path, "w")
            fp.write("%s\n%s\n%s" % (getpass.getuser(), ts, os.getpid()))
        except Exception:
            msg = _("Unable to take lock on %s\nThis means you can't edit the timeline.\nCheck if you have write access to this directory.") % self.timelinepath
            display_warning_message(msg, self.main_frame)
            raise LockedException()
        finally:
            if fp is not None:
                fp.close()

    def _get_lockpath(self):
        return "%s.lock" % self.timelinepath

    def _get_timestamp_string(self):
        now = self.timeline.time_type.now()
        return self.timeline.time_type.time_string(now)

    def _locked(self):
        lockpath = self._get_lockpath()
        return os.path.exists(lockpath)

    def _unlock(self):
        lockpath = self._get_lockpath()
        if os.path.exists(lockpath):
            try:
                os.remove(lockpath)
            except WindowsError, ex:
                if ex.winerror == 32:
                    self._report_other_process_uses_lockfile(lockpath)
                else:
                    raise ex

    def _report_other_process_uses_lockfile(self, lockpath):
        message = _("""The lockfile used to protect the timeline from concurrent updates is opened by another program or process.
This lockfile must be removed in order be able to continue editing the timeline!
The lockfile is found at: %s""") % lockpath
        display_warning_message(message)

    def _the_lock_is_mine(self):
        fp = None
        try:
            user = getpass.getuser()
            pid = os.getpid()
            lockpath = self._get_lockpath()
            fp = open(lockpath, "r")
            lines = fp.readlines()
            lines = [line.strip() for line in lines]
            return lines[0] == user and lines[2] == "%s" % pid
        except:
            return False
        finally:
            if fp is not None:
                fp.close()
