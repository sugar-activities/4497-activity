#!/usr/bin/env python
#
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


import datetime
import os.path
import sys
import traceback

# Make sure that we can import mechanize
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "libs", "dev", "mechanize-0.2.5"))
import mechanize
import wx


def start_release_announcer_gui():
    app = wx.PySimpleApp()
    MainFrame().Show()
    app.MainLoop()


class MainFrame(wx.Frame):

    BORDER = 5
    SMALL_WIDTH = 150
    LARGE_WIDTH = 300

    def __init__(self):
        wx.Frame.__init__(self, parent=None)
        self._create_gui()
        self.controller = MainFrameController(self)
        self.controller.on_started()

    def _create_gui(self):
        self._create_main_panel()

    def _create_main_panel(self):
        self.main_panel = wx.Panel(self)
        self._create_grid()
        self._create_buttons()
        self._create_log()
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.grid, flag=wx.ALL|wx.EXPAND, proportion=0, border=self.BORDER)
        vbox.Add(self.button_box, flag=wx.ALL|wx.EXPAND, proportion=0, border=self.BORDER)
        vbox.Add(self.log_text, flag=wx.ALL|wx.EXPAND, proportion=1, border=self.BORDER)
        self.main_panel.SetSizer(vbox)

    def _create_grid(self):
        self.grid = wx.FlexGridSizer(10, 2, self.BORDER, self.BORDER)
        self.grid.SetFlexibleDirection(wx.VERTICAL)
        self.grid.AddGrowableCol(1)
        self._create_sf_username_controls()
        self._create_sf_password_controls()
        self._create_freecode_username_controls()
        self._create_freecode_password_controls()
        self._create_version_to_release_controls()
        self._create_next_version_controls()
        self._create_next_version_release_date_controls()
        self._create_sf_news_header_controls()
        self._create_release_message_controls()
        self._create_tags_controls()

    def _create_sf_username_controls(self):
        self._add_label_to_grid("SourceForge username:")
        self.sf_username_text = wx.TextCtrl(
            self.main_panel)
        self.grid.Add(self.sf_username_text, flag=wx.EXPAND)

    def get_sf_username(self):
        return self.sf_username_text.GetValue()

    def _create_sf_password_controls(self):
        self._add_label_to_grid("SourceForge password:")
        self.sf_password_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1), style=wx.TE_PASSWORD)
        self.grid.Add(self.sf_password_text, flag=wx.EXPAND)

    def get_sf_password(self):
        return self.sf_password_text.GetValue()

    def _create_freecode_username_controls(self):
        self._add_label_to_grid("Freecode username:")
        self.freecode_username_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1))
        self.grid.Add(self.freecode_username_text, flag=wx.EXPAND)

    def get_freecode_username(self):
        return self.freecode_username_text.GetValue()

    def _create_freecode_password_controls(self):
        self._add_label_to_grid("Freecode password:")
        self.freecode_password_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1), style=wx.TE_PASSWORD)
        self.grid.Add(self.freecode_password_text, flag=wx.EXPAND)

    def get_freecode_password(self):
        return self.freecode_password_text.GetValue()

    def _create_version_to_release_controls(self):
        self._add_label_to_grid("Version to release:")
        self.version_to_release_text = wx.TextCtrl(
            self.main_panel, size=(self.SMALL_WIDTH, -1))
        self.grid.Add(self.version_to_release_text)
        self.Bind(wx.EVT_TEXT, self._on_version_to_release_edited, self.version_to_release_text)

    def _on_version_to_release_edited(self, event):
        self.controller.on_version_to_release_edited()

    def get_version_to_release(self):
        return self.version_to_release_text.GetValue()

    def _create_next_version_controls(self):
        self._add_label_to_grid("Next version:")
        self.next_version_text = wx.TextCtrl(
            self.main_panel, size=(self.SMALL_WIDTH, -1))
        self.grid.Add(self.next_version_text)

    def get_next_version(self):
        return self.next_version_text.GetValue()

    def set_next_version(self, text):
        self.next_version_text.SetValue(text)

    def enable_input_of_next_version(self):
        self.next_version_text.Enable()

    def disable_input_of_next_version(self):
        self.next_version_text.Disable()

    def _create_next_version_release_date_controls(self):
        self._add_label_to_grid("Next version release date (MM/DD/YY):")
        self.next_version_release_date_text = wx.TextCtrl(
            self.main_panel, size=(self.SMALL_WIDTH, -1))
        self.grid.Add(self.next_version_release_date_text)

    def enable_input_of_next_version_release_date(self):
        self.next_version_release_date_text.Enable()

    def disable_input_of_next_version_release_date(self):
        self.next_version_release_date_text.Disable()

    def get_next_version_release_date(self):
        return self.next_version_release_date_text.GetValue()

    def set_next_version_release_date(self, text):
        self.next_version_release_date_text.SetValue(text)

    def _create_sf_news_header_controls(self):
        self._add_label_to_grid("SourceForge news header:")
        self.sf_news_header_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1))
        self.grid.Add(self.sf_news_header_text, flag=wx.EXPAND)

    def get_sf_news_header(self):
        return self.sf_news_header_text.GetValue()

    def set_sf_news_header(self, text):
        self.sf_news_header_text.SetValue(text)

    def _create_release_message_controls(self):
        self._add_label_to_grid("Release message:")
        self.release_message_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1), style=wx.TE_MULTILINE)
        self.grid.Add(self.release_message_text, flag=wx.EXPAND)

    def get_release_message(self):
        return self.release_message_text.GetValue()

    def _create_tags_controls(self):
        self._add_label_to_grid("Tags:")
        self.tags_text = wx.TextCtrl(
            self.main_panel, size=(self.LARGE_WIDTH, -1))
        self.grid.Add(self.tags_text, flag=wx.EXPAND)

    def get_tags(self):
        return self.tags_text.GetValue()

    def set_tags(self, text):
        self.tags_text.SetValue(text)

    def _create_buttons(self):
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)
        self._create_announce_button()
        self._create_exit_button()

    def _create_announce_button(self):
        self.announce_button = wx.Button(self.main_panel, label="Announce")
        self.Bind(wx.EVT_BUTTON, self._announce_button_clicked, self.announce_button)
        self.button_box.Add(self.announce_button, flag=wx.RIGHT, border=self.BORDER)

    def _announce_button_clicked(self, event):
        self.controller.on_announce_button_clicked()

    def disable_announce_button(self):
        self.announce_button.Disable()

    def _create_exit_button(self):
        exit_button = wx.Button(self.main_panel, id=wx.ID_EXIT)
        self.Bind(wx.EVT_BUTTON, self._exit_button_clicked, exit_button)
        self.button_box.Add(exit_button, flag=wx.RIGHT, border=self.BORDER)

    def _exit_button_clicked(self, event):
        self.Close()

    def _create_log(self):
        self.log_text = wx.TextCtrl(self.main_panel, style=wx.TE_MULTILINE)

    def _add_label_to_grid(self, text):
        self.grid.Add(
            wx.StaticText(self.main_panel, label=text),
            flag=wx.ALIGN_CENTER_VERTICAL)

    def show_error_message(self, error):
        dialog = wx.MessageDialog(self, error, "Error", wx.OK|wx.ICON_ERROR)
        dialog.ShowModal()
        dialog.Destroy()

    def clear_log(self):
        self.log_text.SetValue("")

    def log_information(self, message):
        self.log_text.AppendText(message)

    def log_error(self, message):
        message = "\n".join(["    %s" % line for line in message.split("\n")])
        self.log_text.AppendText(" FAILED\n%s\n" % message)


