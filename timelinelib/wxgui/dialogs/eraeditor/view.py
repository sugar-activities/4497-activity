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


import wx

from timelinelib.wxgui.dialogs.eraeditor.controller import EraEditorDialogController
from timelinelib.wxgui.framework import Dialog
import timelinelib.wxgui.utils as guiutils


class EraEditorDialog(Dialog):

    """
    <BoxSizerVertical>

        <StaticBoxSizerVertical label="$(groupbox_text)" border="ALL" >

            <FlexGridSizer rows="0" columns="2" border="ALL">

                <StaticText label="$(when_text)" align="ALIGN_CENTER" />
                <BoxSizerHorizontal >
                    <TimePicker time_type="$(time_type)" config="$(config)" name="dtp_start" />
                    <StaticText label="$(to_text)" align="ALIGN_CENTER_VERTICAL" border="LEFT|RIGHT"/>
                    <TimePicker time_type="$(time_type)" config="$(config)" name="dtp_end"  />
                </BoxSizerHorizontal>

                <Spacer />
                <CheckBox align="ALIGN_CENTER_VERTICAL" label="$(show_time_text)" name="cbx_show_time"
                     event_EVT_CHECKBOX="show_time_checkbox_on_checked" />

                <StaticText label="$(name_text)" align="ALIGN_CENTER_VERTICAL" />
                <TextCtrl name="txt_name" />

                <StaticText label="$(colour_text)" align="ALIGN_CENTER_VERTICAL" />
                <ColourSelect name="colorpicker" align="ALIGN_CENTER_VERTICAL" width="60" height="30" />

            </FlexGridSizer>

        </StaticBoxSizerVertical>

        <DialogButtonsOkCancelSizer
            border="LEFT|RIGHT|BOTTOM"
            event_EVT_BUTTON__ID_OK="on_ok"
        />

    </BoxSizerVertical>
    """

    def __init__(self, parent, title, time_type, config, era):
        Dialog.__init__(self, EraEditorDialogController, parent, {
            "groupbox_text": _("Era Properties"),
            "show_time_text": _("Show time"),
            "name_text": _("Name:"),
            "colour_text": _("Colour:"),
            "when_text": _("When:"),
            "to_text": _("to"),
            "time_type": time_type,
            "config": config,
        }, title=title)
        self.controller.on_init(era, time_type)
        self.dtp_start.SetFocus()

    def SetShowTime(self, value):
        try:
            self.cbx_show_time.SetValue(value)
            self.dtp_start.show_time(value)
            self.dtp_end.show_time(value)
        except:
            # Not all TimePicker objects has a 'show_time' attribute
            pass

    def GetStart(self):
        return self.dtp_start.get_value()

    def SetStart(self, start):
        self.dtp_start.set_value(start)

    def GetEnd(self):
        return self.dtp_end.get_value()

    def SetEnd(self, end):
        self.dtp_end.set_value(end)

    def GetName(self):
        return self.txt_name.GetValue()

    def SetName(self, name):
        self.txt_name.SetValue(name)

    def GetColor(self):
        return self.colorpicker.GetValue()

    def SetColor(self, new_color):
        self.colorpicker.SetValue(new_color)

    def Close(self):
        self.EndModal(wx.ID_OK)

    def DisplayInvalidStart(self, message):
        self._DisplayInvalidInput(message, self.dtp_start)

    def DisplayInvalidEnd(self, message):
        self._DisplayInvalidInput(message, self.dtp_end)

    def DisplayInvalidName(self, message):
        self._DisplayInvalidInput(message, self.txt_name)

    def DisplayInvalidColor(self, message):
        self._DisplayInvalidInput(message, self.colorpicker)

    def DisplayInvalidPeriod(self, message):
        guiutils.display_error_message(message, self)

    def _DisplayInvalidInput(self, message, control):
        guiutils.display_error_message(message, self)
        guiutils._set_focus_and_select(control)
