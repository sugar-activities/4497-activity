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


import os.path


from autopilotlib.app.pythonlauncher import run_python_file
from autopilotlib.app.logger import Logger
import autopilotlib.wrappers.aboutbox as aboutbox
import autopilotlib.wrappers.frame as frame
import autopilotlib.wrappers.dialog as dialog
import autopilotlib.wrappers.messagedialog as messagedialog
import autopilotlib.wrappers.messagebox as messagebox
import autopilotlib.wrappers.filedialog as filedialog
import autopilotlib.wrappers.pagesetup as pagesetup
import autopilotlib.wrappers.printer as printer
import autopilotlib.wrappers.printpreview as printpreview
import autopilotlib.wrappers.dirdialog as dirdialog
import autopilotlib.wrappers.colourdialog as colourdialog


manuscript = None


def run_manuscript(frame):
    """This method is called back from the first Frame object created.
    """
    manuscript.execute(frame)


def execute_frame_instructions(frame):
    """This method is called back from the first Frame object created.
    """
    if frame.Shown:
        manuscript.execute_frame_instructions(frame)

    
def wrap_wx_classes():
    """
    All wx-classes that we wan't to detect the construction of in the
    application under test, must be wrapped in a class of our own.
    """
    frame.Frame.wrap(manuscript.register_dialog)
    aboutbox.AboutBox.wrap(manuscript.register_dialog)
    colourdialog.ColourDialog.wrap(manuscript.register_dialog)
    dialog.Dialog.wrap(manuscript.register_dialog)
    dirdialog.DirDialog.wrap(manuscript.register_dialog)
    filedialog.FileDialog.wrap(manuscript.register_dialog)
    messagedialog.MessageDialog.wrap(manuscript.register_dialog)
    messagebox.wrap(manuscript.register_dialog)
    pagesetup.PageSetupDialog.wrap(manuscript.register_dialog)
    printer.Printer.wrap(manuscript.register_dialog)
    printer.Printer.wrap(manuscript.register_dialog)
    printpreview.PreviewFrame.wrap(manuscript.register_dialog)
    

# Must be included after run_manuscript but before run_python_file()-call
import autopilotlib.wrappers.frame


def start_app(mymanuscript, path):
    global manuscript
    manuscript = mymanuscript
    wrap_wx_classes()
    Logger.header("Starting application %s" % os.path.basename(path))
    run_python_file([path,])