class MainFrameController(object):

    def __init__(self, main_frame):
        self.view = main_frame

    def on_started(self):
        self.view.SetTitle("Release Announcer")

    def on_version_to_release_edited(self):
        self.view.set_sf_news_header(
            "Version %s released" % self.view.get_version_to_release())
        if self._release_is_major_version():
            self.view.enable_input_of_next_version()
            self.view.enable_input_of_next_version_release_date()
            self.view.set_next_version(self._calculate_next_version())
            self.view.set_next_version_release_date(self._calculate_next_release_date())
            self.view.set_tags("Feature Enhancements")
        else:
            self.view.disable_input_of_next_version()
            self.view.disable_input_of_next_version_release_date()
            self.view.set_tags("Bugfixes")

    def _calculate_next_version(self):
        try:
            (x, y, z) = self.view.get_version_to_release().split(".")
            return ".".join([x, str(int(y)+1), z])
        except Exception, e:
            return ""

    def _calculate_next_release_date(self):
        today = datetime.datetime.today()
        three_months_from_now = today + datetime.timedelta(days=30*3)
        return three_months_from_now.strftime("%m/%d/%y")

    def _release_is_major_version(self):
        return self.view.get_version_to_release().endswith("0")

    def on_announce_button_clicked(self):
        self._setup_browser()
        self.view.clear_log()
        if not self._login_to_sf() or not self._login_to_freecode():
            self.view.show_error_message("Check login fields and try again.")
            return
        self._submit_news_on_sf()
        self._submit_news_on_freecode()
        self.view.disable_announce_button()

    def _setup_browser(self):
        browser = mechanize.Browser()
        self.sf_site = SF(browser)
        self.freecoce_site = Freecode(browser)

    def _login_to_sf(self):
        self.view.log_information("\nLogging in to SourceForge...")
        try:
            self.sf_site.login(
                self.view.get_sf_username(),
                self.view.get_sf_password())
            self.view.log_information(" OK")
            return True
        except Exception, e:
            self.view.log_error(traceback.format_exc())
            return False

    def _login_to_freecode(self):
        self.view.log_information("\nLogging in to Freecode...")
        try:
            self.freecoce_site.login(
                self.view.get_freecode_username(),
                self.view.get_freecode_password())
            self.view.log_information(" OK")
            return True
        except Exception, e:
            self.view.log_error(traceback.format_exc())
            return False

    def _submit_news_on_sf(self):
        self.view.log_information("\nSubmitting news on SourceForge...")
        try:
            self.sf_site.submitt_news(
                self.view.get_sf_news_header(),
                self.view.get_release_message())
            self.view.log_information(" OK")
        except Exception, e:
            self.view.log_error(traceback.format_exc())

    def _submit_news_on_freecode(self):
        self.view.log_information("\nSubmitting news on Freecode...")
        try:
            self.freecoce_site.add_release(
                self.view.get_version_to_release(),
                self.view.get_release_message(),
                self.view.get_tags())
            self.view.log_information(" OK")
        except Exception, e:
            self.view.log_error(traceback.format_exc())


