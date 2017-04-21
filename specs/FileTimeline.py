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
import unittest

from specs.utils import TmpDirTestCase
from timelinelib.db.backends.file import dequote
from timelinelib.db.backends.file import FileTimeline
from timelinelib.db.backends.file import quote
from timelinelib.db.backends.file import split_on_semicolon
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import TimePeriod
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.time import PyTimeType


class FileTimelineSpec(TmpDirTestCase):

    IO = True

    def testCorruptData(self):
        """
        Scenario: You open a timeline that contains corrupt data.

        Expected result: You get an exception and you can not use the timeline.
        """
        self.assertRaises(TimelineIOError, FileTimeline, self.corrupt_file)

    def testMissingEOF(self):
        """
        Scenario: A timeline is opened that contains no corrupt data. However,
        no end of file marker is found.

        Expected result: The timeline should be treated as corrupt.
        """
        self.assertRaises(TimelineIOError, FileTimeline, self.missingeof_file)

    def testAddingEOF(self):
        """
        Scenario: You open an old timeline < 0.3.0 with a client >= 0.3.0.

        Expected result: The timeline does not contain the EOF marker but since
        it is an old file, no exception should be raised.
        """
        FileTimeline(self._021_file)

    def testInvalidTimePeriod(self):
        """
        Scenario: You open a timeline that has a PREFERRED-PERIOD of length 0.

        Expected result: Even if this is a valid value for a TimePeriod it
        should not be a valid PREFERRED-PERIOD. The length must be > 0. So we
        should get an error when trying to read this.
        """
        self.assertRaises(TimelineIOError, FileTimeline,
                          self.invalid_time_period_file)

    def testSettingInvalidPreferredPeriod(self):
        """
        Scenario: You try to assign a preferred period whose length is 0.

        Expected result: You should get an error.
        """
        timeline = FileTimeline(self.valid_file)
        now = datetime.datetime.now()
        zero_tp = TimePeriod(PyTimeType(), now, now)
        vp = ViewProperties()
        vp.displayed_period = zero_tp
        self.assertRaises(TimelineIOError, timeline.save_view_properties, vp)

    def setUp(self):
        TmpDirTestCase.setUp(self)
        # Create temporary dir and names
        self.corrupt_file = self.get_tmp_path("corrupt.timeline")
        self.missingeof_file = self.get_tmp_path("missingeof.timeline")
        self._021_file = self.get_tmp_path("021.timeline")
        self.invalid_time_period_file = self.get_tmp_path("invalid_time_period.timeline")
        self.valid_file = self.get_tmp_path("valid.timeline")
        # Write content to files
        HEADER_030 = "# Written by Timeline 0.3.0 on 2009-7-23 9:40:33"
        HEADER_030_DEV = "# Written by Timeline 0.3.0dev on 2009-7-23 9:40:33"
        HEADER_021 = "# Written by Timeline 0.2.1 on 2009-7-23 9:40:33"
        self.write_timeline(self.corrupt_file, ["corrupt data here"])
        self.write_timeline(self.missingeof_file, ["# valid data"])
        self.write_timeline(self._021_file, [HEADER_021])
        invalid_time_period = [
            "# Written by Timeline 0.5.0dev785606221dc2 on 2009-9-22 19:1:10",
            "PREFERRED-PERIOD:2008-12-9 11:32:26;2008-12-9 11:32:26",
            "CATEGORY:Work;173,216,230;True",
            "CATEGORY:Private;200,200,200;True",
            "EVENT:2009-7-13 0:0:0;2009-7-18 0:0:0;Programming course;Work",
            "EVENT:2009-7-10 14:30:0;2009-7-10 14:30:0;Go to dentist;Private",
            "EVENT:2009-7-20 0:0:0;2009-7-27 0:0:0;Vacation;Private",
            "# END",
        ]
        self.write_timeline(self.invalid_time_period_file, invalid_time_period)
        valid = [
            "# Written by Timeline 0.5.0 on 2009-9-22 19:1:10",
            "# END",
        ]
        self.write_timeline(self.valid_file, valid)

    def write_timeline(self, path, lines):
        f = file(path, "w")
        f.write("\n".join(lines))
        f.close()


class FileTimelineQuuoteFunctionsSpec(unittest.TestCase):

    def testQuote(self):
        # None
        self.assertEqual(quote("plain"), "plain")
        # Single
        self.assertEqual(quote("foo;bar"), "foo\\;bar")
        self.assertEqual(quote("foo\nbar"), "foo\\nbar")
        self.assertEqual(quote("foo\\bar"), "foo\\\\bar")
        self.assertEqual(quote("foo\\nbar"), "foo\\\\nbar")
        self.assertEqual(quote("\\;"), "\\\\\\;")
        # Mixed
        self.assertEqual(quote("foo\nbar\rbaz\\n;;"),
                         "foo\\nbar\\rbaz\\\\n\\;\\;")

    def testDequote(self):
        self.assertEqual(dequote("\\\\n"), "\\n")

    def testQuoteDequote(self):
        for s in ["simple string", "with; some;; semicolons",
                  "with\r\n some\n\n newlines\n"]:
            self.assertEqual(s, dequote(quote(s)))

    def testSplit(self):
        self.assertEqual(split_on_semicolon("one;two\\;;three"),
                         ["one", "two\\;", "three"])
