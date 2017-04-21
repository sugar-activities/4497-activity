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


from StringIO import StringIO
import unittest
import xml.sax

import timelinelib.xml.parser as xmlparser


class TestXmlParser(unittest.TestCase):

    def testIllFormedXml(self):
        xml_stream = StringIO("""
        <root>
          <sub
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [])
        self.assertRaises(xml.sax.SAXException,
                          xmlparser.parse, xml_stream, tag_root, {})

    def testInvalidXmlUnexpectedTag(self):
        xml_stream = StringIO("""
        <root>
          <sub1>text</sub1>
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [
            xmlparser.Tag("sub", xmlparser.SINGLE, None, []),
        ])
        self.assertRaises(xmlparser.ValidationError,
                          xmlparser.parse, xml_stream, tag_root, {})

    def testInvalidXmlAttribute(self):
        xml_stream = StringIO("""
        <root foo="bar">
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [])
        self.assertRaises(xmlparser.ValidationError,
                          xmlparser.parse, xml_stream, tag_root, {})

    def testInvalidXmlTextBeforeTag(self):
        xml_stream = StringIO("""
        <root>
            <a>some text <b>here</b></a>
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [
            xmlparser.Tag("a", xmlparser.SINGLE, None, [
                xmlparser.Tag("b", xmlparser.SINGLE, None, []),
            ]),
        ])
        self.assertRaises(xmlparser.ValidationError,
                          xmlparser.parse, xml_stream, tag_root, {})

    def testInvalidXmlTextAfterTag(self):
        xml_stream = StringIO("""
        <root>
            <a><b>here</b> some text</a>
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [
            xmlparser.Tag("a", xmlparser.SINGLE, None, [
                xmlparser.Tag("b", xmlparser.SINGLE, None, []),
            ]),
        ])
        self.assertRaises(xmlparser.ValidationError,
                          xmlparser.parse, xml_stream, tag_root, {})

    def testInvalidXmlTooManyTags(self):
        xml_stream = StringIO("""
        <root>
            <a>some text</a>
            <a>some text</a>
        </root>
        """)
        tag_root = xmlparser.Tag("root", xmlparser.SINGLE, None, [
            xmlparser.Tag("a", xmlparser.SINGLE, None, []),
        ])
        self.assertRaises(xmlparser.ValidationError,
                          xmlparser.parse, xml_stream, tag_root, {})
