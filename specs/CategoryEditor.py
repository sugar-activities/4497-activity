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

from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.editors.category import CategoryEditor
from timelinelib.repositories.interface import CategoryRepository
from timelinelib.wxgui.dialogs.categoryeditor import WxCategoryEdtiorDialog


class CategoryEditorBaseFixture(unittest.TestCase):

    def setUp(self):
        # Category configuration:
        # foo
        #   foofoo
        # bar
        self.category_repository = Mock(CategoryRepository)
        self.foo = Category("foo", (255, 0, 0), None, True, parent=None)
        self.foofoo = Category("foofoo", (255, 0, 0), (0, 255, 0), True, parent=self.foo)
        self.bar = Category("bar", (255, 0, 0), None, True, parent=None)
        self.category_repository.get_all.return_value = [self.foo, self.foofoo, self.bar]
        def get_tree_mock(remove):
            if remove is None:
                return [
                    (self.bar, []),
                    (self.foo, [
                        (self.foofoo,
                            [])
                    ])
                ]
            elif remove is self.foofoo:
                return [
                    (self.bar, []),
                    (self.foo, [])
                ]
            else:
                return []
        self.category_repository.get_tree.side_effect = get_tree_mock
        self.view = Mock(WxCategoryEdtiorDialog)

    def _initializeControllerWith(self, category):
        self.controller = CategoryEditor(self.view)
        self.controller.edit(category, self.category_repository)


class WhenEditingANewCategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)

    def test_all_categories_in_db_are_listed_as_possible_parents(self):
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [
                (self.foofoo, [])
            ])
        ])

    def test_name_is_initialized_to_empty_string(self):
        self.view.set_name.assert_called_with("")

    def test_color_is_initialized_to_red(self):
        self.view.set_color.assert_called_with((255, 0, 0))

    def test_font_color_is_initialized_to_black(self):
        self.view.set_font_color.assert_called_with((0, 0, 0))

    def test_parent_is_initialized_to_none(self):
        self.view.set_parent.assert_called_with(None)


class WhenEditingAnExistingCategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(self.foofoo)

    def test_all_categories_in_db_except_the_one_being_edited_are_possible_parents(self):
        self.view.set_category_tree.assert_called_with([
            (self.bar, []),
            (self.foo, [])
        ])

    def test_name_is_initialized_from_edited_category(self):
        self.view.set_name.assert_called_with("foofoo")

    def test_color_is_initialixed_from_edited_category(self):
        self.view.set_color.assert_called_with((255, 0, 0))

    def test_font_color_is_initialixed_from_edited_category(self):
        self.view.set_font_color.assert_called_with((0, 255, 0))

    def test_parent_is_initialized_from_edited_category(self):
        self.view.set_parent.assert_called_with(self.foo)


class WhenTryingToEditACategoryButDbRaisesException(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self.category_repository.get_tree.side_effect = TimelineIOError
        self._initializeControllerWith(None)

    def test_error_is_handled_by_view(self):
        self.assertTrue(self.view.handle_db_error.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategory(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "new_cat"
        self.view.get_color.return_value = (255, 44, 0)
        self.view.get_font_color.return_value = (0, 44, 255)
        self.view.get_parent.return_value = self.foo
        self.controller.save()

    def _getSavedCategory(self):
        if not self.category_repository.save.called:
            self.fail("No category was saved.")
        return self.category_repository.save.call_args_list[0][0][0]

    def test_saved_category_has_name_from_view(self):
        self.assertEquals("new_cat", self._getSavedCategory().name)

    def test_saved_category_has_color_from_view(self):
        self.assertEquals((255, 44, 0), self._getSavedCategory().color)

    def test_saved_category_has_font_color_from_view(self):
        self.assertEquals((0, 44, 255), self._getSavedCategory().font_color)

    def test_saved_category_has_parent_from_view(self):
        self.assertEquals(self.foo, self._getSavedCategory().parent)

    def test_the_dialog_is_closed(self):
        self.assertTrue(self.view.close.called)


class WhenTryingToSaveACategoryButDbRaisesException(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "foobar"
        self.category_repository.save.side_effect = TimelineIOError
        self.controller.save()

    def test_error_is_handled_by_view(self):
        self.assertTrue(self.view.handle_db_error.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategoryWithAnInvalidName(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = ""
        self.controller.save()

    def test_the_category_is_not_saved_to_db(self):
        self.assertFalse(self.category_repository.save.called)

    def test_the_view_shows_an_error_message(self):
        self.assertTrue(self.view.handle_invalid_name.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)


class WhenSavingACategoryWithAUsedName(CategoryEditorBaseFixture):

    def setUp(self):
        CategoryEditorBaseFixture.setUp(self)
        self._initializeControllerWith(None)
        self.view.get_name.return_value = "foo"
        self.controller.save()

    def test_the_category_is_not_saved_to_db(self):
        self.assertFalse(self.category_repository.save.called)

    def test_the_view_shows_an_error_message(self):
        self.assertTrue(self.view.handle_used_name.called)

    def test_the_dialog_is_not_closed(self):
        self.assertFalse(self.view.close.called)
