import os
from django.test import TestCase
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Room, Event, Organization, View
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "room_reservation_system.settings")
# django.setup()

class RoomEventOrganizationTest(TestCase):
    def setUp(self):
        # Create an organization for testing
        self.organization = Organization.constructor(owner='TestOwner', name='TestOrg')
        self.organization2 = Organization.constructor(owner='TestOwner2', name='TestOrg2')


        # Create a room for testing
        self.room = Room.constructor(
            name='TestRoom',
            x=10.0,
            y=20.0,
            capacity=30,
            working_hours_start=timezone.now(),
            working_hours_end=timezone.now() + timedelta(hours=8),
            permissions='WRITE'
        )

        self.room2 = Room.constructor(
            name='Room2',
            x=15.0,
            y=25.0,
            capacity=40,
            working_hours_start=timezone.now(),
            working_hours_end=timezone.now() + timedelta(hours=8),
            permissions='WRITE'
        )

        # Create an event for testing
        self.event = Event.constructor(
            title='TestEvent',
            description='This is a test event',
            category='Test',
            capacity=10,
            duration=60,
            permissions='WRITE',
            # room=self.room,
            # start_time=timezone.now(),
            # end_time=timezone.now() + timedelta(hours=1)
        )

        self.event2 = Event.constructor(
            title='Event2',
            description='This is the second test event',
            category='Test',
            capacity=20,
            duration=120,
            permissions='WRITE',
        )

    def test_organization_creation(self):
        self.assertEqual(self.organization.owner, 'TestOwner')
        self.assertEqual(self.organization.name, 'TestOrg')

    def test_room_creation(self):
        self.assertEqual(self.room.name, 'TestRoom')
        self.assertEqual(self.room.capacity, 30)

    def test_event_creation(self):
        self.assertEqual(self.event.title, 'TestEvent')
        self.assertEqual(self.event.capacity, 10)

    def test_event_reservation(self):
        # Test reserving the room for the event
        result = self.organization.reserve(self.event, self.room, timezone.now())
        self.assertTrue(result)

        # Test reassigning the event to another room
        new_room = Room.constructor(
            name='NewRoom',
            x=15.0,
            y=25.0,
            capacity=40,
            working_hours_start=timezone.now(),
            working_hours_end=timezone.now() + timedelta(hours=8),
            permissions='WRITE'
        )
        result = self.organization.reassign(self.event, new_room.id)
        self.assertIsNone(result)

    def test_invalid_event_reservation(self):
        # Test attempting to reserve a room for an event that is already reserved
        # other_organization = Organization.constructor(owner='OtherOwner', name='OtherOrg')
        
        result = self.organization.reserve(self.event, self.room, timezone.now())

        other_event = Event.constructor(
            title='OtherEvent',
            description='This is another test event',
            category='Other',
            capacity=15,
            duration=90,
            permissions='WRITE',
            # room=self.room,
            # start_time=timezone.now(),
            # end_time=timezone.now() + timedelta(hours=2)
        )
        result = self.organization.reserve(other_event, self.room, timezone.now())
        self.assertFalse(result)

    def test_query_organization(self):
        # Test querying organization
        self.organization.reserve(self.event, self.room, timezone.now())
        result = self.organization.query(rect=[0, 0, 30, 30],title='TestEvent', category='Test')
        self.assertEqual(len(list(result)), 1)

    def test_view_room(self):
        #Test creating a view and getting room view
        view = View(owner='TestOwner')
        self.organization.reserve(self.event, self.room, timezone.now())
        query_id = view.add_query(organization=self.organization, rect=[0, 0, 30, 30], title='TestEvent', category='Test')
        start_time = timezone.now()-timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        # print("Test View Room query:", view.queries)
        # print("Test View Room", self.room)
        result = view.room_view(start_time, end_time)
        # print("Test View Room Result:", result)
        self.assertEqual(len(result), 1)

    def test_event_capacity_failure(self):
        # Test attempting to reserve an event in a room with insufficient capacity
        self.room.capacity = 5  # Set room capacity lower than the event capacity
        self.room.save()
        result = self.organization.reserve(self.event, self.room, timezone.now())
        self.assertFalse(result)

    def test_organization_update(self):
        # Test updating organization details
        self.organization.Update(owner='NewOwner', name='NewOrg', map_image='new_image.jpg')
        updated_organization = Organization.attach(self.organization.id)
        self.assertEqual(updated_organization.owner, 'NewOwner')
        self.assertEqual(updated_organization.name, 'NewOrg')
        self.assertEqual(updated_organization.map_image, 'new_image.jpg')

    def test_room_update(self):
        # Test updating room details
        self.room.update_room(name='NewRoom', x=15.0, y=25.0, capacity=40, permissions='READ')
        updated_room = Room.attach(self.room.id)
        self.assertEqual(updated_room.name, 'NewRoom')
        self.assertEqual(updated_room.capacity, 40)
        self.assertEqual(updated_room.permissions, 'READ')

    # ... (additional test cases)

    def test_room_deletion(self):
        # Test deleting a room
        room_id = self.room.id
        self.room.delete_room()
        with self.assertRaises(Room.DoesNotExist):
            Room.attach(room_id)

    def test_event_deletion(self):
        # Test deleting an event
        event_id = self.event.id
        self.event.delete_event()
        with self.assertRaises(Event.DoesNotExist):
            Event.attach(event_id)

    def test_organization_deletion(self):
        # Test deleting an organization
        organization_id = self.organization.id
        self.organization.Delete()
        with self.assertRaises(Organization.DoesNotExist):
            Organization.attach(organization_id)


    #Update the test_view_day method
    def test_view_day(self):
        #Test creating a view and getting day view
        view = View(owner='TestOwner')
        self.organization.reserve(self.event, self.room, timezone.now())
        query_id = view.add_query(organization=self.organization, rect=[0, 0, 30, 30], title='TestEvent', category='Test')
        start_time = timezone.now()-timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        result = view.day_view(start_time, end_time)
        # print("Test View Day Result:", result)
        self.assertEqual(len(result), 1)





    

    def test_event_reservation_multiple_rooms(self):
        # Test reserving events in multiple rooms
        result1 = self.organization.reserve(self.event, self.room, timezone.now())
        result2 = self.organization.reserve(self.event2, self.room2, timezone.now())

        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_query_multiple_rooms(self):
        # Test querying organization with multiple rooms
        self.organization.reserve(self.event, self.room, timezone.now())
        self.organization.reserve(self.event2, self.room2, timezone.now())

        result = self.organization.query(rect=[0, 0, 30, 30], title='Event', category='Test')
        self.assertEqual(len(list(result)), 2)

    def test_view_room_multiple_rooms(self):
        # Test creating a view and getting room view with multiple rooms 
        view = View(owner='TestOwner')
        self.organization.reserve(self.event, self.room, timezone.now())
        self.organization.reserve(self.event2, self.room2, timezone.now())
        query_id = view.add_query(organization=self.organization, rect=[0, 0, 30, 30], title='Event', category='Test')

        start_time = timezone.now() - timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        result = view.room_view(start_time, end_time)

        self.assertEqual(len(result), 2)

    def test_view_day_multiple_rooms(self):
        # Test creating a view and getting day view with multiple rooms
        view = View(owner='TestOwner')
        self.organization.reserve(self.event, self.room, timezone.now())
        self.organization.reserve(self.event2, self.room2, timezone.now())
        query_id = view.add_query(organization=self.organization, rect=[0, 0, 30, 30], title='Event', category='Test')

        start_time = timezone.now() - timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)
        result = view.day_view(start_time, end_time)
        # print("Test View Day Result:", result)

        self.assertEqual(len(result), 1)
    
