import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import cmocean
import os
from datetime import datetime
from argparse import ArgumentParser

# Input arguments
parser = ArgumentParser()
parser.add_argument('-i', required=True, action='store', dest='files',
                    nargs='*', help='Input file paths')
parser.add_argument('-s', required=True, action='store', dest='save',
                    nargs=1, help='Figure save directory')
args = parser.parse_args()

dates = [datetime.strptime(''.join(d.split('_')[2:4]),
                           '%Y%m%d%H%M') for d in args.files]
idx = np.argsort(dates)

figpath = args.save[0]
if not os.path.exists(figpath):
    os.mkdir(figpath)

# define projection and setup some graphing routines
crs = ccrs.Orthographic(central_longitude=0., central_latitude=90.)
def plot_background(ax):
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
plt.close('all')

# loop through selected files
for f in np.asarray(args.files)[idx]:
    # grab valid time from file name
    fname = f.split(os.sep)[-1]
    d_valid = ''.join(fname.split('_')[2:4])
    dt_valid = datetime.strptime(d_valid, '%Y%m%d%H%M')

    # load gfs data - northern hemisphere
    print(f'Reading file {fname}')
    df = netCDF4.Dataset(f, 'r')
    lon = df.variables['lon_0'][:]
    iN = np.where(df.variables['lat_0'][:] >= 0)[0]
    lat = df.variables['lat_0'][iN]

    i300 = np.where(df.variables['lv_ISBL0'][:] == 30000.)[0][0]

    u300 = df.variables['UGRD_P0_L100_GLL0'][i300, iN, :]
    v300 = df.variables['VGRD_P0_L100_GLL0'][i300, iN, :]
    z300 = df.variables['HGT_P0_L100_GLL0'][i300, iN, :]
    psfc = df.variables['PRMSL_P0_L101_GLL0'][iN, :] / 100.
    # PRES_P0_L1_GLL0
    # PRMSL_P0_L101_GLL0
    # MSLET_P0_L101_GLL0
    Tsfc = df.variables['TMP_P0_L1_GLL0'][iN, :] - 273.15

    # calculate speed from u and v
    spd300 = np.sqrt(u300**2. + v300**2.)

    # mesh grid
    lon_2d, lat_2d = np.meshgrid(lon, lat)

    # plot
    fig1, ax1 = plt.subplots(nrows=1, ncols=2, figsize=(20, 13),
                             subplot_kw={'projection': crs})
    for a in ax1:
        plot_background(a)

    # 300 mb heights and winds
    vmin1 = 0.
    vmax1 = 120.
    lvl1 = np.linspace(vmin1, vmax1, num=9)
    cf1 = ax1[0].contourf(lon_2d, lat_2d, spd300, cmap=cmocean.cm.dense, 
                          vmin=0., vmax = 120., levels=lvl1,
                          transform=ccrs.PlateCarree())
    c1 = ax1[0].contour(lon_2d, lat_2d, z300, colors='black', linewidths=2,
                        transform=ccrs.PlateCarree())
    ax1[0].clabel(c1, fontsize=10, inline=1, inline_spacing=1, fmt='%i',
                  rightside_up=True)
    ax1[0].set_title('300 mb Wind Speeds and Heights')
    cb1 = fig1.colorbar(
        cf1, ax=ax1[0], orientation='horizontal', shrink=0.74, pad=0)
    cb1.set_label('knots', size='x-large')

    # surface pressure and temperature
    vmin2 = -60.
    vmax2 = 30.
    lvl2 = np.linspace(vmin2, vmax2, num=10)
    cf2 = ax1[1].contourf(lon_2d, lat_2d, Tsfc, cmap=cmocean.cm.thermal,
                          vmin=-60., vmax=30., levels=lvl2,
                          transform=ccrs.PlateCarree(), zorder=0)
    c2 = ax1[1].contour(lon_2d, lat_2d, psfc, colors='black', linewidths=2,
                        transform=ccrs.PlateCarree())
    ax1[1].clabel(c2, fontsize=10, inline=1, inline_spacing=1, fmt='%i',
                  rightside_up=True)
    ax1[1].set_title('Surface Temperature and Pressure')
    cb2 = fig1.colorbar(
        cf2, ax=ax1[1], orientation='horizontal', shrink=0.74, pad=0)
    cb2.set_label('deg C', size='x-large')

    plt.suptitle(f'GFS Analysis Valid {dt_valid.strftime("%d-%B-%Y %H UTC")}')

    fig1.savefig(f'{figpath}v1_{dt_valid.strftime("%Y%m%d_%H%M")}_GFS.png',
                 format='png', dpi=150)

    df.close()
    plt.close(fig1)
