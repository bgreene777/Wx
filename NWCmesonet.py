#!/Users/briangreene/anaconda3/bin/python
'''
Fetches 1-minute data from National Weather Center Mesonet tower.
Displays most recent observations as well as a time series of current day's
T, Td, wind speed, and wind direction.

Written by Brian Greene
University of Oklahoma
Last edit: 25 October 2019
Updated for use with Python 3, includes command line arguments
'''

import numpy as np
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mpdates
import metpy.calc as mcalc
from metpy.units import units
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', '--now', action='store_true', dest='now',
    help='Use current observations? Default is false')
parser.add_argument('-d', '--date', required=False, action='store', dest='date', nargs=1,
    help='Input date as yyyymmdd, or leave blank for latest observations')
parser.add_argument('-f', '--figure', action='store_true', dest='fig',
    help='Save figure? Default is false')
parser.add_argument('-s', '--savedir', required=True, action='store', dest='savedir',
    nargs=1, help='Enter the save directory for file and figure')
parser.add_argument('-si', action='store_true', dest='SI',
    help='Use SI units? Default is false')
args = parser.parse_args()

# Logo
logo_path = '/Users/briangreene/Desktop/mesonet_logo.png'
logo = plt.imread(logo_path)

# Location to save output files and figures
if args.fig:
    saveFig = True
else:
    saveFig = False

saveDir = args.savedir[0]

# Base URL
base_URL = 'http://www.mesonet.org/data/public/nwc/mts-1m/'

# Find today's date and time
if args.now:
    now = True
    dt_now = datetime.utcnow()
else:
    now = False
    d = args.date[0]
    dt_now = datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]))

yr = dt_now.year
mo = dt_now.month
da = dt_now.day
hr = dt_now.hour
mi = dt_now.minute

# Construct url for mts file
mts_URL = f'{base_URL}{yr}/{mo:02d}/{da:02d}/{yr:02d}{mo:02d}{da:02d}nwcm.mts'

# Fetch and save data
saveFileName = f'{saveDir}{datetime.strftime(dt_now, "%Y%m%d")}.NWCM.1min.csv'
r = requests.get(mts_URL)
with open(saveFileName, 'wb') as f:
    f.write(r.content)

# Load new data file
df = np.genfromtxt(saveFileName, skip_header=3, autostrip='True', dtype=str)

time = df[:, 2].astype(float)
relh = df[:, 3].astype(float)
tair = df[:, 4].astype(float)
wspd = df[:, 5].astype(float)
wdir = df[:, 6].astype(float)
wmax = df[:, 7].astype(float)
rain = df[:, 8].astype(float)
pres = df[:, 9].astype(float)
srad = df[:, 10].astype(float)
ta9m = df[:, 11].astype(float)
ws2m = df[:, 12].astype(float)
skin = df[:, 13].astype(float)

# Find latest valid timestep
if now:
    inow = next((i for i, x in enumerate(relh) if x<0), None) - 1
else:
    inow = -2

# remove bad data
relh[relh < -100.] = np.nan
tair[tair < -100.] = np.nan
wspd[wspd < -100.] = np.nan
wdir[wdir < -100.] = np.nan
wmax[wmax < -100.] = np.nan
rain[rain < -100.] = np.nan
pres[pres < -100.] = np.nan
srad[srad < -100.] = np.nan
ta9m[ta9m < -100.] = np.nan
ws2m[ws2m < -100.] = np.nan
skin[skin < -100.] = np.nan

# Convert RH to Td - already read in as degC and m/s
tair = tair * units.degC
wspd = wspd * units.m / units.s
td = mcalc.dewpoint_rh(tair[:inow+1], relh[:inow+1] / 100.)

if args.SI:
    # already in SI, just grab magnitudes
    print('--Using SI Units--')
    tair = tair.magnitude
    td = td.magnitude
    wspd = wspd.magnitude
    tlab = '$^\circ$C'
    wslab = 'm s$^{-1}$'
    tlab2 = 'degC'
    wslab2 = 'm/s'

