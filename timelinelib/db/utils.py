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


import codecs
import os.path

from timelinelib.db.exceptions import TimelineIOError


def safe_write(path, encoding, write_fn):
    """
    Write to path in such a way that the contents of path is only modified
    correctly or not modified at all.

    In some extremely rare cases the contents of path might be incorrect, but
    in those cases the correct content is always present in another dbfile.
    """
    def raise_error(specific_msg, cause_exception):
        err_general = _("Unable to save timeline data to '%s'. File left unmodified.") % path
        err_template = "%s\n\n%%s\n\n%%s" % err_general
        raise TimelineIOError(err_template % (specific_msg, cause_exception))
    tmp_path = create_non_exising_path(path, "tmp")
    backup_path = create_non_exising_path(path, "bak")
    # Write data to tmp dbfile
    try:
        if encoding is None:
            dbfile = open(tmp_path, "wb")
        else:
            dbfile = codecs.open(tmp_path, "w", encoding)
        try:
            try:
                write_fn(dbfile)
            except Exception, e:
                raise_error(_("Unable to write timeline data."), e)
        finally:
            dbfile.close()
    except IOError, e:
        raise_error(_("Unable to write to temporary dbfile '%s'.") % tmp_path, e)
    # Copy original to backup (if original exists)
    if os.path.exists(path):
        try:
            os.rename(path, backup_path)
        except Exception, e:  # Can this only be a OSError?
            raise_error(_("Unable to take backup to '%s'.") % backup_path, e)
    # Copy tmp to original
    try:
        os.rename(tmp_path, path)
    except Exception, e:  # Can this only be a OSError?
        raise_error(_("Unable to rename temporary dbfile '%s' to original.") % tmp_path, e)
    # Delete backup (if backup was created)
    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
        except Exception, e:  # Can this only be a OSError?
            raise_error(_("Unable to delete backup dbfile '%s'.") % backup_path, e)


def create_non_exising_path(base, suffix):
    i = 1
    while True:
        new_path = "%s.%s%i" % (base, suffix, i)
        if os.path.exists(new_path):
            i += 1
        else:
            return new_path


def safe_locking(controller, edit_function, exception_handler=None):
    if controller.ok_to_edit():
        try:
            edit_function()
        except Exception, e:
            if exception_handler is not None:
                controller.edit_ends()
                exception_handler(e)
            else:
                raise
        finally:
            controller.edit_ends()
