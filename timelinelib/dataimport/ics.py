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


from datetime import date
from datetime import datetime
from os.path import abspath

from icalendar import Calendar

from timelinelib.calendar.gregorian import Gregorian, GregorianUtils
from timelinelib.data.db import MemoryDB
from timelinelib.data import Event
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.utils import ex_msg
import timelinelib.calendar.gregorian as gregorian


def import_db_from_ics(path):
    db = MemoryDB()
    db.set_readonly()
    _load(db, path)
    return db


def _load(db, path):
    try:
        ics_file = open(path, "rb")
        try:
            file_contents = ics_file.read()
            try:
                cal = Calendar.from_ical(file_contents)
                for event in cal.walk("VEVENT"):
                    _load_event(db, event)
            except Exception, pe:
                msg1 = _("Unable to read timeline data from '%s'.")
                msg2 = "\n\n" + ex_msg(pe)
                raise TimelineIOError((msg1 % abspath(path)) + msg2)
        finally:
            ics_file.close()
    except IOError, e:
        msg = _("Unable to read from file '%s'.")
        whole_msg = (msg + "\n\n%s") % (abspath(path), e)
        raise TimelineIOError(whole_msg)


def _load_event(db, vevent):
    start, end = _extract_start_end(vevent)
    txt = ""
    if "summary" in vevent:
        txt = vevent["summary"]
    elif "description" in vevent:
        txt = vevent["description"]
    else:
        txt = "Unknown"
    e = Event(db.get_time_type(), start, end, txt)
    if "description" in vevent:
        e.set_data("description", vevent["description"])
    db.save_event(e)


def _extract_start_end(vevent):
    start = _convert_to_datetime(vevent.decoded("dtstart"))
    if "dtend" in vevent:
        end = _convert_to_datetime(vevent.decoded("dtend"))
    elif "duration" in vevent:
        end = start + vevent.decoded("duration")
    else:
        end = _convert_to_datetime(vevent.decoded("dtstart"))
    return (start, end)


def _convert_to_datetime(d):
    if isinstance(d, datetime):
        return Gregorian(d.year, d.month, d.day, d.hour, d.minute, d.second).to_time()
    elif isinstance(d, date):
        return GregorianUtils.from_date(d.year, d.month, d.day).to_time()
    else:
        raise TimelineIOError("Unknown date.")
