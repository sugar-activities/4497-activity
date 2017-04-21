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


MAX_BUFFER_SIZE = 10


class UndoHandler(object):
    """
    The changes made to a timeline are stored in a list (self._undo_buffer).
    This list has a maximum size (MAX_BUFFER_SIZE) for the purpose of restricting
    memory consumption. When a timeline is opened, the original timeline data is
    stored in the first element of the list. If more changes are made than can be
    stored in the list, the first element in the list is discarded. The list has a
    'current position' (self._pos) that keeps track of which data to use after an
    undo/redo action. When 'current position' is at the beginning of the list, no
    more Undo's can be performed and when 'current position' is at the end of the
    list no more Redo's can be performed.
        """

    def __init__(self, db):
        self._db = db
        self._undo_buffer = []
        self._enabled = False
        self._pos = -1
        self._max_buffer_size = MAX_BUFFER_SIZE

    def enable(self, value):
        self._enabled = value

    def undo(self):
        if self._changes_to_undo():
            self._pos -= 1
            self.enable(False)
            self._notify_undo_redo_states()
            return True
        else:
            return False

    def redo(self):
        if self._changes_to_redo():
            self._pos += 1
            self.enable(False)
            self._notify_undo_redo_states()
            return True
        else:
            return False

    def get_data(self):
        return self._undo_buffer[self._pos].clone()

    def save(self):
        if self._enabled:
            del (self._undo_buffer[self._pos + 1:])
            if self._max_buffer_size == len(self._undo_buffer):
                del(self._undo_buffer[0])
                self._pos -= 1
            self._undo_buffer.append(self._db._events.clone())
            self._pos += 1
            self._notify_undo_redo_states()

    def _notify_undo_redo_states(self):
        self._db.notify_undo_redo_states(self._changes_to_undo(), self._changes_to_redo())

    def _changes_to_undo(self):
        return self._pos > 0

    def _changes_to_redo(self):
        return self._pos < len(self._undo_buffer) - 1
