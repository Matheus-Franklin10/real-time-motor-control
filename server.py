import socket 
import threading
from time import sleep

class IPC (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.HEADER = 64
        self.PORT = 5050
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.connected = False
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.clientConn = 0
    def run(self):
        print("[STARTING] server is starting...")
        
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        while True:
            conn, addr = self.server.accept()
            self.clientConn = conn
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")   

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        self.connected = True
        while self.connected:
            msg_length = conn.recv(self.HEADER).decode(self.FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.FORMAT)
                if msg == self.DISCONNECT_MESSAGE:
                    self.connected = False

                print(f"[{addr}] {msg}")
                conn.send("Msg received".encode(self.FORMAT))

        conn.close()

    def send(self, msg):
        while not self.connected:
            pass
        message = msg.encode(self.FORMAT)
        self.clientConn.send(message)


tcp_interface = IPC()
tcp_interface.start()

tcp_interface.send("test message")
