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


from timelinelib.wxgui.components.categorychoice import CategoryChoice
from timelinelib.wxgui.components.colourselect import ColourSelect
from timelinelib.wxgui.components.containerchoice import ContainerChoice
from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonsapplyclosesizer import DialogButtonsApplyCloseSizer
from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonsclosesizer import DialogButtonsCloseSizer
from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonseditaddremoveclosesizer import DialogButtonsEditAddRemoveCloseSizer
from timelinelib.wxgui.components.dialogbuttonssizers.dialogbuttonsokcancelsizer import DialogButtonsOkCancelSizer
from timelinelib.wxgui.components.feedbacktext import FeedbackText
from timelinelib.wxgui.components.filechooser import FileChooser
from timelinelib.wxgui.components.header import Header
from timelinelib.wxgui.components.propertyeditors.alerteditor import AlertEditor
from timelinelib.wxgui.components.propertyeditors.descriptioneditor import DescriptionEditor
from timelinelib.wxgui.components.propertyeditors.hyperlinkeditor import HyperlinkEditor
from timelinelib.wxgui.components.propertyeditors.iconeditor import IconEditor
from timelinelib.wxgui.components.propertyeditors.progresseditor import ProgressEditor
from timelinelib.wxgui.components.textctrlselect import TextCtrlSelect
from timelinelib.wxgui.components.twostatebutton import TwoStateButton


def TimePicker(parent, time_type, name="", *args, **kwargs):
    from timelinelib.wxgui.utils import time_picker_for
    return time_picker_for(time_type)(parent, *args, **kwargs)