else:
    print('--Converting to Imperial Units--')
    tair = tair.to(units.degF).magnitude
    td = np.array([tx.to(units.degF).magnitude for tx in td])
    wspd = np.array([wx.to(units.kts).magnitude for wx in wspd])
    tlab = '$^\circ$F'
    wslab = 'kts'
    tlab2 = 'degF'
    wslab2 = 'kts'

# Calculate Wind Chill
#wchl = mcalc.windchill(tair_F[:inow+1]*units.degF, wspd_kts[:inow+1]*units.kts)

# Convert latest timestep to datetime object
delta_latest = timedelta(minutes=time[inow])
dt_base = datetime(yr, mo, da)
dt_latest = dt_base + delta_latest

# Create matplotlib dates
dt_all = [None] * len(time)
dt_all[0] = dt_base
delta_min = timedelta(minutes=1)
for i in np.arange(1, len(time)):
	dt_all[i] = dt_all[i-1] + delta_min

t_all = mpdates.date2num(dt_all)

# Print current conditions
print('Current conditions at NWC Mesonet:')
print(f'Date: {datetime.strftime(dt_latest, "%A, %d %B %Y")}')
print(f'Time: {datetime.strftime(dt_latest, "%H:%M UTC")}')
print(f'Temperature: {tair[inow]:.1f} {tlab2}')
print(f'Dewpoint: {td[inow]:.1f} {tlab2}')
print(f'Wind Speed: {wspd[inow]:.1f} {wslab2}')
print(f'Wind Direction: {wdir[inow]:.0f} deg')

# Plot time series of T, Td, p, wspd, wdir
fig1, axarr = plt.subplots(4, sharex=True, figsize=(10,10))
figtitle = f'NWC Mesonet Meteogram for {datetime.strftime(dt_now, "%d %B %Y")}'
plt.suptitle(figtitle, fontsize=20)

# T & Td
axarr[0].plot(t_all[:inow+1], tair[:inow+1], color=(213./255, 94./255, 0))
#axarr[0].plot(t_all[:inow+1], wchl, 'b')
axarr[0].plot(t_all[:inow+1], td, color=(0, 158./255, 115./255))
axarr[0].set_title('Temperature and Dewpoint')
axarr[0].tick_params(labeltop=False, right = True, labelright=True)
axarr[0].set_ylabel(f'Temperature [{tlab}]')
axarr[0].grid(axis='y')

# p
axarr[1].plot(t_all[:inow+1], pres[:inow+1], 'k')
axarr[1].set_title('Pressure')
axarr[1].tick_params(labeltop=False, right = True, labelright=True)
axarr[1].set_ylabel('Pressure [hPa]')
axarr[1].grid(axis='y')

# wind speed and direction
axarr_2 = axarr[2].twinx()
axarr[2].plot(t_all[:inow+1], wspd[:inow+1], color=(0, 114./255, 178./255))
axarr_2.plot(t_all[:inow+1], wdir[:inow+1], color=(213./255, 94./255, 0), 
    marker='o', markersize=1, linestyle='')
axarr[2].set_title('Wind Speed and Direction')
axarr[2].set_ylabel(f'Wind Speed [{wslab}]', color=(0, 114./255, 178./255))
axarr_2.set_ylabel('Wind Direction', color=(213./255, 94./255, 0))
axarr_2.set_yticks(range(0, 405, 45))
axarr_2.set_yticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
axarr[2].grid(axis='y')

# solar radiation
axarr[3].plot(t_all[:inow+1], srad[:inow+1], color=(230./255, 159./255, 0))
axarr[3].set_title('Solar Radiation')
axarr[3].set_ylabel('Solar Radiation [W m$^{-2}$]')
axarr[3].xaxis.set_major_locator(mpdates.MinuteLocator(interval=60))
axarr[3].xaxis.set_major_formatter(mpdates.DateFormatter('%H'))
axarr[3].set_xlabel('Time UTC')
axarr[3].grid(axis='y')

# add logo
fig1.figimage(logo, 50, 0, zorder=100)

# Save plot if saveFig = True, else just show
if saveFig:
    fig_name = f'{saveDir}NWC_Meteogram_{dt_base.strftime("%Y%m%d")}.pdf'
    fig1.savefig(fig_name, format='pdf', dpi=150)
    print(f'Finished saving {fig_name}')
else:
    plt.show()

plt.close('all')