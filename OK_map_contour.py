'''
Plot gridded data across state of Oklahoma using basemap

Author: Brian Greene (December 2019)

Copyright - University of Oklahoma Center for Autonomous Sensing and Sampling,
2019
'''
# Python Packages
import os
from datetime import datetime, timedelta

# Installed packages
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

# close all figures
plt.close("all")

# Oklahoma
llcrnrlat = 33.5
urcrnrlat = 37.2
llcrnrlon = -103.2
urcrnrlon = -94.0

# files
flist = glob("/Users/briangreene/Nextcloud/Projects/WindClimo/*.csv")

for f in flist:
    # Initialize map
    print("Initializing map")
    fig_map, ax_map = plt.subplots(1, figsize=(12, 6.75))
    m = Basemap(projection="merc", llcrnrlat=llcrnrlat, urcrnrlat=urcrnrlat,
                llcrnrlon=llcrnrlon, urcrnrlon=urcrnrlon, resolution="h", ax=ax_map)

    # Draw patches over not Oklahoma
    print("Reading shapefile")
    m.readshapefile("/Users/briangreene/Desktop/states_21basic/states",
                    "states", drawbounds=False)
    patch = []
    patch_ok = []
    for info, shape in zip(m.states_info, m.states):
        if info["STATE_NAME"] != "Oklahoma":
            patch.append(Polygon(np.array(shape), True))
        else:
            patch_ok.append(Polygon(np.array(shape), True))

    xy = patch_ok[0].get_xy()

    # print "Creating meshgrid for map"
    xnew = np.arange(llcrnrlon, urcrnrlon, 0.05)
    ynew = np.arange(llcrnrlat, urcrnrlat, 0.05)
    xx, yy = np.meshgrid(xnew, ynew)

    # Load CSV data
    fname = f.split("/")[-1]
    month = fname.split("_")[1]
    thresh = fname.split("_")[2]

    print(f"Reading file: {fname}")
    data = np.genfromtxt(f, dtype=str, skip_header=1, delimiter=",")
    site = data[:, 0]
    lats = data[:, 1].astype(float)
    lons = data[:, 2].astype(float)
    elev = data[:, 3].astype(float)
    frac = data[:, 4].astype(float)

    # transpose to basemap coordinates
    print("transposing to basemap coords")
    lon, lat, xplot, yplot = m.makegrid(len(xnew), len(ynew), returnxy=True)
    x1, y1 = m(lons, lats)

    # connect Oklahoma border points with nearest station to interpolate
    def nearest(Lon, Lat):
        # returns index of closest mesonet site
        dist = np.sqrt((Lon - np.array(x1))**2. + (Lat - np.array(y1))**2.)
        return np.argmin(dist)

    frac_perim, latperim, lonperim = ([] for i in range(3))
    for i in range(len(xy)):
        iclose = nearest(xy[i, 0], xy[i, 1])
        frac_perim.append(frac[iclose])
        latperim.append(xy[i, 1])
        lonperim.append(xy[i, 0])

    x2 = np.concatenate((x1, np.array(lonperim)))
    y2 = np.concatenate((y1, np.array(latperim)))
    frac2 = np.concatenate((frac, np.array(frac_perim)))

    points = np.array(list(zip(x2, y2)))

    # Interpolate 2d data
    frac_new = interpolate.griddata(
        points, frac2, (xplot, yplot), method="cubic")
    # Create mask
    mpath = Path(xy)
    xxyyplot = np.dstack((xplot, yplot))
    xxyyplot_flat = xxyyplot.reshape(-1, 2)
    mask_flat = np.invert(mpath.contains_points(xxyyplot_flat))
    mask = mask_flat.reshape(xplot.shape)

    frac_plot = ma.masked_where(mask, frac_new)

    cfax = m.pcolormesh(xplot, yplot, frac_plot,
                        cmap=cmocean.cm.amp, vmin=50., vmax=100.)
    cfax.set_edgecolor("face")
    cbar = m.colorbar(cfax)

    for i in np.arange(len(frac)):
        plotstring = f"{frac[i]:3.1f}"
        txt = plt.text(x1[i], y1[i], plotstring, fontweight="bold",
                       ha="center", va="center")
        txt.set_path_effects(
            [PathEffects.withStroke(linewidth=3, foreground="w")])

    # m.drawcounties()
    m.drawstates()

    ax_map.set_title(
        f"Percent of time reaching 600 hPa for Month: {month} and Threshold: {thresh} m/s")
    cbar.ax.set_ylabel("Percent")

    fig_map.tight_layout()
    fig_map.savefig(
        f"/Users/briangreene/Desktop/OK_Wind_Climo/{fname}.pdf", 
        dpi=150, format="pdf")
    plt.close(fig_map)
