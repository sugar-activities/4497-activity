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


from autopilotlib.app.logger import Logger


class MenuBarDescriber():
    
    @classmethod
    def describe(self,frame):
        try:
            menu_bar = frame.GetMenuBar()
            if menu_bar is not None:
                self.describe_menu_bar(menu_bar)
                Logger.add(" ")
        except AttributeError:
            pass
        
    @classmethod
    def describe_menu_bar(self, menu_bar):
        Logger.newline()
        Logger.header2("Menu Bar:  count = %d" % menu_bar.MenuCount)
        for menu, name in menu_bar.Menus:
            self.describe_menu(menu, name)

    @classmethod
    def describe_menu(self, menu, name):
        Logger.add(" ")
        Logger.add("   Menu: '%s'    Item count: %d" % (name, menu.MenuItemCount))
        Logger.add("        Id   Label                      Text")
        Logger.add("      ----   ------------------------   ---------------------")
        for item in menu.MenuItems:
            self.describe_menu_item(item)
            if item.SubMenu is not None and item.SubMenu.MenuItemCount > 0:
                self.describe_submenu(item.SubMenu)
        
    @classmethod
    def describe_menu_item(self, item):
        Logger.add("      %4d   %-24.24s  '%s' " % (item.Id, item.Label, item.Text) )
        
    @classmethod
    def describe_submenu(self, submenu):
        Logger.add(" ")
        Logger.add("        Submenu Item count: %d" % (submenu.MenuItemCount))
        Logger.add("             Id   Label                      Text")
        Logger.add("           ----   ------------------------   ---------------------")
        for item in submenu.MenuItems:
            Logger.add("           %4d   %-24.24s  '%s' " % (item.Id, item.Label, item.Text) )
        Logger.add(" ")