class Site(object):

    def _select_form_with_controls(self, control_names):
        self.browser.select_form(predicate=self._has_controls_predicate(control_names))

    def _has_controls_predicate(self, control_names):
        def predicate(form):
            try:
                for name in control_names:
                    form.find_control(name=name)
            except mechanize.ControlNotFoundError:
                return False
            return True
        return predicate


class SF(Site):

    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        self.browser.open("https://sourceforge.net/account/login.php")
        self.browser.select_form(name="login_userpw")
        self.browser["form_loginname"] = username
        self.browser["form_pw"] = password
        self.browser.submit()
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        self.browser.find_link(text="Log Out")

    def submitt_news(self, subject, details):
        self.browser.open("https://sourceforge.net/news/submit.php?group_id=241839")
        self.browser.select_form(name="postNews")
        self.browser["summary"] = subject
        self.browser["details"] = details
        self.browser.submit("submitb")
        assert "News Added." in self.browser.response().read()


class Freecode(Site):

    def __init__(self, browser):
        self.browser = browser

    def login(self, username, password):
        self.browser.open("http://freecode.com/session/new?return_to=%2F")
        self._select_form_with_controls(["user_session[login]"])
        self.browser["user_session[login]"] = username
        self.browser["user_session[password]"] = password
        self.browser.submit("commit")
        self._ensure_logged_in()

    def _ensure_logged_in(self):
        self.browser.find_link(text="Logout")
        assert "Logged in successfully." in self.browser.response().read()

    def add_release(self, version, summary, tags):
        self.browser.open("http://freecode.com/projects/timeline-2/releases/new")
        self._select_form_with_controls(["release[version]"])
        self.browser["release[version]"] = version
        self.browser["release[changelog]"] = summary
        self.browser["release[tag_list]"] = tags
        self.browser.submit("commit")


if __name__ == '__main__':
    start_release_announcer_gui()
