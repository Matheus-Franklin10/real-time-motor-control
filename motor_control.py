import threading
from itertools import count
import time
from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import socket
import asyncio
#####################################################

# Inter Process Communication via TCP/IP
class IPC (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.HEADER = 64
        self.PORT = 5051
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
        self.active = False  #flag para aquisição do semaforo sem_security
        self.ini = 0   #variavel para contagem de tempo
        self.ID = id  #identificação do motor
        self.sem_GV = threading.Semaphore(1) #semaforo para exclusao mutua no acesso das inputs e outputs dos motores
        self.index = 0

    def run(self):
        asyncio.run(self.async_exec())
      
    async def async_exec(self):
        self.index = count() 
                  
        while(1):
            task_motor_thread = asyncio.create_task(self.exec())
            task_contador = asyncio.ensure_future(self.async_count(0.1))
    
            await task_motor_thread
            await task_contador
            
            
    async def async_count(self, quanto):
        await asyncio.sleep(quanto) 
    
    async def exec(self):
        # motor's difference equations
            
        self.sem_GV.acquire()    #mutex para proteção de V e Wm
        self.Tm = ((self.Km)*(self.V)-(self.Km*self.Kb*self.Wm) -
                       (self.Ra*self.Tm))*(self.T/self.La)+self.Tm
        self.Wm = (self.Tm-self.TL-(self.B*self.Wm)) * \
                (self.T/self.Jm)+self.Wm
            
        # adds the speed values to an array that is used to plot the graph
        self.y.append(self.Wm)
        # appends the sampling equivalent time to the x axis
        self.x.append(next(self.index)*(self.T))
        # the setpoint vector needs to be the same size of the y vector so they can be plotted together
        self.setPoint.append(self.Wmax/2)
        self.sem_GV.release()


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
        asyncio.run(self.async_exec())
      
    async def async_exec(self):
        for j in range(len(motor_thread)):
            self.setPoint.append(0)  # cria um setpoint para cada motor
            
        while(1):
            task_control_thread = asyncio.create_task(self.exec())   #dispara execução da control thread
            task_contador = asyncio.ensure_future(self.async_count(0.2))  #dispara um contador
    
            await task_control_thread   #espera a control thread terminar
            await task_contador         #espera o contador terminar
            
            
    async def async_count(self, quanto):
        await asyncio.sleep(quanto)    


    async def exec(self):
        #disabled integrative controller
        #self.previousTime = self.currentTime
        #self.currentTime = time.time()
        #self.elapsedTime = self.currentTime - self.previousTime
        # gestão dos motores energizados
        for i in range(len(motor_thread)):
            # se nao estou dentro do semaforo
            if (motor_thread[i].active == False):
                if(motor_thread[i-1].active == False):  #garantir que dois motores em sequencia nao sejam acionados simultaneamente
                    # tento adquiri-lo. Se consigo...
                    if (sem_security.acquire(blocking=False) == True):
                        motor_thread[i].active = True  # digo que adquiri
                        motor_thread[i].sem_GV.acquire()
                        self.setPoint[i] = motor_thread[i].Wmax / \
                            2  # seto o setpoint
                        motor_thread[i].sem_GV.release()
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
                sem_security.release()                                  # libero o semaforo

            # Controle dos motores
            motor_thread[i].sem_GV.acquire()
            self.error = self.setPoint[i] - motor_thread[i].Wm
            #self.cumError += self.error*self.elapsedTime
            #self.controlSignal = self.Kp*self.error + self.Ki*self.cumError
            self.controlSignal = self.Kp*self.error
            motor_thread[i].V = self.controlSignal
            #print('Motor: ', motor_thread[i].ID, '  Velocidade: ', motor_thread[i].Wm, '  Setpoint: ', self.setPoint[i])
            motor_thread[i].sem_GV.release()
                
            



class LoggerThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        asyncio.run(self.async_exec())
      
    async def async_exec(self):            
        while(1):
            task_logger_thread = asyncio.create_task(self.exec())   #dispara execução da logger thread
            task_contador = asyncio.ensure_future(self.async_count(1))  #dispara um contador
    
            await task_logger_thread   #espera a logger thread terminar
            await task_contador         #espera o contador terminar
                    
    async def async_count(self, quanto):
        await asyncio.sleep(quanto) 

    async def exec(self):
        try:
            with open('log.txt', 'a') as f:
                for count, motor_log in enumerate(motor_thread):
                    motor_log.sem_GV.acquire()
                    msg = ("Motor " + str(count) + ":" + "\n\t" + "time: " +
                            str(datetime.now()) + "\n\t" + "Wm = " + str(motor_log.Wm) + "\n")
                    f.write(msg)
                    tcp_interface.send(msg)
                    motor_log.sem_GV.release()
                msg = "###########################################################################\n"
                f.write(msg)
                tcp_interface.send(msg)
        except Exception as e:
            print("Erro na escrita de log.txt: " + e)



######################################################
# Iniciando a IPC
tcp_interface = IPC()
tcp_interface.start()

# Criando as threads dos motores
motor_thread = []

for i in range(30):
    motor_thread.append(Motor(i))

# Iniciando novas threads
for motor in motor_thread:
    motor.start()

# Iniciando ControlThread
softPLC = ControlThread()

sem_security = threading.Semaphore(12)  # semaforo para doze motores simultaneos

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

