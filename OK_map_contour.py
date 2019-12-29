'''
Plot gridded data across state of Oklahoma using basemap

Author: Brian Greene (December 2019)

Copyright - University of Oklahoma Center for Autonomous Sensing and Sampling,
2019
'''
# Python Packages
import os
from datetime import datetime, timedelta
import warnings

# Installed packages
import matplotlib
matplotlib.use('TkAgg')
import netCDF4
import numpy as np
import numpy.ma as ma
import cmocean
import matplotlib.patheffects as PathEffects

from mpl_toolkits.basemap import Basemap
from matplotlib import dates as mpdates
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from scipy import interpolate
from glob import glob

# Oklahoma
llcrnrlat = 33.5
urcrnrlat = 37.2
llcrnrlon = -103.2
urcrnrlon = -94.0

# Initialize map
# print 'Initializing map'
fig_map, ax_map = plt.subplots(1, figsize=(12, 6.75))
m = Basemap(projection='merc', llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat, 
    llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, resolution='l', ax=ax_map)

# Draw patches over not Oklahoma
# print 'Reading shapefile'
m.readshapefile('/Users/briangreene/Desktop/states_21basic/states',
 'states', drawbounds=False)
patch = []
patch_ok = []
for info, shape in zip(m.states_info, m.states):
	if info['STATE_NAME'] != 'Oklahoma':
		patch.append( Polygon(np.array(shape), True) )
	else:
		patch_ok.append( Polygon(np.array(shape), True))

xy = patch_ok[0].get_xy()

# print 'Creating meshgrid for map'
xnew = np.arange(llcrnrlon, urcrnrlon, 0.1)
ynew = np.arange(llcrnrlat, urcrnrlat, 0.1)
xx, yy = np.meshgrid(xnew, ynew)

# Load CSV data
f = "/Users/briangreene/Nextcloud/Projects/WindClimo/2018_All_20.0_frac.csv"
# print "Reading file: {}".format(f.split('/')[-1])
data = np.genfromtxt(f, dtype=str, skip_header=1, delimiter=",")
site = data[:, 0]
lats = data[:, 1].astype(float)
lons = data[:, 2].astype(float)
elev = data[:, 3].astype(float)
frac = data[:, 4].astype(float)

# transpose to basemap coordinates
# print 'transposing to basemap coords'
lon, lat, xplot, yplot = m.makegrid(len(xnew), len(ynew), returnxy=True)
x1, y1 = m(lons, lats)

points = np.array(list(zip(x1, y1)))

# Interpolate 2d data
frac_new = interpolate.griddata(points, frac, (xplot, yplot), method='cubic')
# Create mask
mpath = Path(xy)
xxyyplot = np.dstack((xplot, yplot))
xxyyplot_flat = xxyyplot.reshape(-1, 2)
mask_flat = np.invert(mpath.contains_points(xxyyplot_flat))
mask = mask_flat.reshape(xplot.shape)

frac_plot = ma.masked_where(mask, frac_new)

cfax = m.pcolormesh(xplot, yplot, frac_plot, cmap=cmocean.cm.haline, vmin=75., vmax=100.)
cbar = m.colorbar(cfax)

for i in np.arange(len(frac)):
	plotstring = "{0:3.1f}".format(frac[i])
	txt= plt.text(x1[i], y1[i], plotstring, fontweight='bold', 
		ha='center', va='center')
	txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='w')])

# m.drawcounties()
m.drawstates()

ax_map.set_title("Percent of time reaching 600 hPa for all of 2018 with 20 m/s threshold")
cbar.ax.set_ylabel('Percent')

plt.show()