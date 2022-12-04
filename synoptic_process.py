import socket
import asyncio
from time import sleep

HEADER = 64
PORT = 5051
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.147.1"
ADDR = (SERVER, PORT)
connected = False

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
async def async_count(quanto):
    await asyncio.sleep(quanto)
    
async def try_connection_async():
  global connected
  while not connected:
    try:
      client.connect(ADDR)
      connected = True
    except:
      task_contador = asyncio.ensure_future(async_count(1))  #dispara um contador
      print('Conexão não estabelecida')
      await task_contador         #espera o contador terminar
      
asyncio.run(try_connection_async())
    
try:
    with open('historiador.txt', 'a') as f:
      while(1):
        msg = client.recv(2048).decode(FORMAT)
        print(msg)
        f.write(msg)
except Exception as e:
    print(e)
    send(DISCONNECT_MESSAGE)

# passa o setpoint uma vez e depois não pede mais
# imprime na tela os valores dos motores de 1 em um segundo
# só recebe dados do motor_control
# não precisa ler teclado
# pode ler no outro arquivo mesmo
