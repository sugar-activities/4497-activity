# -*- coding: utf-8 -*-
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


from datetime import datetime
import codecs

import wx

from specs.utils import TmpDirTestCase
from timelinelib.db.backends.xmlfile import XmlTimeline
from timelinelib.db import db_open
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.meta.version import get_version
from timelinelib.time import WxTimeType


class XmlTimelineSpec(TmpDirTestCase):

    IO = True

    def testUseWxTimeTypeWhenUseWideDateRangeIsTrue(self):
        timeline = XmlTimeline(None, load=False, use_wide_date_range=True)
        self.assertTrue(isinstance(timeline.get_time_type(), WxTimeType))

    def testAlertStringParsingGivesAlertData(self):
        timeline = XmlTimeline(None, load=False, use_wide_date_range=True)
        time, text = timeline._parse_alert_string("2012-11-11 00:00:00;Now is the time")
        self.assertEqual("Now is the time", text)
        self.assertEqual("2012-11-11 00:00:00", "%s" % timeline.get_time_type().time_string(time))

    def testAlertDataConversionGivesAlertString(self):
        timeline = XmlTimeline(None, load=False, use_wide_date_range=False)
        alert = (datetime(2010, 8, 31, 0, 0, 0), "Hoho")
        alert_text = timeline.alert_string(alert)
        self.assertEqual("2010-8-31 0:0:0;Hoho", alert_text)

    def testWxTimeAlertDataConversionGivesAlertString(self):
        timeline = XmlTimeline(None, load=False, use_wide_date_range=True)
        alert = (wx.DateTimeFromDMY(30, 8, 2010, 0, 0, 0), "Hoho")
        alert_text = timeline.alert_string(alert)
        self.assertEqual("2010-09-30 00:00:00;Hoho", alert_text)

    def testDisplayedPeriodTagNotWrittenIfNotSet(self):
        # Create a new db and add one event
        db = db_open(self.tmp_path)
        db.save_event(Event(db.get_time_type(), datetime(2010, 8, 31, 0, 0, 0),
                            datetime(2010, 8, 31, 0, 0, 0),
                            "test"))
        # Read the file content from disk
        f = codecs.open(self.tmp_path, "r", "utf-8")
        content = f.read()
        f.close()
        # Assert that displayed_period tag is not written
        self.assertEquals(content, """<?xml version="1.0" encoding="utf-8"?>
<timeline>
  <version>%s</version>
  <categories>
  </categories>
  <events>
    <event>
      <start>2010-8-31 0:0:0</start>
      <end>2010-8-31 0:0:0</end>
      <text>test</text>
      <fuzzy>False</fuzzy>
      <locked>False</locked>
      <ends_today>False</ends_today>
    </event>
  </events>
  <view>
    <hidden_categories>
    </hidden_categories>
  </view>
</timeline>
""" % get_version())

    def testWriteReadCycle(self):
        self._create_db()
        db_re_read = XmlTimeline(self.tmp_path)
        self._assert_re_read_db_same(db_re_read)

    def _create_db(self):
        db = XmlTimeline(self.tmp_path)
        # Create categories
        cat1 = Category("Category 1", (255, 0, 0), (0, 0, 255), True)
        db.save_category(cat1)
        cat2 = Category("Category 2", (0, 255, 0), None, True, parent=cat1)
        db.save_category(cat2)
        cat3 = Category("Category 3", (0, 0, 255), None, True, parent=cat2)
        db.save_category(cat3)
        # Create events
        ev1 = Event(db.get_time_type(), datetime(2010, 3, 3), datetime(2010, 3, 6),
                    "Event 1", cat1)
        ev1.set_data("description", u"The <b>first</b> event åäö.")
        ev1.set_data("alert", (datetime(2012, 12, 31), "Time to go"))
        db.save_event(ev1)
        # Create view properties
        vp = ViewProperties()
        start = datetime(2010, 3, 1)
        end = datetime(2010, 4, 1)
        vp.displayed_period = TimePeriod(db.get_time_type(), start, end)
        vp.set_category_visible(cat3, False)
        db.save_view_properties(vp)

    def _assert_re_read_db_same(self, db):
        # Assert event correctly loaded
        events = db.get_all_events()
        self.assertEquals(len(events), 1)
        event = events[0]
        self.assertEquals(event.text, "Event 1")
        self.assertEquals(event.time_period.start_time, datetime(2010, 3, 3))
        self.assertEquals(event.time_period.end_time, datetime(2010, 3, 6))
        self.assertEquals(event.category.name, "Category 1")
        self.assertEquals(event.get_data("description"), u"The <b>first</b> event åäö.")
        self.assertEquals(event.get_data("alert"), (datetime(2012, 12, 31), "Time to go"))
        self.assertEquals(event.get_data("icon"), None)
        # Assert that correct view properties are loaded (category visibility
        # checked later)
        vp = ViewProperties()
        db.load_view_properties(vp)
        self.assertEquals(vp.displayed_period.start_time, datetime(2010, 3, 1))
        self.assertEquals(vp.displayed_period.end_time, datetime(2010, 4, 1))
        # Assert categories correctly loaded
        categories = db.get_categories()
        self.assertEquals(len(categories), 3)
        for cat in categories:
            self.assertTrue(cat.has_id())
            if cat.name == "Category 1":
                self.assertEquals(cat.color, (255, 0, 0))
                self.assertEquals(cat.font_color, (0, 0, 255))
                self.assertTrue(vp.category_visible(cat))
                self.assertEquals(cat.parent, None)
            elif cat.name == "Category 2":
                self.assertEquals(cat.color, (0, 255, 0))
                self.assertTrue(vp.category_visible(cat))
                self.assertEquals(cat.parent.name, "Category 1")
            elif cat.name == "Category 3":
                self.assertEquals(cat.color, (0, 0, 255))
                self.assertFalse(vp.category_visible(cat))
                self.assertEquals(cat.parent.name, "Category 2")
            else:
                self.fail("Unknown category.")

    def setUp(self):
        TmpDirTestCase.setUp(self)
        self.tmp_path = self.get_tmp_path("test.timeline")
