import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "room_reservation_system.settings")
# django.setup()

from datetime import datetime, timedelta
from django.utils import timezone

import socket
import sqlite3
import sys
from threading import Thread, Lock, Condition
import hashlib
import json
import struct
from django.db import models
# from '../room_reservation_system/room_reservation/models.py' import RoomReservation
# from room_reservation.models import RoomReservation
from room_reservation.models import ReservationSystem

import secrets



class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

class Chat:
    def __init__(self):
        self.buf = []
        self.lock = Lock()
        self.newmess = Condition(self.lock)

    def newmessage(self, mess):
        self.lock.acquire()
        self.buf.append(mess)
        self.newmess.notify_all()
        self.lock.release()

    def getmessages(self, after=0):
        self.lock.acquire()
        if len(self.buf) < after:
            a = []
        else:
            a = self.buf[after:]
        self.lock.release()
        return a

class RDAgent(Thread):
    def __init__(self, conn, addr, chat):
        self.conn = conn
        self.claddr = addr
        self.chat = chat
        Thread.__init__(self)
        ChatServer.init_database()

    def run(self):
        #ChatServer.adduser('user2', 'password2')
        (authenticated,username) = self.authenticate()
        #ReservationSystem.Organization.constructor(owner='user1', name='organization7',map_image=None,permissions={'LIST': ['user1'], 'ADD': ['user1'], 'ACCESS': ['user1'], 'DELETE': ['user1'], 'WRITE': ['user1']})
        if not authenticated:
            print('client is terminating', self.claddr)
            self.conn.close()
            return
        # print('yaklastim')
        inp = self.conn.recv(4096)
        # print('daha cok yaklastim')
        while inp:
            # self.chat.newmessage(inp) 
            # This returns the message that came from the client to client
            # print('buradayim')
            message = ChatServer.handle_message(username , inp.decode())
            # print(message)
            # self.chat.newmessage(message)
            print(message)
            print('n/')
            message_bytes = json.dumps(message, cls=DateTimeEncoder).encode()
            print(message_bytes.decode())
            self.conn.send(message_bytes)
            print('waiting next', self.claddr)
            inp = self.conn.recv(4096)
        print('client is terminating', self.claddr)
        self.conn.close()

    def authenticate(self):
        # self.conn.send("Enter username and password: ".encode())
        credentials = self.conn.recv(4096).decode().strip()
        credentials = credentials.split(',')
        if (credentials[0] == 'token'):
            # print(credentials[2])
            return (True, credentials[2])
        username = credentials[0]
        password = credentials[1]
        # self.conn.send("Enter password: ".encode())
        # password = self.conn.recv(1024).decode().strip()

        # Perform authentication using existing login function
        if ChatServer.login(username, password):
            token = secrets.token_hex(16)
            self.conn.send(token.encode())
            # self.conn.send("Authentication successful.\n".encode())
            print(username + " has logged in.")
            return (True, username)
        else:
            self.conn.send("Invalid Credentials".encode())
            return (False, None)

class WRAgent(Thread):
    def __init__(self, conn, addr, chat):
        self.conn = conn
        self.claddr = addr
        self.chat = chat
        self.current = 0
        Thread.__init__(self)

    def run(self):
        oldmess = self.chat.getmessages()
        self.current += len(oldmess)
        self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
        notexit = True
        while notexit:
            self.chat.lock.acquire()
            self.chat.newmess.wait()
            self.chat.lock.release()
            oldmess = self.chat.getmessages(self.current)
            self.current += len(oldmess)
            try:
                self.conn.send('\n'.join([i.decode() for i in oldmess]).encode())
            except:
                notexit = False

