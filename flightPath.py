import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os
from geopy.distance import vincenty as vin

proj = 'ISOBAR'

fname = os.sep + os.path.join('Users', 'briangreene', 'Nextcloud', 'thermo', 
	'data', proj, 'Coptersonde21', '20180210', 
	'Coptersonde21_Data_2018-02-10_18h57m24s.csv')

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

# dx = geopy.distance.vincenty((xmin, ymin), (xmax, ymin)).m
# dy = geopy.distance.vincenty((xmin, ymin), (xmin, ymax)).m

# print dx
# print dy

# x_m = np.zeros(len(t))
# y_m = x_m

# for i in range(len(t)):
# 	x_m[i] = vin((lon[0], lat[0]), (lon[i], lat[0])).m
# 	y_m[i] = vin((lon[0], lat[0]), (lon[0], lat[i])).m

# xmin = min(x_m)
# xmax = max(x_m)
# ymin = min(y_m)
# ymax = max(y_m)

fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
	xlim=(xmin, xmax), ylim=(ymin, ymax), zlim=(0, 2000), projection='3d')

# fig2 = plt.figure()
# ax2 = fig2.add_subplot(111, aspect='equal', autoscale_on=False,
# 	xlim=(xmin, xmax), ylim=(ymin, ymax))

line, = ax.plot([], [], '-', lw=2)
# line2, = ax2.plot([], [], '-', lw=2)

def init():
	line.set_data([], [])
	line.set_3d_properties([])
	return line,

# def init2():
# 	line2.set_data([], [])
# 	return line2,

def animate(i):
	line.set_data(lon[:i], lat[:i])
	line.set_3d_properties(alt[:i])
	return line,

# def animate2(i):
# 	line2.set_data(x_m[:i], y_m[:i])
# 	return line2,

ani = animation.FuncAnimation(fig, animate, frames=len(t),
                              interval=1, blit=False, init_func=init)

# ani2 = animation.FuncAnimation(fig2, animate2, frames=len(t),
#                               interval=1, blit=False, init_func=init2)

plt.show()