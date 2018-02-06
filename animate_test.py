import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation

'''
Animated ball trajectory
'''

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 10), ylim=(0, 100))
line, = ax.plot([], [], '-o', lw=2)

# initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return line,

# animation function.  This is called sequentially
def animate(i):
    t = np.arange(0, i)
    y = 30 * t - 0.5 * 9.8 * t**2
    line.set_data(t, y)
    return line,

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=20, blit=True)

plt.show()