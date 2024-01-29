import socket
import threading

def receive_messages(sock):
    while True:
        data = sock.recv(4096).decode()
        if not data:
            break
        print(data)

def send_messages(sock):
    while True:
        message = input()
        sock.send(message.encode())

if __name__ == "__main__":
    HOST = 'localhost'  # Use 'localhost' for local testing
    PORT = 1423  # Change this to the port number you specified for the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    client_socket.close()
