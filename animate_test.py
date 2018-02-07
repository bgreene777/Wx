import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from time import time

class RaceCar:
	def __init__(self, v=1., origin=(0, 0), theta=0., r=2.):
		self.speed_init = v
		self.origin = origin
		self.theta_init = theta
		self.time_elapsed = 0.
		self.radius = r

		self.theta = self.theta_init * np.pi / 180.

	def position(self):
		x = self.radius * np.cos(self.theta)
		y = self.radius * np.sin(self.theta)

		return (x, y)

	def step(self, dt):
		omega = self.speed_init / self.radius
		self.theta += omega * dt
		self.time_elapsed += dt


car = RaceCar()
dt = 1./30

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=(-3, 3), ylim=(-3, 3))

line, = ax.plot([], [], 'o-', lw=2)

def init():
    """initialize animation"""
    line.set_data([], [])
    return line,

def animate(i):
    """perform animation step"""
    global car, dt
    car.step(dt)
    
    line.set_data(*car.position())
    return line, 

# choose the interval based on dt and the time to animate one step
t0 = time()
animate(0)
t1 = time()
interval = 1000 * dt - (t1 - t0)

ani = animation.FuncAnimation(fig, animate, frames=300,
                              interval=interval, blit=False, init_func=init)

plt.show()

