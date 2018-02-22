import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D
import os
from datetime import datetime
from geopy.distance import vincenty as vin

proj = 'ISOBAR'

fname = os.sep + os.path.join('Users', 'briangreene', 'Nextcloud', 'thermo', 
	'data', proj, 'Coptersonde22', '20180218', 
	'Coptersonde22_Data_2018-02-18_23h25m49s.csv')

cols = range(1, 25)
cols = tuple(cols)

data = np.loadtxt(fname, skiprows=1, usecols=cols, delimiter=',')
t = data[:, 0]
lat = data[:, 1]
lon = data[:, 2]
alt = data[:, 3]
T1 = data[:, 21]
T2 = data[:, 22]
T3 = data[:, 23]
j = range(0, len(t))

# fname = '/Users/briangreene/Desktop/TuffFlight1.csv'
# data = np.loadtxt(fname, skiprows=1, delimiter=',')
# t = data[:, 0]
# lat = data[:, 1]
# lon = data[:, 2]
# alt = data[:, 3]
# roll = data[:, 4]
# j = range(0, len(t))

dt = [datetime.utcfromtimestamp(i) for i in t]

xmin = min(lon)
xmax = max(lon)
ymin = min(lat)
ymax = max(lat)
zmax = max(alt)

dx = vin((xmin, ymin), (xmax, ymin)).m
dy = vin((xmin, ymin), (xmin, ymax)).m

# x_m = ((lon - xmin) / xmax) * dx
# y_m = ((lat - ymin) / ymax) * dy

# xmin_m = 0.
# xmax_m = dx
# ymin_m = 0.
# ymax_m = dy

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(121, aspect='equal', autoscale_on=False,
	xlim=(xmin, xmax), ylim=(ymin, ymax), 
	zlim=(0, zmax), projection='3d')
#ax.view_init(45, -76)
ax.view_init(10, -50)
ax.set_xticks(np.linspace(xmin, xmax, num=1))
ax.set_yticks(np.linspace(ymin, ymax, num=1))
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

ax2 = fig.add_subplot(122, xlim=(min(T1)-1, max(T1)+1), ylim=(0, zmax))
ax2.set_title('Temperature vs. Height')
ax2.set_ylabel('Altitude AGL (m)')
ax2.set_xlabel('Temperature (K)')
ax2.grid('on')


line, = ax.plot([], [], '-', lw=2)
#roll_text = ax.text(0.02, 0.95, 0.95, '', transform=ax.transAxes)
#time_text = ax.text(0.50, 0.5, 0.50, '', transform=ax.transAxes)
line2, = ax2.plot([], [], '-', lw=2)
line3, = ax2.plot([], [], '-', lw=2)
line4, = ax2.plot([], [], '-', lw=2)

def init():
	line.set_data([], [])
	line.set_3d_properties([])
	line2.set_data([], [])
	line3.set_data([], [])
	line4.set_data([], [])
	#roll_text.set_text('')
	#time_text.set_text('')
	return line, line2, line3, line4

def animate(i):
	line.set_data(lon[:i], lat[:i])
	line.set_3d_properties(alt[:i])
	line2.set_data(T1[:i], alt[:i])
	line3.set_data(T2[:i], alt[:i])
	line4.set_data(T3[:i], alt[:i])
	#roll_text.set_text('roll = %.1f deg' % roll[i])
	#time_text.set_text('time = %s' % dt[i].strftime('%H:%M:%S'))
	#line.set_marker(marker=(3, 0, roll[i]))
	return line, line2, line3, line4

# Writer = animation.writers['ffmpeg']
# writer = Writer(fps=30, bitrate=1800)

ani = animation.FuncAnimation(fig, animate, frames=len(t),
                              interval=1, blit=False, init_func=init, 
                              repeat=False)

# ani.save('/Users/briangreene/Desktop/Coptersonde22_20180218_last.mp4', 
# 	fps=40, writer='ffmpeg', extra_args=['-vcodec', 'libx264'])

plt.show()