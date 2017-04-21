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


from timelinelib.data.idnumber import get_process_unique_id


class InvalidOperationError(Exception):
    pass


class Eras(object):
    """
    The list of all eras defined for a timeline.

    Contains function for cloning of the whole list which is a
    necessary operation for undo/redo operations.
    """

    def __init__(self, eras=None):
        if eras is None:
            self._eras = []
        else:
            self._eras = eras

    def clone(self):
        return Eras(clone_era_list(self._eras))

    def get_all(self):
        return self._eras

    def get_in_period(self, time_period):
        def include_era(era):
            if not era.inside_period(time_period):
                return False
            return True
        return [e for e in self._eras if include_era(e)]

    def save_era(self, era):
        self._ensure_era_exists_for_update(era)
        if era not in self._eras:
            self._eras.append(era)
            era.set_id(get_process_unique_id())

    def delete_era(self, era):
        if era not in self._eras:
            raise InvalidOperationError("era not in db.")
        self._eras.remove(era)
        era.set_id(None)

    def _ensure_era_exists_for_update(self, era):
        message = "Updating an era that does not exist."
        if era.has_id():
            if not self._does_era_exists(era):
                raise InvalidOperationError(message)

    def _does_era_exists(self, an_era):
        for stored_era in self.get_all():
            if stored_era.get_id() == an_era.get_id():
                return True
        return False


def clone_era_list(eralist):
    eras = []
    for era in eralist:
        new_era = era.clone()
        new_era.set_id(era.get_id())
        eras.append(new_era)
    return eras
