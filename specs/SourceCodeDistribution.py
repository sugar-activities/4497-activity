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


import codecs
import os
import unittest
import datetime

from timelinelib.calendar.monthnames import english_name_of_month
from timelinelib.calendar.monthnames import month_from_english_name
import timelinelib.meta.about
import timelinelib.meta.version


class SourceCodeDistributionSpec(unittest.TestCase):

    IO = True

    def test_version_number_in_README_should_match_that_in_version_module(self):
        self.assertTrue(
            self.get_module_version_string() in
            self.read_first_line_from(self.README))

    def test_version_number_in_CHANGES_should_match_that_in_version_module(self):
        self.assertTrue(
            self.get_module_version_string() in
            self.read_first_line_from(self.CHANGES))

    def test_all_authors_mentioned_in_about_module_should_be_mentioned_in_AUTHORS(self):
        authors_content = self.read_utf8_encoded_text_from(self.AUTHORS)
        for author in self.get_authors_from_about_module():
            self.assertTrue(author in authors_content)

    def setUp(self):
        self.ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
        self.README = os.path.join(self.ROOT_DIR, "README")
        self.CHANGES = os.path.join(self.ROOT_DIR, "CHANGES")
        self.AUTHORS = os.path.join(self.ROOT_DIR, "AUTHORS")
        self.MANPAGE = os.path.join(self.ROOT_DIR, "man", "man1", "timeline.1")

    def get_authors_from_about_module(self):
        return [possible_author.strip()
                for possible_author
                in self.get_possible_authors_from_about_module()
                if self.is_author_from_about_module(possible_author)]

    def get_possible_authors_from_about_module(self):
        return (timelinelib.meta.about.DEVELOPERS +
                timelinelib.meta.about.TRANSLATORS +
                timelinelib.meta.about.ARTISTS)

    def is_author_from_about_module(self, possible_author):
        return possible_author and not self.is_header(possible_author)

    def is_header(self, possible_author):
        return ":" in possible_author

    def get_release_date_from_changes(self):
        first_line = self.read_first_line_from(self.CHANGES)
        date_str = first_line.split("released on ")[1]
        return self.parse_release_date_from(date_str)

    def parse_release_date_from(self, date_str):
        day_str, month_name, year_str = date_str.split(" ")
        return datetime.date(
            int(year_str),
            month_from_english_name(month_name),
            int(day_str))

    def release_date_in_man_format(self, date):
        return "%s %s" % (english_name_of_month(date.month), date.year)

    def get_module_version_string(self):
        return "%s.%s.%s" % timelinelib.meta.version.VERSION

    def read_first_line_from(self, path):
        f = open(path, "r")
        first_line = f.readline()
        f.close()
        return first_line

    def read_utf8_encoded_text_from(self, path):
        f = codecs.open(path, "r", "utf-8")
        content = f.read()
        f.close()
        return content
