import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os
from geopy.distance import vincenty as vin

proj = 'ISOBAR'

fname = os.sep + os.path.join('Users', 'briangreene', 'Nextcloud', 'thermo', 
	'data', proj, 'Coptersonde22', '20180217', 
	'Coptersonde22_Data_2018-02-17_17h45m56s.csv')

cols = range(1, 25)
cols = tuple(cols)

data = np.loadtxt(fname, skiprows=1, usecols=cols, delimiter=',')
t = data[:, 0]
lat = data[:, 1]
lon = data[:, 2]
alt = data[:, 3]
j = range(0, len(t))

xmin = min(lon)
xmax = max(lon)
ymin = min(lat)
ymax = max(lat)
zmax = max(alt)

dx = vin((xmin, ymin), (xmax, ymin)).m
dy = vin((xmin, ymin), (xmin, ymax)).m

x_m = ((lon - xmin) / xmax) * dx
y_m = ((lat - ymin) / ymax) * dy

xmin_m = 0.
xmax_m = dx
ymin_m = 0.
ymax_m = dy

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
	xlim=(xmin_m, xmax_m), ylim=(ymin_m, ymax_m), 
	zlim=(0, zmax), projection='3d')


line, = ax.plot([], [], '-', lw=2)

def init():
	line.set_data([], [])
	line.set_3d_properties([])
	return line,

def animate(i):
	line.set_data(x_m[:i], y_m[:i])
	line.set_3d_properties(alt[:i])
	return line,

ani = animation.FuncAnimation(fig, animate, frames=len(t),
                              interval=1, blit=False, init_func=init)

plt.show()