import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndimage
import xarray as xr
import netCDF4
from argparse import ArgumentParser

# Input arguments
parser = ArgumentParser()
parser.add_argument('-i', required=True, action='store', dest='file',
	nargs=1, help='Input file path')
args = parser.parse_args()

# define projection and setup some graphing routines
crs = ccrs.Orthographic(central_longitude=0., central_latitude=90.)
def plot_background(ax):
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)

# load gfs data - northern hemisphere
df = netCDF4.Dataset(args.file[0], 'r')
lon = df.variables['lon_0'][:]
iN = np.where(df.variables['lat_0'][:] >= 0)[0]
lat = df.variables['lat_0'][iN]

i300 = np.where(df.variables['lv_ISBL0'][:] == 30000.)[0][0]

u300 = df.variables['UGRD_P0_L100_GLL0'][i300, iN, :]
v300 = df.variables['VGRD_P0_L100_GLL0'][i300, iN, :]
z300 = df.variables['HGT_P0_L100_GLL0'][i300, iN, :]
psfc = df.variables['PRES_P0_L1_GLL0'][iN, :] / 100.
Tsfc = df.variables['TMP_P0_L1_GLL0'][iN, :] - 273.15

# calculate speed from u and v
spd300 = np.sqrt(u300**2. + v300**2.)

# mesh grid
lon_2d, lat_2d = np.meshgrid(lon, lat)

# plot
fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(20,13), 
	subplot_kw={'projection': crs})
for a in ax1:
	plot_background(a)

# 300 mb heights and winds
cf1 = ax1[0].contourf(lon_2d, lat_2d, spd300, cmap='cool', 
	transform=ccrs.PlateCarree())
c1 = ax1[0].contour(lon_2d, lat_2d, z300, colors='black', linewidths=2, 
	transform=ccrs.PlateCarree())
ax1[0].clabel(c1, fontsize=10, inline=1, inline_spacing=1, fmt='%i', 
	rightside_up=True)
ax1[0].set_title('300 mb Wind Speeds and Heights')
cb1 = fig1.colorbar(cf1, ax=ax1[0], orientation='horizontal', shrink=0.74, pad=0)
cb1.set_label('knots', size='x-large')

# surface pressure and temperature
cf2 = ax1[1].contourf(lon_2d, lat_2d, Tsfc, cmap='YlOrRd',
	transform=ccrs.PlateCarree(), zorder=0)
c2 = ax1[1].contour(lon_2d, lat_2d, psfc, colors='black', linewidths=2,
	transform=ccrs.PlateCarree())
ax1[1].clabel(c2, fontsize=10, inline=1, inline_spacing=1, fmt='%i', 
	rightside_up=True)
ax1[1].set_title('Surface Temperature and Pressure')
cb2 = fig1.colorbar(cf2, ax=ax1[1], orientation='horizontal', shrink=0.74, pad=0)
cb2.set_label('deg C', size='x-large')

plt.show()

df.close()