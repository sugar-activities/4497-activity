# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
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


import unittest

from mock import Mock

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.objects import Category
from timelinelib.wxgui.components.cattree import CategoriesTree
from timelinelib.wxgui.components.cattree import CategoriesTreeController
from timelinelib.wxgui.components.timelineview import DrawingAreaPanel


class describe_categories_tree_control(unittest.TestCase):

    def test_categories_are_populated_from_db_when_initializing_from_db(self):
        self.controller.initialize_from_db(self.db)
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [
                (self.foofoo, []),
            ])
        ], None)

    def test_categories_are_populated_from_db_when_initializing_from_timeline_view(self):
        self.controller.initialize_from_timeline_view(self.timeline_view)
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [
                (self.foofoo, []),
            ])
        ], self.timeline_view.get_view_properties())

    def test_initializing_from_none_timeline_view_should_not_raise_exception(self):
        self.controller.initialize_from_timeline_view(None)

    def setUp(self):
        self.db = Mock(MemoryDB)
        self.foo = Category("foo", (255, 0, 0), None, True, parent=None)
        self.foofoo = Category("foofoo", (255, 0, 0), None, True, parent=self.foo)
        self.bar = Category("bar", (255, 0, 0), None, True, parent=None)
        self.db.get_categories.return_value = [self.foo, self.foofoo, self.bar]
        self.view = Mock(CategoriesTree)
        self.timeline_view = Mock(DrawingAreaPanel)
        self.timeline_view.get_timeline.return_value = self.db
        self.timeline_view.get_view_properties.return_value = Mock()
        self.controller = CategoriesTreeController(self.view, None)
