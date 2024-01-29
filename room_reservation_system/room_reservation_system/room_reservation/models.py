import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "room_reservation_system.settings")
django.setup()

#models.py
import hashlib
import sqlite3
from collections import defaultdict
from django.db import models
import sys
import json
from datetime import timedelta
from django.utils import timezone
import datetime
from django.contrib.auth.models import User as DjangoUser




# room_reservation_system/models.py
class ReservationSystemNotifications:
    _subscribers = set()

    @classmethod
    def subscribe(cls, subscriber):
        cls._subscribers.add(subscriber)

    @classmethod
    def unsubscribe(cls, subscriber):
        cls._subscribers.remove(subscriber)

    @classmethod
    def notify(cls, instance, message):
        for subscriber in cls._subscribers:
            subscriber.receive_notification(instance, message)

class ReservationSystem:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ReservationSystem, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.room = ReservationSystem.Room
            self.event = ReservationSystem.Event
            self.view = ReservationSystem.View
            self.organization = ReservationSystem.Organization
            self.initialized = True

    def get_room_class(self):
        return self.room

    def get_event_class(self):
        return self.event

    def get_view_class(self):
        return self.view

    def get_organization_class(self):
        return self.organization

    
    class Room(models.Model):
        name = models.CharField(max_length=200)
        x = models.FloatField()
        y = models.FloatField()
        capacity = models.IntegerField()
        working_hours_start = models.DateTimeField()
        working_hours_end = models.DateTimeField()
        permissions = models.JSONField(default=dict)  # Add a permissions field


        def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            ReservationSystemNotifications.notify(self, "Room has been saved.")

        def delete(self, *args, **kwargs):
            ReservationSystemNotifications.notify(self, "Room has been deleted.")
            super().delete(*args, **kwargs)

        def get_id(self):
            return self.id

        @classmethod
        def attach(cls, room_id):
            return cls.objects.get(id=room_id)


        def detach(self):
            print(f"Room {self.name} (ID: {self.id}) detached.")
            self = None

        @classmethod
        def list_objects(cls):
            return cls.objects.all()

        @classmethod
        def constructor(cls, name, x, y, capacity, working_hours_start, working_hours_end, permissions=None):
            room = cls(
                name=name,
                x=x,
                y=y,
                capacity=capacity,
                working_hours_start=working_hours_start,
                working_hours_end=working_hours_end,
                permissions=permissions
            )
            room.save()
            return room
        
        #get JSON data of room
        def get_room(self):
            return {
                'id': self.id,
                "name": self.name,
                "x": self.x,
                "y": self.y,
                "capacity": self.capacity,
                "working_hours_start": self.working_hours_start,
                "working_hours_end": self.working_hours_end,
                "permissions": self.permissions,
            }

        # Update the room with new values.
        def update_room(self, name=None, x=None, y=None, capacity=None,working_hours_start=None, working_hours_end=None, permissions=None):
            # for key, value in kwargs.items():
            #     setattr(self, key, value)
            # self.save()


            if name:
                self.name = name
            if x:
                self.x = x
            if y:
                self.y = y
            if capacity:
                self.capacity = capacity
            if working_hours_start:
                self.working_hours_start = working_hours_start
            if working_hours_end:
                self.working_hours_end = working_hours_end
            if permissions:
                self.permissions = permissions
            self.save()

        # Delete room
        def delete_room(self):
            self.delete()

        def list_events_user(self):
            reservations = ReservationSystem.Event.objects.filter(room=self)
            event_list = []

            for event in reservations:
                event_info = {
                    'title': event.title,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                }
                event_list.append(event_info)

            return event_list
        
        def reserve_room_user(self, event, start_time):
            # Check if the user has RESERVE permission
            # we did the perreserve part too in the reserve function
            if (True): # Assuming the user has write permission
                return self.organization.reserve(event, self, start_time)

            return False  # Reservation failed
        
        def delete_room_user(self):
            if (True): # Assuming the user has write permission
                self.delete_room()
            print('You do not have permission to delete this room.')
        



    class Event(models.Model):
        title = models.CharField(max_length=200)
        description = models.TextField()
        category = models.CharField(max_length=200)
        capacity = models.IntegerField()
        duration = models.IntegerField()
        weekly = models.DateTimeField(null=True, blank=True)
        permissions = models.JSONField(default=dict)  # Add a permissions field
        room = models.ForeignKey('Room', on_delete=models.CASCADE, null=True, blank=True, related_name='events')
        start_time = models.DateTimeField(null=True, blank=True)
        end_time = models.DateTimeField(null=True, blank=True)

        def save(self, *args, **kwargs):
            super().save(*args, **kwargs)
            ReservationSystemNotifications.notify(self, "Event has been saved.")

        def delete(self, *args, **kwargs):
            ReservationSystemNotifications.notify(self, "Event has been deleted.")
            super().delete(*args, **kwargs)

        def get_id(self):
            return self.id

        @classmethod
        def attach(cls, event_id):
            return cls.objects.get(id=event_id)


        def detach(self):
            print(f"Event {self.name} (ID: {self.id}) detached.")
            self = None

        @classmethod
        def list_objects(cls):
            return cls.objects.all()


        @classmethod
        def constructor(cls, title, description, category, capacity, duration, weekly=None, permissions=None, room=None, start_time=None, end_time=None):
            event = cls(
                title=title,
                description=description,
                category=category,
                capacity=capacity,
                duration=duration,
                weekly=weekly,
                permissions=permissions,
                room=room,
                start_time=start_time,
                end_time=end_time,
            )
            event.save()
            return event

        #get JSON data of event
        def get(self):
            return{
                'title': self.title,
                'description': self.description,
                'category': self.category,
                'capacity': self.capacity,
                'duration': self.duration,
                'weekly': self.weekly.isoformat() if self.weekly else None,
                'permissions': self.permissions,
                'room': self.room.get_room() if self.room else None,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
            }

        # Update the event with new values.
        def update(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            self.save()

        def delete_event_room(self):
            self.weekly=None
            self.room=None
            self.start_time=None
            self.end_time=None
            self.save()

        def update_event_room(self,title,description,category,capacity,duration):
            self.title = title
            self.description = description
            self.category = category
            self.capacity = capacity
            self.duration = duration
            self.save()


        # Delete event
        def delete_event(self):
            self.delete()

        def read_event(self):
            if (True): # if it has permission
                return self.get()
            print('BUSY') # If not granted room will be displayed as BUSY without any other detail.

        def delete_event_user(self):
            if (True): # if it has permission
                self.delete_event()
            print('You do not have permission to delete this event.')

        def update_event_user(self, **kwargs):
            if (True):
                self.update(**kwargs)
            print('You do not have permission to update this event.')

















    class View(models.Model):
        # owner = models.CharField(max_length=255)
        # queries = []

        def __init__(self, owner):
            self.owner = owner
            self.queries = {}

        def __str__(self):
            return self.owner + " "
            

        def add_query(self, organization, **kwargs):
            query_id = len(self.queries) + 1
            self.queries[query_id] = {"organization": organization, "params": kwargs}
            return query_id

        def del_query(self, qid):
            # self.queries = [query for query in self.queries if query.get('qid') != qid]
            # del self.queries[qid-1]
            if qid in self.queries:
                del self.queries[qid]

        def room_view(self, start, end):
            result = defaultdict(list)
            for query_id, query_data in self.queries.items():
                organization = query_data["organization"]
                params = query_data["params"]
                query_result = organization.query(**params)

                for event, room, event_start in query_result:
                    if start <= event_start <= end:
                        if room:
                            result[room.name].append({
                                "event_id": event.id,
                                "title": event.title,
                                "start_time": event_start,
                            })

            return dict(result)

        
        def day_view(self, start, end):
            result = defaultdict(list)
            for query_id, query_data in self.queries.items():
                organization = query_data["organization"]
                params = query_data["params"]
                query_result = organization.query(**params)

                for event, room, event_start in query_result:
                    if start <= event_start <= end:
                        day_key = event_start.date()
                        result[day_key].append({
                            "event_id": event.id,
                            "title": event.title,
                            "start_time": event_start,
                        })

            return dict(result)
        

        def receive_notification(self, instance, message):

            user = self.owner  # Assuming 'owner' is a reference to the User associated with the View.

            if isinstance(instance, ReservationSystem.Organization):
                # Handle notifications related to Organization
                ReservationSystemNotifications.notify(instance, f"Organization Notification: {message}")

            elif isinstance(instance, ReservationSystem.Room):
                # Handle notifications related to Room
                ReservationSystemNotifications.notify(instance, f"Room Notification: {message}")

            elif isinstance(instance, ReservationSystem.Event):
                # Handle notifications related to Event
                ReservationSystemNotifications.notify(instance, f"Event Notification: {message}")

            else:
                # Handle other types of notifications
                ReservationSystemNotifications.notify(instance, f"General Notification: {message}")






    class Organization(models.Model):
        owner = models.CharField(max_length=255)
        name = models.CharField(max_length=255)
        map_image = models.CharField(max_length=255, null=True, blank=True)
        permissions = models.JSONField(default=dict)  # Add a permissions field


        def __str__(self):
            return self.owner + " " + self.name + " " + self.get_id().__str__() + " " + self.permissions.__str__()

        @classmethod
        def constructor(cls, owner, name, map_image=None,permissions=None):
            organization = cls(owner=owner, name=name, map_image=map_image, permissions=permissions)
            organization.save()
            return organization

        def add_user_permission(self, user, permissions):
            """
            Add permissions for a user in the organization.

            Parameters:
                - user: User instance
                - permissions: Dictionary of permissions
            """
            user_id = user.id
            self.permissions[user_id] = permissions
            self.save()

        def remove_user_permission(self, user):
            """
            Remove permissions for a user in the organization.

            Parameters:
                - user: User instance
            """
            user_id = user.id
            if user_id in self.permissions:
                del self.permissions[user_id]
                self.save()

        def has_permission(self, user, operation, resource):
            """
            Check if a user has a specific permission in the organization.

            Parameters:
                - user: User instance
                - operation: CRUD operation (e.g., 'LIST', 'ADD', 'ACCESS')
                - resource: Resource being accessed (e.g., 'Room', 'Event')
            """
            user_id = user.id
            user_permissions = self.permissions.get(user_id, {})
            resource_permissions = user_permissions.get(resource, {})
            return operation in resource_permissions
        
        def has_list_permission(self, user, resource):
            return self.has_permission(user, 'LIST', resource)

        def has_add_permission(self, user, resource):
            return self.has_permission(user, 'ADD', resource)

        def has_access_permission(self, user, resource):
            return self.has_permission(user, 'ACCESS', resource)

        def get_id(self):
            return self.id

        @classmethod
        def attach(cls, organization_id):
            return cls.objects.get(id=organization_id)


        def detach(self):
            print(f"Organization {self.name} (ID: {self.id}) detached.")
            self = None

        @classmethod
        def list_objects(cls):
            return cls.objects.all()

        
        def Read(self):
            return {
                "owner": self.owner,
                "name": self.name,
                "map_image": str(self.map_image),
            }
            
        def Update(self, owner=None, name=None, map_image=None):
            if owner or name or map_image:
                if owner:
                    self.owner = owner
                if name:
                    self.name = name
                if map_image:
                    self.map_image = map_image
                self.save()
                return self
            
        def Delete(self):
            self.delete()
            return None
            
        # RUD operations
        def Read_room(self, room_id):
            try:
                room = ReservationSystem.Room.objects.get(id=room_id)
            except ReservationSystem.Room.DoesNotExist:
                return None 

            return {
                'id': room.id,
                "name": room.name,
                "x": room.x,
                "y": room.y,
                "capacity": room.capacity,
                "working_hours_start": room.working_hours_start,
                "working_hours_end": room.working_hours_end,
                "permissions": room.permissions,
            }

        def Update_room(self, room_id, name=None, x=None, y=None, capacity=None,working_hours_start=None, working_hours_end=None, permissions=None):
            try:
                room = ReservationSystem.Room.objects.get(id=room_id)
            except ReservationSystem.Room.DoesNotExist:
                return None 

            # Update room
            if name:
                room.name = name
            if x:
                room.x = x
            if y:
                room.y = y
            if capacity:
                room.capacity = capacity
            if working_hours_start:
                room.working_hours_start = working_hours_start
            if working_hours_end:
                room.working_hours_end = working_hours_end
            if permissions:
                room.permissions = permissions

            # room.update_room(name=name, x=x, y=y, capacity=capacity,working_hours_start=working_hours_start, working_hours_end=working_hours_end, permissions=permissions)
            room.save()
            return room

        def Delete_room(self, room_id):
            try:
                room = ReservationSystem.Room.objects.get(id=room_id)
            except ReservationSystem.Room.DoesNotExist:
                return None 

            room.delete_room()
            return None

        def reserve(self, event, room, start):


            end_time = start + timedelta(minutes=event.duration)

            # Check time
            existing_reservations = ReservationSystem.Event.objects.filter(
                room=room,
                weekly__isnull=True,
                start_time__lt=end_time,
                end_time__gt=start,
            )

            if not existing_reservations.exists():
                # Check capacity
                if room.capacity >= event.capacity:
                    if event.weekly and room.permissions == "PERWRITE":
                        event.update(
                            title=event.title,
                            description=event.description,
                            category=event.category,
                            capacity=event.capacity,
                            duration=event.duration,
                            weekly=event.weekly,
                            permissions=event.permissions,
                            room=room,
                            start_time=start,
                            end_time=end_time,
                        )
                        event.save()

                        # reservation.save()
                        return True  #successful
                    elif not event.weekly:
                        event.update(
                            title=event.title,
                            description=event.description,
                            category=event.category,
                            capacity=event.capacity,
                            duration=event.duration,
                            weekly=event.weekly,
                            permissions=event.permissions,
                            room=room,
                            start_time=start,
                            end_time=end_time,
                        )
                        event.save()
                        # reservation.save()
                        return True  # successful


        
        def findRoom(self, event, rect, start_time, end_time):
            
            rooms_within_rect = ReservationSystem.Room.objects.filter(
                x__gte=rect[0], y__gte=rect[1], x__lte=rect[2], y__lte=rect[3]
            )

            for room in rooms_within_rect:
                # Check time
                reservations = ReservationSystem.Event.objects.filter(
                    room=room,
                    weekly__isnull=True,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )

                if not reservations.exists():
                    # Check capacity
                    if room.capacity >= event.capacity:
                        yield {
                            "id": room.id,
                            "name": room.name,
                            "x": room.x,
                            "y": room.y,
                            "capacity": room.capacity,
                            "permissions": room.permissions,
                        }

        def findSchedule(self, event_list, rect, start, end):
            
            schedule = []

            start = timezone.make_aware(start)
            end = timezone.make_aware(end)

            for event in event_list:
                # Check time 
                
                if start <= event.start_time and end >= event.end_time:
                    if event.room:
                        # Check rectangle
                        if rect[0] <= event.room.x <= rect[2] and rect[1] <= event.room.y <= rect[3]:
                            schedule.append({
                                "event_id": event.id,
                                "title": event.title,
                                "room_id": event.room.id,
                                "room_name": event.room.name,
                                "start_time": event.start_time,
                                "end_time": event.end_time,
                            })
                        else:
                            return None  # outside of rectangle
                    else:
                        # Find available rooms with rectangle and time
                        available_rooms = self.findRoom(event, rect, start, end)
                        if available_rooms:
                            # Assign room to event
                            room = available_rooms[0]
                            event.room = ReservationSystem.Room.objects.get(id=room['id'])
                            event.save()

                            schedule.append({
                                "event_id": event.id,
                                "title": event.title,
                                "room_id": event.room.id,
                                "room_name": event.room.name,
                                "start_time": event.start_time,
                                "end_time": event.end_time,
                            })
                        else:
                            return None  # No room

            return schedule

        def reassign(self, event, new_room_id):
            try:
                new_room = ReservationSystem.Room.objects.get(id=new_room_id)
            except ReservationSystem.Room.DoesNotExist:
                return  # No room

            # Check permissions
            if event.permissions == "WRITE" and new_room.permissions == "WRITE":
                # Check time availability
                existing_reservations = ReservationSystem.Event.objects.filter(
                    room=new_room,
                    weekly__isnull=True,
                    start_time__lt=event.end_time,
                    end_time__gt=event.start_time,
                )

                if not existing_reservations.exists():
                    # Check the capacity
                    if new_room.capacity >= event.capacity:
                        event.room = None
                        event.save()

                        # Create new reservation
                        event.room = new_room
                        event.save()
                        return  #successful

            #no changes made

        def query(self, rect=None, title=None, category=None, room=None):

            query_set = ReservationSystem.Event.objects.all()

            if room:
                query_set = query_set.filter(room=room)

            if rect:
                x1, y1, x2, y2 = rect
                query_set = query_set.filter(
                    room__x__gte=x1,
                    room__y__gte=y1,
                    room__x__lte=x2,
                    room__y__lte=y2
                )

            if title:
                query_set = query_set.filter(title__icontains=title)

            if category:
                query_set = query_set.filter(category__icontains=category)

            for event in query_set:
                yield (event, event.room, event.start_time)

                
