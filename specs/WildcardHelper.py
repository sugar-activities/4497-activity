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
import wx

from timelinelib.wxgui.utils import WildcardHelper


class TestWildcardHelper(unittest.TestCase):

    def testGeneratesWildcardStringForUseInFileDialog(self):
        helper = WildcardHelper("Source code files", ["cpp", "py"])
        self.assertEquals(
            helper.wildcard_string(),
            "Source code files (*.cpp, *.py)|*.cpp;*.py")

    def testReturnsExtensionDataIfExtensionDataGivenAndPathMatch(self):
        helper = WildcardHelper("Image files", [("png", 1), ("bmp", 2)])
        self.assertEquals(
            helper.get_extension_data("bar.png"),
            1)

    def testReturnsNoExtensionDataIfPathDoesNotPathExtension(self):
        helper = WildcardHelper("Text files", [("txt", 4)])
        self.assertEquals(
            helper.get_extension_data("bar"),
            None)

    def testReturnsNoExtensionDataIfNoExtensionDataGiven(self):
        helper = WildcardHelper("Text files", ["txt"])
        self.assertEquals(
            helper.get_extension_data("foo.txt"),
            None)

    def testDoesNotAddExtensionIfExtensionAlreadyInPathFromDialog(self):
        helper = WildcardHelper("Image files", ["png", "bmp"])
        self.assertEquals(
            helper.get_path(self.aFileDialogReturningPath("bar.bmp")),
            "bar.bmp")

    def testAddsFirstExtensionIfNoExtensionInPathFromDialog(self):
        helper = WildcardHelper("Image files", ["png", "bmp"])
        self.assertEquals(
            helper.get_path(self.aFileDialogReturningPath("bar")),
            "bar.png")

    def aFileDialogReturningPath(self, path):
        file_dialog = Mock(wx.FileDialog)
        file_dialog.GetPath.return_value = path
        return file_dialog
