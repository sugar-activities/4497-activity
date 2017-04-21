#!/usr/bin/env python


# Make sure timelinelib can be imported
import os.path
import sys
root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(root_dir, ".."))


import wx

from timelinelib.wxgui.component import TimelineComponent


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
        timeline_component = TimelineComponent(self)
        timeline_component.open_timeline(
            os.path.join(root_dir, "example.timeline"))


def install_gettext_in_builtin_namespace():
    def _(message):
        return message
    import __builtin__
    if not "_" in __builtin__.__dict__:
        __builtin__.__dict__["_"] = _


if __name__ == "__main__":
    install_gettext_in_builtin_namespace()
    app = wx.PySimpleApp()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()
