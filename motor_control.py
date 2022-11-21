import threading
from itertools import count
import time
from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket
#####################################################

# Inter Process Communication via TCP/IP
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length)
    server.send(message)
    #print(server.recv(2048).decode(FORMAT))

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
startCon = threading.Thread(target=start, args=())
startCon.start()

###############################################################################


class Motor (threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        # Simulation parameters
        self.T = 0.01  # sampling period
        # motor parameters
        self.Vmax = 20  # maximum armature voltage
        self.V = 0  # armature voltage(input)
        self.Ra = 0.78  # armature circuit resistance
        self.La = 0.016  # armature circuit inductance
        self.Ia = 1  # armature current #I CANT DECLARE THE CURRENT LIKE THIS. NEED TO FIX THIS LATER
        self.Km = 1  # torque constant
        self.Tm = 0  # motor's torque current value
        self.TL = 0  # load torque (disturbance)
        self.Jm = 5  # moment of inertia - slows the system dynamics down - time constant must be 10 times bigger than the sampling period
        self.B = 0.01  # viscous friction
        self.Wm = 0  # output shaft's angular speed (output)
        self.Kb = 1  # electric constant
        self.Wmax = (self.Vmax-self.Ia*self.Ra) / self.Kb  # maximum speed of the motor
        self.setPoint = []  # setPoint vector that is used to plot the graph
        self.y = []
        self.x = []
        self.active = False
        self.ini = 0
        self.ID = id

    def run(self):
        index = count()
        # motor's difference equations
        while (1):

            self.Tm = ((self.Km)*(self.V)-(self.Km*self.Kb*self.Wm) -
                       (self.Ra*self.Tm))*(self.T/self.La)+self.Tm
            self.Wm = (self.Tm-self.TL-(self.B*self.Wm)) * \
                (self.T/self.Jm)+self.Wm

            # adds the speed values to an array that is used to plot the graph
            self.y.append(self.Wm)
            # appends the sampling equivalent time to the x axis
            self.x.append(next(index)*(self.T))
            # the setpoint vector needs to be the same size of the y vector so they can be plotted together
            self.setPoint.append(self.Wmax/2)
            sleep(self.T)


class ControlThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # simulation parameters
        self.T = 0.1  # sampling time
        self.setPoint = []
        self.controlSignal = 0
        self.Kp = 4
        self.Ki = 1
        self.currentTime = time.time()
        self.previousTime = 0
        self.elapsedTime = 0
        self.cumError = 0
        self.error = 0

    def run(self):
        for j in range(len(motor_thread)):
            self.setPoint.append(0)  # cria um setpoint para cada motor

        while (1):
            # retirei o controle integrativo por agora, pois não estava funcionando com a gestão de tempo atual
            #self.previousTime = self.currentTime
            #self.currentTime = time.time()
            #self.elapsedTime = self.currentTime - self.previousTime
            # gestão dos motores energizados
            for i in range(len(motor_thread)):
                # se nao estou dentro do semaforo
                if (motor_thread[i].active == False):
                    # tento adquiri-lo. Se consigo...
                    if (sem.acquire(blocking=False) == True):
                        motor_thread[i].active = True  # digo que adquiri
                        self.setPoint[i] = motor_thread[i].Wmax / \
                            2  # seto o setpoint
                        # comeco a contar o tempo
                        motor_thread[i].ini = time.time()
                    else:  # se nao consigo adquirir o semaforo...
                        self.setPoint[i] = 0  # setpoint continua 0
                # se ja estou dentro do semaforo e ja se passaram 60 seg
                elif ((time.time()-motor_thread[i].ini) >= 60):
                    # zero setpoint
                    self.setPoint[i] = 0
                    # digo q nao estou no semaforo
                    motor_thread[i].active = False
                    sem.release()                                  # libero o semaforo

                # Controle dos motores
                self.error = self.setPoint[i] - motor_thread[i].Wm
                #self.cumError += self.error*self.elapsedTime
                #self.controlSignal = self.Kp*self.error + self.Ki*self.cumError
                self.controlSignal = self.Kp*self.error
                motor_thread[i].V = self.controlSignal

            sleep(self.T)


class LoggerThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while (1):
            try:
                with open('log.txt', 'a') as f:
                    for count, motor_log in enumerate(motor_thread):
                        msg = ("Motor " + str(count) + ":" + "\n\t" + "time: " +
                               str(datetime.now()) + "\n\t" + "Wm = " + str(motor_log.Wm) + "\n")
                        f.write(msg)
                        #send(msg)
                    msg = "###########################################################################\n"
                    f.write(msg)
                    #send(msg)
            except:
                print("Erro na escrita do arquivo")

            sleep(1)


######################################################
# Criando as threads
motor_thread = []

for i in range(30):
    motor_thread.append(Motor(i))

# Iniciando novas threads
for motor in motor_thread:
    # print(motor.ID)
    motor.start()

# Iniciando ControlThread
softPLC = ControlThread()
sem = threading.Semaphore(12)  # semaforo para doze motores simultaneos
softPLC.start()

# Iniciando LoggerThread
velocityLog = LoggerThread()
velocityLog.start()

##############
# Plotando
plt.style.use('fivethirtyeight')


def animate(i):
    x = motor_thread[0].x
    y1 = motor_thread[0].y
    y2 = motor_thread[0].setPoint

    plt.cla()
    plt.plot(x, y1, label='Motor 0')
    plt.plot(x, y2, label='Setpoint')
    plt.legend(loc='upper left')
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=500)

plt.tight_layout()
plt.show()
