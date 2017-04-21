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


from timelinelib.features.experimental.experimentalfeature import ExperimentalFeature


DISPLAY_NAME = "Mark Event as Done"
DESCRIPTION = """
              Mark an Event as Done by setting progress=100%

              A menu item 'Mark as Done' appears in the context menu,
              displayed when you righ-click on one or more selected Events.
              """


class ExperimentalFeatureDone(ExperimentalFeature):

    def __init__(self):
        ExperimentalFeature.__init__(self, DISPLAY_NAME, DESCRIPTION)
