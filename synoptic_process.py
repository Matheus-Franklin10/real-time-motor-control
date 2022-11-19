import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.96.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))
for i in range(5):
  velocity = input(f"Insira a velocidade angular do motor {i}: ")
  send(f"Velocidade angular do motor {i} é " + velocity)

send(DISCONNECT_MESSAGE)

#passa o setpoint uma vez e depois não pede mais
#imprime na tela os valores dos motores de 1 em um segundo
# só recebe dados do motor_control
#não precisa ler teclado
#pode ler no outro arquivo mesmo