class ChatServer:
    @staticmethod
    def login(username, password):
        with sqlite3.connect('project.sql3') as db:
            c = db.cursor()
            # Fetch user's data from the database
            c.execute('SELECT username, password FROM auth WHERE username=?', (username,))
            row = c.fetchone()

            # Check if the user exists and the password is correct
            if row and hashlib.sha256(password.encode()).hexdigest() == row[1]:
                return True
            return False

    @staticmethod
    def adduser(username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        with sqlite3.connect('project.sql3') as db:
            c = db.cursor()
            # Insert a new user into the database
            c.execute('INSERT INTO auth (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()

    @staticmethod
    def init_database():
        with sqlite3.connect('project.sql3') as db:
            c = db.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            db.commit()

    @staticmethod
    def handle_message(username, message):
        # Process the incoming message and interact with functions from models.py
        # For example, you might have logic to handle specific commands or actions
        # print(message)
        try:
            # Split the message into words
            words = message.split()
            
        # Check for the LIST command
            if (len(words) == 3 and words[0]) == 'LIST':
                object_name = words[2]
            # Check if the requested object is an organization
                if words[1] == 'ORGANIZATION':
                # Retrieve permission list for LIST operation
                    #print(ReservationSystem.Organization.objects.all())
                    permission_list = (ReservationSystem.Organization.list_objects().filter(name=object_name)[0].permissions.get('LIST', []))
                # Check if the user has permission to list objects in the organization
                    if username in permission_list:
                    # List all rooms in the organization
                        rooms = [room.get_room() for room in ReservationSystem.Room.list_objects()]
                        # print(rooms)
                        return rooms
                    else:
                        # print("No permission to list.")
                        return "No permission to list."
            # Check if the requested object is a room
                elif words[1] == 'ROOM':
                # Retrieve the specified room
                    room = ReservationSystem.Room.list_objects().filter(name=object_name)[0]
                    permission_list = room.permissions.get('LIST', [])
                # Check if the user has permission to list events in the room
                    if username in permission_list:
                    # List events in the room for the user
                        # print(room.list_events_user())
                        return room.list_events_user()
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

        # Check for the ADD command
            elif (len(words) == 9 and words[0]) == 'ADD':
                object_name = words[2]
                room_name = words[3]
                room_x = float(words[4])
                room_y = float(words[5])
                room_capacity = int(words[6])
                room_start = datetime.strptime(words[7], '%H:%M')
                room_end = datetime.strptime(words[8], '%H:%M')
            # Check if the requested object is an organization
                if words[1] == 'ORGANIZATION':
                # Retrieve permission list for ADD operation
                    permission_list = (ReservationSystem.Organization.list_objects().filter(name=object_name)[0].permissions.get('ADD', []))
                # Check if the user has permission to add objects to the organization
                    if username in permission_list:
                    # Add a new room to the organization
                        room = ReservationSystem.Room.constructor(
                            name=room_name,
                            x=room_x,
                            y=room_y,
                            capacity=room_capacity,
                            working_hours_start=room_start,
                            working_hours_end=room_end,
                            permissions={'LIST': [username], 'RESERVE': [username], 'PERRESERVE': [username], 'DELETE': [username], 'WRITE': [username]},
                        )
                        # if does not work delete get_room()
                        return 'Room added.'
                    else:
                        # print("No permission to add.")
                        return "No permission to add."
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

        # Check for the ACCESS command
            elif (len(words) == 3 and words[0]) == 'ACCESS':
                object_name = words[2]
            # Check if the requested object is an organization
                if words[1] == 'ORGANIZATION':
                # Retrieve permission list for ACCESS operation
                    permission_list = (ReservationSystem.Organization.list_objects().filter(name=object_name)[0].permissions.get('ACCESS', []))
                # Check if the user has permission to access objects in the organization
                    if username in permission_list:
                    # Print information about all rooms in the organization
                        rooms = [room.get_room() for room in ReservationSystem.Room.list_objects()]
                        # print(rooms)
                    # Print information about all events in the organization
                        # for event in ReservationSystem.Event.list_objects():
                        #     print(event.get())
                        events = [event.get() for event in ReservationSystem.Event.list_objects()]
                        result = rooms + events
                        print(result)

                        return result
                    else:
                        # print("No permission to access.")
                        return "No permission to access."
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

        # Check for the DELETE command
            elif ((len(words) == 3 or len(words)==4) and words[0]) == 'DELETE':
            # Check if the requested object is an organization            
                if words[1] == 'ORGANIZATION':
                    organization_name = words[2]
                    room_name = words[3]
                # Retrieve the organization
                    organization = (ReservationSystem.Organization.list_objects().filter(name=organization_name)[0])
                    permission_list = organization.permissions.get('DELETE', [])
                    permission_list2 = organization.permissions.get('WRITE', [])
                # Check if the user has permission to delete objects from the organization
                    if ((username in permission_list) and (username in permission_list2)) or (username == organization.owner):
                    # Delete the specified room from the organization
                        ReservationSystem.Room.list_objects().filter(name=room_name)[0].delete_room()
                        return 'Room deleted.'
                    else:
                        # print("No permission to delete.")
                        return "No permission to delete."

            # Check if the requested object is a room
                elif words[1] == 'ROOM':
                    room_name = words[2]
                    room = ReservationSystem.Room.list_objects().filter(name=room_name)[0]

                    permission_list = room.permissions.get('DELETE', [])
                # Check if the user has permission to delete the room
                    for event in ReservationSystem.Event.list_objects():
                        if event.room:
                            if event.room.name == room_name:
                                permission_list2 = event.permissions.get('WRITE', [])
                                if ((username in permission_list) and (username in permission_list2)):
                                    event.delete_event_room()
                                    return 'Event deleted from room.'
                                else:
                                    # print("No permission to delete.")
                                    return "No permission to delete."
            # Check if the requested object is an event
                elif words[1] == 'EVENT':
                    event_name = words[2]
                    room_name = words[3]
                    event = ReservationSystem.Event.list_objects().filter(title=event_name)[0]
                    room = ReservationSystem.Room.list_objects().filter(name=room_name)[0]
                    permission_list2 = event.permissions.get('WRITE', [])
                    permission_list = room.permissions.get('DELETE', [])
                # Check if the user has permission to delete the event
                    if ((username in permission_list) and (username in permission_list2)):
                    # Delete the event
                        event.delete_event()
                        return 'Event deleted.'
                    else:
                        # print("No permission to delete.")
                        return "No permission to delete."
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

            
        # Check for the RESERVE command
            elif (len(words) == 6 and words[0]) == 'RESERVE':
                organization_name = words[2]
                room_name = words[3]
                event_name = words[4]
                start = datetime.strptime(words[5], '%H:%M')
            # Retrieve the specified room, event, and organization
                room = ReservationSystem.Room.list_objects().filter(name=room_name)[0]
                event = ReservationSystem.Event.list_objects().filter(title=event_name)[0]
                organization = (ReservationSystem.Organization.list_objects().filter(name=organization_name)[0])
                permission_list = room.permissions.get('RESERVE', [])
            # Check if the user has permission to reserve the room for the event
                if (username in permission_list):
                # Reserve the room for the event
                    organization.reserve(event, room, start)
                    return 'Room reserved.'
                else:
                    # print("No permission to reserve.")
                    return "No permission to reserve."


        # Check for the PERRESERVE command
            elif (len(words) == 7 and words[0]) == 'PERRESERVE':
                organization_name = words[2]
                room_name = words[3]
                event_name = words[4]
                start = datetime.strptime(words[5], '%H:%M')
                weekly = datetime.strptime(words[6], '%H:%M')
                room = ReservationSystem.Room.list_objects().filter(name=room_name)[0]
                event = ReservationSystem.Event.list_objects().filter(title=event_name)[0]
                organization = (ReservationSystem.Organization.list_objects().filter(name=organization_name)[0])
                permission_list = room.permissions.get('RESERVE', [])


            # Check if the user has permission to reserve the room for the event
                if (username in permission_list):
                # Update the event with weekly information
                    organization.reserve(event, room, start)                    
                    event.update(weekly=weekly)
                    return 'Room perreserved.'
                # Reserve the room for the event
                else:
                    # print("No permission to reserve.")
                    return "No permission to reserve."

            
        # Check for the READ command
            elif (len(words) == 3 and words[0]) == 'READ':
                object_name = words[2]
            # Check if the requested object is an event
                if words[1] == 'EVENT':
                    event_name = words[2]
                    event = ReservationSystem.Event.list_objects().filter(title=event_name)[0]
                    permission_list = event.permissions.get('READ', [])
                # Check if the user has permission to read the event details
                    if username in permission_list:
                    # Print information about the event
                        # print(event.get())
                        return event.get()
                    else:
                        # print("BUSY!!")
                        return "BUSY!!"
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

        # Check for the UPDATE command
            elif (len(words) == 8 and words[0]) == 'UPDATE':
                title = words[3]
                description = words[4]
                category = words[5]
                capacity = words[6]
                duration = words[7]
            # Check if the requested object is an event
                if words[1] == 'EVENT':
                    event_name = words[2]
                    event = ReservationSystem.Event.list_objects().filter(title=event_name)[0]
                    permission_list = event.permissions.get('WRITE', [])
                # Check if the user has permission to update the event
                    if username in permission_list:
                    # Update the event with new information
                        event.update_event_room(title, description, category, capacity, duration)
                        return 'Event updated.'
                    else:
                        # print("No permission to update.")
                        return "No permission to update."
                else:
                    # print("Invalid message format.")
                    return "Invalid message format."

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if len(sys.argv) != 2:
    print('usage: ', sys.argv[0], 'port')
    sys.exit(-1)

HOST = ''
PORT = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

chatroom = Chat()

while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    a = RDAgent(conn, addr, chatroom)
    b = WRAgent(conn, addr, chatroom)
    a.start()
    b.start()

          # ReservationSystem.Organization.constructor('user1','organization3',map_image='',permissions = {'LIST': ['user1'],'ADD': ['user1'],'ACCESS': ['user1'],'DELETE': ['user1'],'WRITE': ['user1']})


            # ReservationSystem.Room.constructor(
            #     name='r1',
            #     x=10.0,
            #     y=20.0,
            #     capacity=200,
            #     working_hours_start=timezone.now(),
            #     working_hours_end=timezone.now() + timedelta(hours=8),
            #     permissions = {'LIST': ['user1'],'RESERVE': ['user1'],'PERRESERVE': ['user1'],'DELETE': ['user1'],'WRITE': ['user1']}
            # )
            
            # ReservationSystem.Event.constructor(
            #     title='e3',
            #     description='This is the haha',
            #     category='e2category',
            #     capacity=100,
            #     duration=120,
            #     permissions = {'READ': ['user1'],'WRITE': ['user1']},
            #     room = ReservationSystem.Room.list_objects().filter(name='r1')[0],
            # )

            # for event in ReservationSystem.Event.objects.all():
            #     print(event.get())
