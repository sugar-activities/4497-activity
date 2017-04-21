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


from timelinelib.data.event import Event
from timelinelib.features.experimental.experimentalfeatures import EXTENDED_CONTAINER_STRATEGY


class Container(Event):

    def __init__(self, time_type, start_time, end_time, text, category=None,
                 cid=-1):
        Event.__init__(self, time_type, start_time, end_time, text, category,
                       False, False, False)
        self.container_id = cid
        self.events = []
        import timelinelib.db.strategies
        if EXTENDED_CONTAINER_STRATEGY.enabled():
            self.strategy = timelinelib.db.strategies.ExtendedContainerStrategy(self)
        else:
            self.strategy = timelinelib.db.strategies.DefaultContainerStrategy(self)

    def __eq__(self, other):
        return (isinstance(other, Container) and
                self.container_id == other.cid() and
                super(Container, self).__eq__(other))

    def is_container(self):
        return True

    def is_subevent(self):
        return False

    def cid(self):
        return self.container_id

    def set_cid(self, cid):
        self.container_id = cid
        return self

    def register_subevent(self, subevent):
        self.strategy.register_subevent(subevent)

    def unregister_subevent(self, subevent):
        self.strategy.unregister_subevent(subevent)

    def update_container(self, subevent):
        self.strategy.update(subevent)

    def update_properties(self, text, category=None):
        self.set_text(text)
        self.set_category(category)

    def clone(self):
        return Container(
            self.get_time_type(), self.get_time_period().start_time,
            self.get_time_period().end_time, self.get_text(),
            self.get_category(), self.container_id)

    def get_subevents(self):
        return self.events
