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


import collections

from timelinelib.data.category import clone_categories_list
from timelinelib.data.event import clone_event_list
from timelinelib.data.idnumber import get_process_unique_id
from timelinelib.data.container import Container


class InvalidOperationError(Exception):
    pass


class Events(object):

    def __init__(self, categories=None, events=None):
        if categories is None:
            self._categories = []
        else:
            self._categories = categories
        if events is None:
            self._events = []
        else:
            self._events = events

    def get_all(self):
        return list(self._events)

    def get_first(self):
        if len(self.get_all()) == 0:
            return None
        return min(self.get_all(), key=lambda e: e.get_time_period().start_time)

    def get_last(self):
        if len(self.get_all()) == 0:
            return None
        return max(self.get_all(), key=lambda e: e.get_time_period().end_time)

    def get_in_period(self, time_period):
        def include_event(event):
            if not event.inside_period(time_period):
                return False
            return True
        return [e for e in self._events if include_event(e)]

    def search(self, search_string):
        return _generic_event_search(self._events, search_string)

    def get_categories(self):
        return list(self._categories)

    def get_category_by_name(self, name):
        for category in self._categories:
            if category.get_name() == name:
                return category

    def get_category_with_id(self, event_id):
        for category in self._categories:
            if category.get_id() == event_id:
                return category
        return None

    def save_category(self, category):
        self._ensure_category_exists_for_update(category)
        self._ensure_category_name_available(category)
        self._ensure_parent_exists(category)
        self._ensure_no_circular_parent(category)
        if not self._does_category_exists(category):
            category.set_id(get_process_unique_id())
            self._categories.append(category)

    def delete_category(self, category):
        if category not in self._categories:
            raise InvalidOperationError("Category not in db.")
        self._categories.remove(category)
        category.set_id(None)
        # Loop to update parent attribute on children
        for cat in self._categories:
            if cat._get_parent() == category:
                cat.set_parent(category._get_parent())
        # Loop to update category for events
        for event in self._events:
            if event.get_category() == category:
                event.set_category(category._get_parent())

    def _ensure_category_exists_for_update(self, category):
        message = "Updating a category that does not exist."
        if category.has_id():
            if not self._does_category_exists(category):
                raise InvalidOperationError(message)

    def _ensure_category_name_available(self, category):
        message = "A category with name %r already exists." % category.get_name()
        ids = self._get_ids_with_name(category.get_name())
        if self._does_category_exists(category):
            if ids != [category.get_id()]:
                raise InvalidOperationError(message)
        else:
            if ids != []:
                raise InvalidOperationError(message)

    def _get_ids_with_name(self, name):
        ids = []
        for category in self.get_categories():
            if category.get_name() == name:
                ids.append(category.get_id())
        return ids

    def _does_category_exists(self, a_category):
        for stored_category in self.get_categories():
            if stored_category.get_id() == a_category.get_id():
                return True
        return False

    def _ensure_parent_exists(self, category):
        message = "Parent category not in db."
        if (category._get_parent() is not None and category._get_parent() not in self._categories):
            raise InvalidOperationError(message)

    def _ensure_no_circular_parent(self, category):
        message = "Circular category parent."
        parent = category._get_parent()
        while parent is not None:
            if parent == category:
                raise InvalidOperationError(message)
            else:
                parent = parent._get_parent()

    def save_event(self, event):
        self._ensure_event_exists_for_update(event)
        self._ensure_event_category_exists(event)
        if event not in self._events:
            self._events.append(event)
            event.set_id(get_process_unique_id())
            if event.is_subevent():
                self._register_subevent(event)

    def delete_event(self, event):
        if event not in self._events:
            raise InvalidOperationError("Event not in db.")
        if event.is_subevent():
            self._unregister_subevent(event)
        if event.is_container():
            for subevent in event.events:
                self._events.remove(subevent)
        self._events.remove(event)
        event.set_id(None)

    def _unregister_subevent(self, subevent):
        container_events = self.get_containers()
        containers = {}
        for container in container_events:
            containers[container.cid()] = container
        try:
            container = containers[subevent.cid()]
            container.unregister_subevent(subevent)
            if len(container.events) == 0:
                self._events.remove(container)
        except:
            pass

    def get_containers(self):
        return [event for event in self._events if event.is_container()]

    def _ensure_event_exists_for_update(self, event):
        message = "Updating an event that does not exist."
        if event.has_id():
            if not self._does_event_exists(event):
                raise InvalidOperationError(message)

    def _does_event_exists(self, an_event):
        for stored_event in self.get_all():
            if stored_event.get_id() == an_event.get_id():
                return True
        return False

    def _ensure_event_category_exists(self, event):
        message = "Event's category not in db."
        if (event.get_category() is not None and event.get_category() not in self._categories):
            raise InvalidOperationError(message)

    def _register_subevent(self, subevent):
        container_events = [event for event in self._events
                            if event.is_container()]
        containers = {}
        for container in container_events:
            key = container.cid()
            containers[key] = container
        try:
            container = containers[subevent.cid()]
            container.register_subevent(subevent)
        except:
            subevent_id = subevent.cid()
            if subevent_id == 0:
                subevent_id = self._get_max_container_id(container_events) + 1
                subevent.set_cid(subevent_id)
            name = "[%d]Container" % subevent_id
            container = Container(subevent.time_type,
                                  subevent.get_time_period().start_time,
                                  subevent.get_time_period().end_time, name)
            self.save_event(container)
            self._register_subevent(subevent)

    def _get_max_container_id(self, container_events):
        event_id = 0
        for event in container_events:
            if event_id < event.cid():
                event_id = event.cid()
        return event_id

    def place_event_after_event(self, event_to_place, target_event):
        if event_to_place == target_event:
            return
        self._events.remove(event_to_place)
        new_index = self._events.index(target_event) + 1
        self._events.insert(new_index, event_to_place)

    def place_event_before_event(self, event_to_place, target_event):
        if event_to_place == target_event:
            return
        self._events.remove(event_to_place)
        new_index = self._events.index(target_event)
        self._events.insert(new_index, event_to_place)

    def clone(self):
        (categories, events) = clone_data(self._categories, self._events)
        return Events(categories, events)

    def compress(self):
        rows = self._place_events_on_rows()
        self._set_events_order_from_rows(rows)

    def _set_events_order_from_rows(self, rows):
        evs = []
        for key in sorted(rows.keys()):
            evs.extend(rows[key])
        self._events = evs

    def _place_events_on_rows(self):
        rows = collections.defaultdict(lambda: [])
        for event in self._length_sort():
            inx = 0
            while True:
                if self.fits_on_row(rows[inx], event):
                    event.r = inx
                    rows[inx].append(event)
                    break
                inx += 1
        return rows

    def _length_sort(self):
        reordered_events = [event for event in self._events if not event.is_subevent()]
        reordered_events = self._sort_by_length(reordered_events)
        subevents = [event for event in self._events if event.is_subevent()]
        reordered_events.extend(subevents)
        return reordered_events

    def _sort_by_length(self, events):
        return sorted(events, key=self._event_length, reverse=True)

    def _event_length(self, evt):
        return evt.get_time_period().delta()

    def fits_on_row(self, row_events, event):
        for ev in row_events:
            if ev.overlaps(event):
                return False
        return True


def _generic_event_search(events, search_string):
    def match(event):
        target = search_string.lower()
        description = event.get_data("description")
        if description is None:
            description = ""
        else:
            description = description.lower()
        return target in event.get_text().lower() or target in description

    def mean_time(event):
        return event.mean_time()
    matches = [event for event in events if match(event)]
    matches.sort(key=mean_time)
    return matches


def clone_data(categories, events):
    categories, catclones = clone_categories_list(categories)
    events = clone_event_list(events)
    for event in events:
        try:
            event.set_category(catclones[event.get_category()])
        except KeyError:
            event.set_category(None)
    return categories, events
