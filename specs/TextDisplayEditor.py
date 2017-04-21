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

from timelinelib.wxgui.dialogs.textdisplay import TextDisplayDialog
from timelinelib.editors.textdisplay import TextDisplayEditor

class TextDisplayEditorSpec(unittest.TestCase):

    def test_set_text_sets_dialog_text(self):
        text = "aha"
        self.editor.set_text(text)
        self.view.set_text.assert_called_with(text)

    def test_initialization_sets_dialog_text(self):
        self.editor.initialize()
        self.view.set_text.assert_called_with(self.text)

    def test_get_text_returns_dialog_text(self):
        self.assertTrue(WhenDialogTextIs("foo2", self.view, self.editor).controller_returns("foo2"))
        self.assertTrue(WhenDialogTextIs("foo3", self.view, self.editor).controller_returns("foo3"))

    def setUp(self):
        self.text = "buu"
        self.view = Mock(TextDisplayDialog)
        self.editor = TextDisplayEditor(self.view, self.text)


class WhenDialogTextIs(object):

    def __init__(self, text, view, editor):
        self.text = text
        view.get_text.return_value = text
        self.editor = editor
        self.editor.initialize()

    def controller_returns(self, text):
        text = self.editor.get_text()
        return self.text == text

