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


from timelinelib.data import Category
from timelinelib.data import Event
from timelinelib.data import Events
from timelinelib.data import Eras
from timelinelib.data.undohandler import UndoHandler
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.time.gregoriantime import GregorianTimeType
from timelinelib.utilities.observer import Observable
from timelinelib.utilities.observer import STATE_CHANGE_ANY
from timelinelib.utilities.observer import STATE_CHANGE_CATEGORY
from timelinelib.features.experimental.experimentalfeatures import EVENT_DONE
from timelinelib.features.experimental.experimentalfeatures import experimental_feature
from timelinelib.time.timeline import Time


class MemoryDB(Observable):

    def __init__(self):
        Observable.__init__(self)
        self.path = ""
        self._events = Events()
        self._eras = Eras()
        self.displayed_period = None
        self.hidden_categories = []
        self.save_disabled = False
        self.time_type = GregorianTimeType()
        self.saved_now = self.time_type.now()
        self.readonly = False
        self._undo_handler = UndoHandler(self)
        self._save_callback = None
        self._should_lock = False
        self._undo_enabled = False
        self._redo_enabled = False

    def is_saved(self):
        return self._save_callback is not None

    def get_should_lock(self):
        return self._should_lock

    def set_should_lock(self, should_lock):
        self._should_lock = should_lock

    def register_save_callback(self, callback):
        self._save_callback = callback

    def get_time_type(self):
        return self.time_type

    def set_time_type(self, time_type):
        self.time_type = time_type
        if not time_type is None:
            try:
                self.saved_now = time_type.now()
            except NotImplementedError:
                self.saved_now = Time(0,0)

    def is_read_only(self):
        return self.readonly

    def set_readonly(self):
        self.readonly = True
        self._notify(STATE_CHANGE_ANY)

    def supported_event_data(self):
        return ["description", "icon", "alert", "hyperlink", "progress"]

    def search(self, search_string):
        return self._events.search(search_string)

    def get_events(self, time_period):
        return self._events.get_in_period(time_period)

    def get_all_events(self):
        return self._events.get_all()

    def get_first_event(self):
        return self._events.get_first()

    def get_last_event(self):
        return self._events.get_last()

    def save_events(self, events):
        try:
            for event in events:
                self._events.save_event(event)
        except Exception, e:
            raise TimelineIOError("Saving event failed: %s" % e)
        else:
            self._save_if_not_disabled(STATE_CHANGE_ANY)

    def save_event(self, event):
        self.save_events([event])

    def delete_event(self, event_or_id, save=True):
        def delete(event):
            self._events.delete_event(event)
        error_text = "Deleting event failed"
        self._process_event(event_or_id, delete, error_text, save)

    def get_all_eras(self):
        return self._eras.get_all()

    def save_era(self, era):
        try:
            self._eras.save_era(era)
        except Exception, e:
            raise TimelineIOError("Saving Era failed: %s" % e)
        else:
            self._save_if_not_disabled(STATE_CHANGE_CATEGORY)

    def get_max_cid(self):
        max_cid = 0
        for event in self.get_all_events():
            if event.is_container():
                max_cid = max(event.cid(), max_cid)
        return max_cid

    @experimental_feature(EVENT_DONE)
    def mark_event_as_done(self, event_or_id, save=True):
        def mark_as_done(event):
            if not event.is_container():
                event.set_progress(100)
        error_text = "Mark event Done failed"
        self._process_event(event_or_id, mark_as_done, error_text, save)

    def _process_event(self, event_or_id, process_func, error_text, save=False):
        try:
            process_func(self._get_event(event_or_id))
        except Exception, e:
            raise TimelineIOError("%s: %s" % (error_text, e))
        else:
            if save:
                self._save_if_not_disabled(STATE_CHANGE_ANY)

    def _get_event(self, event_or_id):
        if isinstance(event_or_id, Event):
            return event_or_id
        else:
            return self.find_event_with_id(event_or_id)

    def get_categories(self):
        return self._events.get_categories()

    def get_containers(self):
        return self._events.get_containers()

    def save_category(self, category):
        try:
            self._events.save_category(category)
        except Exception, e:
            raise TimelineIOError("Saving category failed: %s" % e)
        else:
            self._save_if_not_disabled(STATE_CHANGE_CATEGORY)

    def loaded(self):
        self._undo_handler.enable(True)
        self._undo_handler.save()

    def get_category_by_name(self, name):
        return self._events.get_category_by_name(name)

    def delete_category(self, category_or_id):
        if isinstance(category_or_id, Category):
            category = category_or_id
        else:
            category = self._events.get_category_with_id(category_or_id)
        if category in self.hidden_categories:
            self.hidden_categories.remove(category)
        try:
            self._events.delete_category(category)
        except Exception, e:
            raise TimelineIOError("Deleting category failed: %s" % e)
        else:
            self._save_if_not_disabled(STATE_CHANGE_CATEGORY)

    def get_saved_now(self):
        return self.saved_now
    
    def set_saved_now(self,time):
        self.saved_now = time
        self.time_type.set_saved_now(time)        

    def load_view_properties(self, view_properties):
        view_properties.displayed_period = self.displayed_period
        for cat in self._events.get_categories():
            visible = cat not in self.hidden_categories
            view_properties.set_category_visible(cat, visible)

    def save_view_properties(self, view_properties):
        if view_properties.displayed_period is not None:
            if not view_properties.displayed_period.is_period():
                raise TimelineIOError(_("Displayed period must be > 0."))
            self.displayed_period = view_properties.displayed_period
        self.hidden_categories = []
        for cat in self._events.get_categories():
            if not view_properties.is_category_visible(cat):
                self.hidden_categories.append(cat)
        self._save_if_not_disabled()

    def disable_save(self):
        self.save_disabled = True

    def enable_save(self, call_save=True):
        if self.save_disabled is True:
            self.save_disabled = False
            if call_save is True:
                self._save_if_not_disabled()

    def place_event_after_event(self, event_to_place, target_event):
        self._events.place_event_after_event(event_to_place, target_event)
        self._save_if_not_disabled(STATE_CHANGE_ANY)

    def place_event_before_event(self, event_to_place, target_event):
        self._events.place_event_before_event(event_to_place, target_event)
        self._save_if_not_disabled(STATE_CHANGE_ANY)

    def undo(self):
        if self._undo_handler.undo():
            self._events = self._undo_handler.get_data()
            self._save_if_not_disabled(STATE_CHANGE_ANY)
            self._undo_handler.enable(True)

    def redo(self):
        if self._undo_handler.redo():
            self._events = self._undo_handler.get_data()
            self._save_if_not_disabled(STATE_CHANGE_ANY)
            self._undo_handler.enable(True)

    def notify_undo_redo_states(self, undo_state, redo_state):
        self._undo_enabled = undo_state
        self._redo_enabled = redo_state

    def undo_enabled(self):
        return self._undo_enabled

    def redo_enabled(self):
        return self._redo_enabled

    def find_event_with_id(self, event_id):
        for e in self._events.get_all():
            if e.get_id() == event_id:
                return e
        return None

    def _save_enabled(self):
        return self.save_disabled is False

    def _save_if_not_disabled(self, notification=None):
        if self._save_enabled():
            if self._save_callback is not None:
                self._save_callback()
            self._undo_handler.save()
            if notification is not None:
                self._notify(notification)

    def get_displayed_period(self):
        """
        Inheritors can call this method to get the displayed period used in
        load_view_properties and save_view_properties.
        """
        return self.displayed_period

    def set_displayed_period(self, period):
        """
        Inheritors can call this method to set the displayed period used in
        load_view_properties and save_view_properties.
        """
        self.displayed_period = period

    def get_hidden_categories(self):
        """
        Inheritors can call this method to get the hidden categories used in
        load_view_properties and save_view_properties.
        """
        return self.hidden_categories

    def set_hidden_categories(self, hidden_categories):
        """
        Inheritors can call this method to set the hidden categories used in
        load_view_properties and save_view_properties.
        """
        self.hidden_categories = []
        for cat in hidden_categories:
            if cat not in self._events.get_categories():
                raise ValueError("Category '%s' not in db." % cat.get_name())
            self.hidden_categories.append(cat)

    def import_db(self, db):
        if self.get_time_type() != db.get_time_type():
            raise Exception("Import failed: time type does not match")
        self.disable_save()
        self._import_events_from(db)
        self.enable_save()
        self._notify(STATE_CHANGE_ANY)

    def _import_events_from(self, db):
        def get_max_container_id():
            max_container_id = 0
            for event in self.get_all_events():
                if event.is_container():
                    if event.cid() > max_container_id:
                        max_container_id = event.cid()
            return max_container_id

        def set_imported_ids(max_cid):
            for event in db.get_all_events():
                if event.is_container():
                    event.set_cid(event.cid() + max_cid)
                elif event.is_subevent():
                    event.set_container_id(event.get_container_id() + max_cid)
        max_cid = get_max_container_id()
        set_imported_ids(max_cid)
        for event in db.get_all_events():
            self.save_event(self._create_imported_event(event))

    def _create_imported_event(self, event):
        clone = event.clone()
        clone.set_category(self._create_imported_category(event.get_category()))
        return clone

    def _create_imported_category(self, category):
        if category is None:
            return None
        elif self._has_category_with_name(category.get_name()):
            return self.get_category_by_name(category.get_name())
        else:
            imported_parent = self._create_imported_category(category._get_parent())
            category = category.clone().set_parent(imported_parent)
            self.save_category(category)
            return category

    def _has_category_with_name(self, name):
        for category in self.get_categories():
            if category.get_name() == name:
                return True
        return False

    def compress(self):
        self._events.compress()
        self.save_events(self._events.get_all())
