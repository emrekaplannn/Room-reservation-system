import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def receive_messages(self):
        while True:
            data = self.sock.recv(4096).decode()
            print(data)
            if data != None:
                return data
        
    # def receive_messages(self):
    #     while True:
    #         data = self.sock.recv(1024).decode()
    #         return data

    def send_messages(self, message):
        self.sock.send(message.encode())

    def start(self):
        receive_thread = threading.Thread(target=self.receive_messages)
        send_thread = threading.Thread(target=self.send_messages)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

    def close(self):
        self.sock.close()