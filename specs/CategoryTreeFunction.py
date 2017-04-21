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

from timelinelib.db.objects import Category
from timelinelib.wxgui.utils import category_tree


class CategoryTreeFunctionSpec(unittest.TestCase):

    def testCreatesTreeOfCategories(self):
        tree = category_tree([self.c11, self.c1, self.c2])
        self.assertEquals(tree, [(self.c1, [(self.c11, [])]), (self.c2, [])])

    def testCreatesEmptyChildListForLeaves(self):
        tree = category_tree([self.c1, self.c2])
        self.assertEquals(tree, [(self.c1, []), (self.c2, [])])

    def testSortsCategories(self):
        tree = category_tree([self.c11, self.c2, self.c1])
        self.assertEquals(tree, [(self.c1, [(self.c11, [])]), (self.c2, [])])

    def setUp(self):
        self.c1 = Category("c1", (255, 0, 0), None, True, parent=None)
        self.c11 = Category("c11", (255, 0, 0), None, True, parent=self.c1)
        self.c2 = Category("c2", (255, 0, 0), None, True, parent=None)
