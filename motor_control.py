import threading
from time import sleep
######################################################


class motor (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # parâmetros de simulação
        self.T = 0.01  # período de amostragem
        # parâmetros do motor
        self.V = 20  # tensão de armadura(entrada)
        self.Ra = 0.78  # resistência do circuito de armadura
        self.La = 0.016  # indutância do circuito de armadura
        self.ia = 1  # corrente de armadura
        self.Km = 1  # constante de torque
        self.Tm = 0  # torque atual do motor
        self.TL = 0  # toque de carga (perturbação)
        self.Jm = 0.05  # momento de inércia - desacelera a dinamica do sistema - cte de tempo tem que ser 10* maior que a amostragem
        self.B = 0.01  # atrito viscoso
        self.Wm = 0  # velocidade de rotação do motor (saída)
        self.Kb = 1  # constante elétrica

    def run(self):
        # equação dinâmica do motor
        while(1):
            self.Tm = ((self.Km)*(self.V)-(self.Km*self.Kb*self.Wm) -
                       (self.Ra*self.Tm))*(self.T/self.La)+self.Tm
            self.Wm = (self.Tm-self.TL-(self.B*self.Wm)) * \
                (self.T/self.Jm)+self.Wm
            print(self.Wm)
            sleep(0.1)


class control_thread (threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        # parâmetros de simulação
        self.T = 0.2  # período de amostragem
    # ainda não está pronto. falta o run
    # faz o controle de velocidade dos motores com T=200ms
    # tem lei de controle simples que mantenha os motores funcionando a metade da vmax por 1 min
    # velocidade dada por sinal de referência
    # apenas 12 motores de cada vez


######################################################
# Criando as threads
motor_thread = []
for i in range(30):
    motor_thread.append(motor())

motor_thread[0].start()

# Comecando novas Threads
# for i in range(29):
#   motor_thread[i].start()


# for t in motor_thread:
#    t.join()


#print ("Saindo da main")
