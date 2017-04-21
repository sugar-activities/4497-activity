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


from timelinelib.drawing.drawers import get_progress_color


EXPORTABLE_FIELDS = FIELDS = ("Name", "Color", "Progress Color", "Done Color", "Parent")


class Category(object):

    def __init__(self, name, color, font_color, parent=None):
        self.id = None
        self.name = name
        self.color = color
        self.progress_color = get_progress_color(color)
        self.done_color = get_progress_color(color)
        if font_color is None:
            self.font_color = (0, 0, 0)
        else:
            self.font_color = font_color
        self.parent = parent

    def get_id(self):
        return self.id

    def has_id(self):
        return self.id is not None

    def set_id(self, category_id):
        self.id = category_id
        return self

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        return self

    def get_color(self):
        return self.color

    def get_progress_color(self):
        return self.progress_color

    def get_done_color(self):
        return self.done_color

    def set_color(self, color):
        self.color = color
        return self

    def set_progress_color(self, color):
        self.progress_color = color
        return self

    def set_done_color(self, color):
        self.done_color = color
        return self

    def get_font_color(self):
        return self.font_color

    def set_font_color(self, font_color):
        self.font_color = font_color
        return self

    def _get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent
        return self

    def clone(self):
        clone = Category(self.get_name(), self.get_color(),
                         self.get_font_color(), self._get_parent())
        clone.set_progress_color(self.get_progress_color())
        clone.set_done_color(self.get_done_color())
        return clone

    def get_exportable_fields(self):
        return EXPORTABLE_FIELDS

    def __repr__(self):
        return "Category<id=%r, name=%r, color=%r, font_color=%r>" % (
            self.get_id(), self.get_name(), self.get_color(),
            self.get_font_color())

    def __eq__(self, other):
        if self is other:
            return True
        return (isinstance(other, Category) and
                self.get_id() == other.get_id() and
                self.get_name() == other.get_name() and
                self.get_color() == other.get_color() and
                self.get_progress_color() == other.get_progress_color() and
                self.get_done_color() == other.get_done_color() and
                self.get_font_color() == other.get_font_color() and
                self._get_parent() == other._get_parent())

    def __ne__(self, other):
        return not (self == other)


def sort_categories(categories):
    sorted_categories = list(categories)
    sorted_categories.sort(cmp, lambda category: category.get_name().lower())
    return sorted_categories


def clone_categories_list(categories):
    cloned_list = []
    clones = {}
    for category in categories:
        clone = category.clone()
        clone.set_id(category.get_id())
        cloned_list.append(clone)
        clones[category] = clone
    for category in cloned_list:
        if category._get_parent() is not None:
            category.set_parent(clones[category._get_parent()])
    return (cloned_list, clones)
