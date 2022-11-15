import random
import threading
from time import sleep
import numpy as np
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.animation import FuncAnimation
######################################################

class Motor (threading.Thread):
    def __init__(self):
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
        self.Wmax = (self.Vmax-self.Ia*self.Ra)/self.Kb #maximum speed of the motor
        self.setPoint = []
        self.y = []
        self.x = []
        self.iterations = 3000

    def run(self):
        index = count()
        # motor's difference equations
        #for i in range(self.iterations):
        while(1):
            self.Tm = ((self.Km)*(self.V)-(self.Km*self.Kb*self.Wm) -
                       (self.Ra*self.Tm))*(self.T/self.La)+self.Tm
            self.Wm = (self.Tm-self.TL-(self.B*self.Wm)) * \
                (self.T/self.Jm)+self.Wm
            # adds the speed values to an array that is used to plot the graph
            self.y.append(self.Wm)
            self.x.append(next(index)*(self.T)) #appends the sampling equivalent time to the x axis
            self.setPoint.append(self.Wmax/2) #the setpoint vector needs to be the same size of the y vector so they can be plotted together
            #print(self.Wm)
            #print(self.V)
            sleep(self.T)


class ControlThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # simulation parameters
        self.T = 0.2  # sampling time
        self.setPoint = motor_thread[0].Wmax/2
        self.controlSignal = 0
        self.Kp = 1
        self.error = 0
    def run(self):
        self.error = self.setPoint - motor_thread[0].Wm
        self.controlSignal = self.error*self.Kp
        motor_thread[0].V = self.controlSignal
        print(motor_thread[0].V)
    # not finished yet. Still need to implement "run"
    # does the motors' speed control with T=200ms
    # has a simple control law that keeps the motors working with half of the maximum speed for one minute
    # speed it determined by reference signal
    # it can run only 12 motors at a time

######################################################
# Creating the threads
motor_thread = []
for i in range(30):
    motor_thread.append(Motor())

motor_thread[0].start()
#motor_thread[0].join()

softPLC = ControlThread()
softPLC.start()
# Starting new threads
# for i in range(29):
#   motor_thread[i].start()

# for t in motor_thread:
#    t.join()

##############
#plotting
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

ani = FuncAnimation(plt.gcf(), animate, interval = 1)

plt.tight_layout()
plt.show()

###############################


# creating the x axis
# creates an array from 0 to the number of iterations spaced by intervals of 1
'''x = np.arange(0, motor_thread[0].iterations, 1)

# Plotting
fig = plt.figure()
plt.ion()
ax = fig.subplots()
ax.plot(x, motor_thread[0].y, color='b')
ax.grid()
# Defining the cursor
cursor = Cursor(ax, horizOn=True, vertOn=True, useblit=True,
                color='r', linewidth=1)
# Creating an annotating box
annot = ax.annotate("", xy=(0, 0), xytext=(-40, 40), textcoords="offset points",
                    bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                    arrowprops=dict(arrowstyle='-|>'))
annot.set_visible(False)

# Function for storing and showing the clicked values
coord = []


def onclick(event):
    global coord
    coord.append((event.xdata, event.ydata))
    x = event.xdata
    y = event.ydata

    # printing the values of the selected point
    print([x, y])
    annot.xy = (x, y)
    text = "({:.3g}, {:.3g})".format(x, y)
    annot.set_text(text)
    annot.set_visible(True)
    fig.canvas.draw()  # redraw the figure


fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
# Unzipping the coord list in two different arrays
if (coord): #only prints if there are values in "coord"
    x1, y1 = zip(*coord)
    print(x1, y1)'''