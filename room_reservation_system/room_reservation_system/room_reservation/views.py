#views.py
import time
from django.http import HttpResponse
from django.shortcuts import render
from django import forms
# from room_reservation_system.chatclient import ChatClient
from room_reservation_system.sck_client import WebSocketClient
from asgiref.sync import sync_to_async

def index(request):
    return HttpResponse("You're at the room_reservation index.")

class AuthForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

class CommandForm(forms.Form):
    command = forms.CharField(label='command', max_length=100)

async def auth_form(request):
    token_with_username = None
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            # Extract the command from the form data
            print("form is valid")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # chat_client = ChatClient("localhost", 1423)
            websocketclient = WebSocketClient("ws://localhost:12345")

            credentials = username + "," + password
            # chat_client.send_messages(credentials)
            print(credentials)
            # await websocketclient.send_messages(credentials)
            # token = chat_client.receive_messages()
            # token = await websocketclient.receive_notifications()
            # if token == 'Invalid credentials':
            #     return HttpResponse('Invalid Credentials')
            # chat_client.close()
            # print('haha')
            # print(token_message)
            # print('wawa')
            # print(token)
            # print(token)
            print(username)
            # token_with_username = 'token' + ',' + token + ',' + username
            # print(token)
            await sync_to_async(request.session.__setitem__)('token', token_with_username)
            await sync_to_async(request.session.__setitem__)('websocketclient', websocketclient)



            # Render the HTML template with the server response
            # return render(request, 'response.html', { 'response': token_with_username})


    else:
        form = AuthForm()

    return render(request, 'form.html', {'form': form, 'response': token_with_username})

def command_form(request):
    response = None
    token = request.session.get('token', None)
    if token is None:
        return HttpResponse('No token found in session. Please authenticate first.')
    if request.method == 'POST':
        form = CommandForm(request.POST)
        if form.is_valid():
            command = form.cleaned_data['command']

            # Use the command and the token here...
            # For example, send them to the server:
            # print('token is ' + token)
            # chat_client = ChatClient("localhost", 1423)
            websocketclient = WebSocketClient("ws://localhost:12345")
            # chat_client.send_messages(token)
            websocketclient.send_messages(token)
            time.sleep(0.1)
            # chat_client.send_messages(command)
            websocketclient.send_messages(command)
            print(command)
            # response = chat_client.receive_messages()
            response = websocketclient.receive_notifications()
            # print('dort')

            # return render(request, 'response.html', {'response': response})

    else:
        form = CommandForm()

    return render(request, 'form.html', {'form': form, 'response': response})


def notification_view(request):
    return render(request, 'notification.html')

def auth_view(request):
    return render(request, 'auth.html')

def signup_view(request):
    return render(request, 'signup.html')