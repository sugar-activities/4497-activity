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
import unittest

from mock import Mock

from timelinelib.db.backends.memory import MemoryDB
from timelinelib.db.exceptions import TimelineIOError
from timelinelib.db.objects import Category
from timelinelib.db.objects import Event
from timelinelib.db.objects import TimePeriod
from timelinelib.drawing.viewproperties import ViewProperties
from timelinelib.time import PyTimeType


class MemoryDBSpec(unittest.TestCase):

    def testInitialState(self):
        db = MemoryDB()
        self.assertEquals(db.path, "")
        self.assertEquals(db.displayed_period, None)
        self.assertEquals(db.hidden_categories, [])
        self.assertEquals(db.is_read_only(), False)
        self.assertEquals(db.supported_event_data(), ["description", "icon", "alert", "hyperlink"])
        self.assertEquals(db.search(""), [])
        self.assertEquals(db.get_all_events(), [])
        self.assertEquals(db.get_first_event(), None)
        self.assertEquals(db.get_last_event(), None)
        self.assertEquals(db.get_categories(), [])

    def testLoadSaveViewProperties(self):
        # Make sure the database contains categories
        self.db.save_category(self.c1)
        self.db.save_category(self.c2)
        # Set up a view properties object that simulates having selected a
        # specific period and hidden one category
        vp = ViewProperties()
        vp.set_category_visible(self.c1, False)
        start = datetime(2010, 3, 23)
        end = datetime(2010, 3, 24)
        tp = TimePeriod(self.db.get_time_type(), start, end)
        vp.displayed_period = tp
        # Save these properties and assert that the database fields are written
        # correctly
        self.db.save_view_properties(vp)
        self.assertEquals(self.db.displayed_period, tp)
        self.assertEquals(self.db.hidden_categories, [self.c1])
        # Load view properties from db simulating that this db was just loaded
        # into memory and the view is being configured
        new_vp = ViewProperties()
        self.db.load_view_properties(new_vp)
        self.assertFalse(new_vp.category_visible(self.c1))
        self.assertTrue(new_vp.category_visible(self.c2))
        self.assertEquals(new_vp.displayed_period, self.db.displayed_period)
        # Assert virtual _save method called: 2 save categories, 1 save view
        # properties
        self.assertEquals(self.db._save.call_count, 3)

    def testSaveInvalidDisplayedPeriod(self):
        # Assign a zero-period as displayed period
        vp = ViewProperties()
        start = datetime(2010, 3, 23)
        end = datetime(2010, 3, 23)
        tp = TimePeriod(PyTimeType(), start, end)
        vp.displayed_period = tp
        # Assert error when trying to save
        self.assertRaises(TimelineIOError, self.db.save_view_properties, vp)

    def testGetSetDisplayedPeriod(self):
        tp = TimePeriod(self.db.get_time_type(), datetime(2010, 3, 23),
                        datetime(2010, 3, 24))
        self.db._set_displayed_period(tp)
        # Assert that we get back the same period
        self.assertEquals(self.db._get_displayed_period(), tp)
        # Assert that the period is correctly loaded into ViewProperties
        vp = ViewProperties()
        self.db.load_view_properties(vp)
        self.assertEquals(vp.displayed_period, tp)

    def testGetSetHiddenCategories(self):
        # Assert that we cannot include categories not in the db
        self.assertRaises(ValueError, self.db._set_hidden_categories, [self.c1])
        self.db._set_hidden_categories([])
        self.db.save_category(self.c1)
        self.db.save_category(self.c2)
        self.db._set_hidden_categories([self.c1])
        # Assert that the returned list is the same
        self.assertEquals(self.db._get_hidden_categories(), [self.c1])
        # Assert that category visibility information is correctly written to
        # ViewProperties
        vp = ViewProperties()
        self.db.load_view_properties(vp)
        self.assertFalse(vp.category_visible(self.c1))
        self.assertTrue(vp.category_visible(self.c2))

    def testSaveNewCategory(self):
        self.db.save_category(self.c1)
        self.assertTrue(self.c1.has_id())
        self.assertEqual(self.db.get_categories(), [self.c1])
        self.assertEqual(self.db_listener.call_count, 1)
        # Assert virtual _save method called: 1 save category
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveExistingCategory(self):
        self.db.save_category(self.c1)
        id_before = self.c1.id
        self.c1.name = "new name"
        self.db.save_category(self.c1)
        self.assertEqual(id_before, self.c1.id)
        self.assertEqual(self.db.get_categories(), [self.c1])
        self.assertEqual(self.db_listener.call_count, 2) # 2 save
        # Assert virtual _save method called: 2 save category
        self.assertEquals(self.db._save.call_count, 2)

    def testSaveNonExistingCategory(self):
        other_db = MemoryDB()
        other_db.save_category(self.c1)
        # It has id but is not in this db
        self.assertRaises(TimelineIOError, self.db.save_category, self.c1)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testSaveCategoryWithUnknownParent(self):
        self.c1.parent = self.c2
        # c2 not in db so we should get exception
        self.assertRaises(TimelineIOError, self.db.save_category, self.c1)
        # But after c2 is added everything is fine
        self.db.save_category(self.c2)
        self.db.save_category(self.c1)

    def testSaveCategoryWithParentChange(self):
        # Start with this hierarchy:
        # c1
        #   c11
        #     c111
        #   c12
        c1 = Category("c1", (255, 0, 0), None, True, parent=None)
        c11 = Category("c11", (255, 0, 0), None, True, parent=c1)
        c111 = Category("c111", (255, 0, 0), None, True, parent=c11)
        c12 = Category("c12", (255, 0, 0), None, True, parent=c1)
        self.db.save_category(c1)
        self.db.save_category(c11)
        self.db.save_category(c111)
        self.db.save_category(c12)
        # Changing c11's parent to c12 should create the following tree:
        # c1
        #   c12
        #     c11
        #       c111
        c11.parent = c12
        self.db.save_category(c11)
        self.assertEquals(c1.parent, None)
        self.assertEquals(c12.parent, c1)
        self.assertEquals(c11.parent, c12)
        self.assertEquals(c111.parent, c11)
        # Changing c11's parent to c111 should raise exception since that would
        # create a circular parent link.
        c11.parent = c111
        self.assertRaises(TimelineIOError, self.db.save_category, c11)

    def testDeleteExistingCategory(self):
        # Add two categories to the db
        self.db.save_category(self.c1)
        self.db.save_category(self.c2)
        # Make category 1 hidden
        vp = ViewProperties()
        vp.set_category_visible(self.c1, False)
        self.db.save_view_properties(vp)
        # Assert both categories in db
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 2)
        self.assertTrue(self.c1 in categories)
        self.assertTrue(self.c2 in categories)
        # Remove first (by category)
        self.db.delete_category(self.c1)
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 1)
        self.assertTrue(self.c2 in categories)
        self.assertFalse(self.c1.has_id())
        self.assertFalse(self.c1 in self.db.hidden_categories)
        # Remove second (by id)
        self.db.delete_category(self.c2.id)
        categories = self.db.get_categories()
        self.assertEquals(len(categories), 0)
        self.assertFalse(self.c2.has_id())
        # Check events
        self.assertEqual(self.db_listener.call_count, 4) # 2 save, 2 delete
        # Assert virtual _save method called: 2 save category, 1 save view
        # properties, 2 delete categories
        self.assertEquals(self.db._save.call_count, 5)

    def testDeleteNonExistingCategory(self):
        self.assertRaises(TimelineIOError, self.db.delete_category, self.c1)
        self.assertRaises(TimelineIOError, self.db.delete_category, 5)
        other_db = MemoryDB()
        other_db.save_category(self.c2)
        self.assertRaises(TimelineIOError, self.db.delete_category, self.c2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testDeleteCategoryWithParent(self):
        # Create hierarchy:
        # c1
        #   c11
        #   c12
        #     c121
        c1 = Category("c1", (255, 0, 0), None, True, parent=None)
        c11 = Category("c11", (255, 0, 0), None, True, parent=c1)
        c12 = Category("c12", (255, 0, 0), None, True, parent=c1)
        c121 = Category("c121", (255, 0, 0), None, True, parent=c12)
        self.db.save_category(c1)
        self.db.save_category(c11)
        self.db.save_category(c12)
        self.db.save_category(c121)
        # Delete c12 should cause c121 to get c1 as parent
        self.db.delete_category(c12)
        self.assertEquals(c121.parent, c1)
        # Delete c1 should cause c11, and c121 to be parentless
        self.db.delete_category(c1)
        self.assertEquals(c11.parent, None)
        self.assertEquals(c121.parent, None)

    def testDelteCategoryWithEvent(self):
        # Create hierarchy:
        # c1
        #   c11
        c1 = Category("c1", (255, 0, 0), None, True, parent=None)
        c11 = Category("c11", (255, 0, 0), None, True, parent=c1)
        self.db.save_category(c1)
        self.db.save_category(c11)
        # Create event belonging to c11
        self.e1.category = c11
        self.db.save_event(self.e1)
        # Delete c11 should cause e1 to get c1 as category
        self.db.delete_category(c11)
        self.assertEquals(self.e1.category, c1)
        # Delete c1 should cause e1 to have no category
        self.db.delete_category(c1)
        self.assertEquals(self.e1.category, None)

    def testSaveEventUnknownCategory(self):
        # A new
        self.e1.category = self.c1
        self.assertRaises(TimelineIOError, self.db.save_event, self.e1)
        # An existing
        self.db.save_event(self.e2)
        self.e2.category = self.c1
        self.assertRaises(TimelineIOError, self.db.save_event, self.e2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveNewEvent(self):
        self.db.save_event(self.e1)
        tp = TimePeriod(self.db.get_time_type(), datetime(2010, 2, 12),
                        datetime(2010, 2, 14))
        self.assertTrue(self.e1.has_id())
        self.assertEqual(self.db.get_events(tp), [self.e1])
        self.assertEqual(self.db.get_all_events(), [self.e1])
        self.assertEqual(self.db_listener.call_count, 1) # 1 save
        # Assert virtual _save method called: 1 save event
        self.assertEquals(self.db._save.call_count, 1)

    def testSaveExistingEvent(self):
        self.db.save_event(self.e1)
        id_before = self.e1.id
        self.e1.text = "new text"
        self.db.save_event(self.e1)
        tp = TimePeriod(self.db.get_time_type(), datetime(2010, 2, 12),
                        datetime(2010, 2, 14))
        self.assertEqual(id_before, self.e1.id)
        self.assertEqual(self.db.get_events(tp), [self.e1])
        self.assertEqual(self.db.get_all_events(), [self.e1])
        self.assertEqual(self.db_listener.call_count, 2) # 1 save
        # Assert virtual _save method called: 2 save event
        self.assertEquals(self.db._save.call_count, 2)

    def testSaveNonExistingEvent(self):
        other_db = MemoryDB()
        other_db.save_event(self.e1)
        # It has id but is not in this db
        self.assertRaises(TimelineIOError, self.db.save_event, self.e1)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testDeleteExistingEvent(self):
        tp = TimePeriod(self.db.get_time_type(), datetime(2010, 2, 12),
                        datetime(2010, 2, 15))
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        # Assert both in db
        self.assertEquals(len(self.db.get_events(tp)), 2)
        self.assertTrue(self.e1 in self.db.get_events(tp))
        self.assertTrue(self.e2 in self.db.get_events(tp))
        # Delete first (by event)
        self.db.delete_event(self.e1)
        self.assertFalse(self.e1.has_id())
        self.assertEquals(len(self.db.get_events(tp)), 1)
        self.assertTrue(self.e2 in self.db.get_events(tp))
        # Delete second (by id)
        self.db.delete_event(self.e2.id)
        self.assertFalse(self.e2.has_id())
        self.assertEquals(len(self.db.get_events(tp)), 0)
        # Check events
        self.assertEqual(self.db_listener.call_count, 4) # 2 save, 2 delete
        # Assert virtual _save method called: 2 save event, 2 delete event
        self.assertEquals(self.db._save.call_count, 4)

    def testDeleteNonExistingEvent(self):
        self.assertRaises(TimelineIOError, self.db.delete_event, self.e1)
        self.assertRaises(TimelineIOError, self.db.delete_event, 5)
        other_db = MemoryDB()
        other_db.save_event(self.e2)
        self.assertRaises(TimelineIOError, self.db.delete_event, self.c2)
        # Assert virtual _save method not called
        self.assertEquals(self.db._save.call_count, 0)

    def testDisableEnableSave(self):
        self.db.save_category(self.c1)
        # Assert virtual _save method called: save enabled by default
        self.assertEquals(self.db._save.call_count, 1)
        self.db.disable_save()
        self.db.save_category(self.c1)
        self.assertEquals(self.db._save.call_count, 1) # still 1
        self.db.enable_save()
        self.assertEquals(self.db._save.call_count, 2)
        # Now do the same thing but tell enable not to call save
        self.db.disable_save()
        self.db.save_category(self.c1)
        self.db.enable_save(False)
        self.assertEquals(self.db._save.call_count, 2)
        # Enabling when enabled should not have any effect
        self.db.enable_save()
        self.assertEquals(self.db._save.call_count, 2)

    def testMoveEventForward(self):
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        self.db.save_event(self.e3)
        self.db.place_event_after_event(self.e1, self.e2)
        self.assertTrue(self.db.events[0] == self.e2 )
        self.assertTrue(self.db.events[1] == self.e1 )
        self.assertTrue(self.db.events[2] == self.e3 )

    def testMoveEventToEnd(self):
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        self.db.save_event(self.e3)
        self.db.place_event_after_event(self.e1, self.e3)
        self.assertTrue(self.db.events[0] == self.e2 )
        self.assertTrue(self.db.events[1] == self.e3 )
        self.assertTrue(self.db.events[2] == self.e1 )

    def testMoveEventBackward(self):
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        self.db.save_event(self.e3)
        self.db.place_event_before_event(self.e2, self.e1)
        self.assertTrue(self.db.events[0] == self.e2 )
        self.assertTrue(self.db.events[1] == self.e1 )
        self.assertTrue(self.db.events[2] == self.e3 )

    def testMoveEventToBeginning(self):
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        self.db.save_event(self.e3)
        self.db.place_event_before_event(self.e3, self.e1)
        self.assertTrue(self.db.events[0] == self.e3 )
        self.assertTrue(self.db.events[1] == self.e1 )
        self.assertTrue(self.db.events[2] == self.e2 )

    def testMoveEventToOriginalPlace(self):
        self.db.save_event(self.e1)
        self.db.save_event(self.e2)
        self.db.save_event(self.e3)
        self.db.place_event_before_event(self.e2, self.e2)
        self.assertTrue(self.db.events[0] == self.e1 )
        self.assertTrue(self.db.events[1] == self.e2 )
        self.assertTrue(self.db.events[2] == self.e3 )

    def testEventShouldNotBeFuzzyByDefault(self):
        self.assertFalse(self.e1.fuzzy)

    def testEventShouldNotBeLockedByDefault(self):
        self.assertFalse(self.e1.locked)

    def setUp(self):
        self.db = MemoryDB()
        self.db._save = Mock()
        self.db_listener = Mock()
        self.c1 = Category("work", (255, 0, 0), None, True)
        self.c2 = Category("private", (0, 255, 0), None, True)
        self.e1 = Event(self.db.get_time_type(), datetime(2010, 2, 13), datetime(2010, 2, 13),
                        "holiday")
        self.e2 = Event(self.db.get_time_type(), datetime(2010, 2, 14), datetime(2010, 2, 14),
                        "work starts")
        self.e3 = Event(self.db.get_time_type(), datetime(2010, 2, 15), datetime(2010, 2, 16),
                        "period")
        self.db.register(self.db_listener)
