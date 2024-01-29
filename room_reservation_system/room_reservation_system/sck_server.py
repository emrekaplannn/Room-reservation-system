import hashlib
import json
import secrets
import sqlite3
# from chatserver import DateTimeEncoder
from room_reservation.models import ReservationSystem
from websockets.sync import server
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from datetime import datetime

# Store a set of connected clients
connected_clients = set()

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


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



def adduser(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    with sqlite3.connect('project.sql3') as db:
        c = db.cursor()
        # Insert a new user into the database
        c.execute('INSERT INTO auth (username, password) VALUES (?, ?)', (username, hashed_password))
        db.commit()



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



def authenticate(sock):

    inp = sock.recv()

    data = json.loads(inp)

    # if there is token it is already authenticated
    if 'token' in data:
        token = data['token']
        username = data['username']
        return (True, username)
    
    username = data['username']
    password = data['password']

    if data['type']=='login' and login(username, password):
        token = secrets.token_hex(16)
        message = json.dumps({'token': token, 'username': username})
        sock.send(message)
        print(username + " has logged in.")
        return (True, username)
    elif data['type']=='register':
        adduser(username, password)
        token = secrets.token_hex(16)
        message = json.dumps({'token': token, 'username': username})
        sock.send(message)
        print(username + " has logged in.")
        return (True, username)
    else:
        return (False, None)
    
    return
    # self.conn.send("Enter username and password: ".encode())
    credentials = inp.strip()
    credentials = credentials.split(',')
    if (credentials[0] == 'token'):
        # print(credentials[2])
        return (True, credentials[2])
    username = credentials[0]
    password = credentials[1]
    # self.conn.send("Enter password: ".encode())
    # password = self.conn.recv(1024).decode().strip()

    # Perform authentication using existing login function
    if login(username, password):
        token = secrets.token_hex(16)
        # self.conn.send(token.encode())
        sock.send(token.encode())
        # self.conn.send("Authentication successful.\n".encode())
        print(username + " has logged in.")
        return (True, username)
    else:
        sock.send("Invalid Credentials".encode())
        return (False, None)



def broadcast(message):
    # Iterate over connected clients and send the message to each
    for client in connected_clients:
        try:
            client.send(message)
            print(f'Message sent to {client}')
        except ConnectionClosedOK:
            print('Client is terminating')
        except ConnectionClosedError:
            print('Client generated error')

def Agent(sock):
    try:
        # Add the client to the set of connected clients
        authenticated = False
        while not authenticated:
            (authenticated,username) = authenticate(sock)
        print('Authenticated')
        connected_clients.add(sock)
        print(f"Client connected: {sock}")

        while True:
            inp = sock.recv()
            print(f"Received message: {inp}")

            # message_json = json.dumps(inp)
            # sock.send(message_json.encode())

            # client_response = handle_message('user1', inp)
            # print(client_response)

            # message_bytes = json.dumps(client_response, cls=DateTimeEncoder).encode()
            # print(message_bytes.decode())

            command = json.loads(inp)
            command_message = command['message']

            reply_response = handle_message(username, command_message)
            notification_response = ''

            # client_response = handle_message(username, command_message)
            if command_message == 'LIST ORGANIZATION organization3' or command_message == 'ACCESS ORGANIZATION organization3':
                reply_response = ''


            first_word = command_message.split()[0]
            if first_word in ['ADD', 'RESERVE', 'PERRESERVE', 'DELETE', 'UPDATE']:
                notification_response = command_message
            general_response = handle_message(username, 'ACCESS ORGANIZATION organization3')

            response = {'notification': notification_response, 'general': general_response}

            message = json.dumps(response, cls=DateTimeEncoder)

            print('reply',reply_response)

            reply = json.dumps({'reply': reply_response},cls=DateTimeEncoder)
            sock.send(reply)

            # print(message)
            broadcast(message)

            # yolla = json.dumps(inp)
            # print(yolla)
            # broadcast(yolla)

    except ConnectionClosedOK:
        print('Client is terminating')
    except ConnectionClosedError:
        print('Client generated error')
    finally:
        # Remove the client from the set when the connection is closed
        if sock in connected_clients:
            connected_clients.remove(sock)

HOST = ""
PORT = 12345

srv = server.serve(Agent, host=HOST, port=PORT)
srv.serve_forever()
