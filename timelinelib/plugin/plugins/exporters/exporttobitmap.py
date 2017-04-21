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


import os.path

import wx

from timelinelib.wxgui.utils import _ask_question
from timelinelib.wxgui.utils import WildcardHelper
from timelinelib.wxgui.utils import display_warning_message
from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.factory import EXPORTER


class BitmapExporter(PluginBase):

    def service(self):
        return EXPORTER

    def display_name(self):
        return _("Export Current view to Image...")

    def wxid(self):
        from timelinelib.wxgui.frames.mainframe.mainframe import ID_EXPORT
        return ID_EXPORT

    def run(self, main_frame):
        export_to_image(main_frame)


class MultiBitmapExporter(PluginBase):

    def service(self):
        return EXPORTER

    def display_name(self):
        return _("Export Whole Timeline to Images...")

    def wxid(self):
        from timelinelib.wxgui.frames.mainframe.mainframe import ID_EXPORT_ALL
        return ID_EXPORT_ALL

    def run(self, main_frame):
        export_to_images(main_frame)


def export_to_image(main_frame):
    path, image_type = get_image_path(main_frame)
    if path is not None and overwrite_existing_path(main_frame, path):
        bitmap = main_frame.main_panel.get_current_image()
        image = wx.ImageFromBitmap(bitmap)
        image.SaveFile(path, image_type)


def export_to_images(main_frame):
    path, image_type = get_image_path(main_frame)
    if path is not None:
        try:
            periods, current_period = main_frame.get_export_periods()
        except ValueError:
            msg = _("The first image contains a Julian day < 0\n\nNavigate to first event or\nUse the feature 'Accept negative Julian days'")
            display_warning_message(msg)
            return
        view_properties = main_frame.main_panel.timeline_panel.timeline_canvas.controller.view_properties
        view_properties.set_use_fixed_event_vertical_pos(True)
        path_without_extension, extension = path.rsplit(".", 1)
        view_properties.set_use_fixed_event_vertical_pos(True)
        view_properties.periods = periods
        count = 1
        for period in periods:
            path = "%s_%d.%s" % (path_without_extension, count, extension)
            if overwrite_existing_path(main_frame, path):
                main_frame.main_panel.timeline_panel.timeline_canvas.controller.view_properties.displayed_period = period
                main_frame.main_panel.redraw_timeline()
                bitmap = main_frame.main_panel.get_current_image()
                image = wx.ImageFromBitmap(bitmap)
                image.SaveFile(path, image_type)
            count += 1
        view_properties.set_use_fixed_event_vertical_pos(False)
        main_frame.main_panel.timeline_panel.timeline_canvas.controller.view_properties.displayed_period = current_period
        main_frame.main_panel.redraw_timeline()


def get_image_path(main_frame):
    image_type = None
    path = None
    file_info = _("Image files")
    file_types = [("png", wx.BITMAP_TYPE_PNG)]
    images_wildcard_helper = WildcardHelper(file_info, file_types)
    wildcard = images_wildcard_helper.wildcard_string()
    dialog = wx.FileDialog(main_frame, message=_("Export to Image"), wildcard=wildcard, style=wx.FD_SAVE)
    if dialog.ShowModal() == wx.ID_OK:
        path = images_wildcard_helper.get_path(dialog)
        image_type = images_wildcard_helper.get_extension_data(path)
    dialog.Destroy()
    return path, image_type


def overwrite_existing_path(main_frame, path):
    if os.path.exists(path):
        overwrite_question = _("File '%s' exists. Overwrite?") % path
        return _ask_question(overwrite_question, main_frame) == wx.YES
    return True
