import numpy as np
import urllib2
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mpdates
import metpy.calc as mcalc
from metpy.units import units
import csv

'''
Fetches 1-minute data from National Weather Center Mesonet tower.
Displays most recent observations as well as a time series of current day's
T, Td, wind speed, and wind direction.

Written by Brian Greene
University of Oklahoma
Last edit: 23 Jan 2018
'''
# Location to save output files
saveDir = '/Users/briangreene/Desktop/'

# Base URL
base_URL = 'http://www.mesonet.org/data/public/nwc/mts-1m/'

# Find today's date and time
dt_now = datetime.utcnow()
yr = dt_now.year
mo = dt_now.month
da = dt_now.day
hr = dt_now.hour
mi = dt_now.minute

# Construct url for mts file
mts_URL = '%s%d/%02d/%02d/%d%02d%02dnwcm.mts' % (base_URL, yr, mo, da, 
	yr, mo, da)

# Fetch data
f = urllib2.urlopen(mts_URL)
df = f.read()
df_line = df.split('\n')
df_line = df_line[3:-1]

# Load into arrays
time, relh, tair, wspd, wdir, wmax, rain, pres, srad, ta9m, ws2m, skin = (
	[] for i in range(12))

for i in range(1440):
	data_short = df_line[i].split()
	time.append(float(data_short[2]))
	relh.append(float(data_short[3]))
	tair.append(float(data_short[4]))
	wspd.append(float(data_short[5]))
	wdir.append(float(data_short[6]))
	wmax.append(float(data_short[7]))
	rain.append(float(data_short[8]))
	pres.append(float(data_short[9]))
	srad.append(float(data_short[10]))
	ta9m.append(float(data_short[11]))
	ws2m.append(float(data_short[12]))
	skin.append(float(data_short[13]))

# Find latest valid timestep
inow = next((i for i, x in enumerate(relh) if x<0), None) - 1

# Convert RH to Td
tair = np.array(tair)
relh = np.array(relh)
wspd = np.array(wspd)
td = np.array(mcalc.dewpoint_rh(tair[:inow+1] * units.degC, 
	relh[:inow+1] / 100.))
wspd_kts = wspd * 1.94
tair_F = tair * 1.8 + 32.
td_F = td * 1.8 + 32.

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
print 'Current conditions at NWC Mesonet:'
print 'Date: %s' % (datetime.strftime(dt_latest, '%A, %d %B %Y'))
print 'Time: %s' % (datetime.strftime(dt_latest, '%H:%M UTC'))
print 'Temperature: %3.1fC' % tair[inow]
print 'Dewpoint: %3.1fC' % td[inow]
print 'Wind Speed: %3.1f m s-1' % wspd[inow]
print 'Wind Direction: %.0f deg' % wdir[inow]

# Plot time series of T, Td, p, wspd, wdir
fig1, axarr = plt.subplots(4, sharex=True, figsize=(10,10))
figtitle = 'NWC Mesonet Meteogram for %s' % datetime.strftime(dt_now,
	'%d %B %Y')
plt.suptitle(figtitle, fontsize=20)

# T & Td
axarr[0].plot(t_all[:inow+1], tair_F[:inow+1], 'r')
#axarr[0].plot(t_all[:inow+1], wchl, 'b')
axarr[0].plot(t_all[:inow+1], td_F, 'g')
axarr[0].set_title('Temperature and Dewpoint')
axarr[0].tick_params(labeltop=False, right = True, labelright=True)
axarr[0].set_ylabel('Temperature ($^\circ$F)')
axarr[0].grid(axis='y')

# p
axarr[1].plot(t_all[:inow+1], pres[:inow+1], 'k')
axarr[1].set_title('Pressure')
axarr[1].tick_params(labeltop=False, right = True, labelright=True)
axarr[1].set_ylabel('Pressure (hPa)')
axarr[1].grid(axis='y')

# wind speed and direction
axarr_2 = axarr[2].twinx()
axarr[2].plot(t_all[:inow+1], wspd_kts[:inow+1], 'b')
axarr_2.plot(t_all[:inow+1], wdir[:inow+1], 'r*', markersize=1)
axarr[2].set_title('Wind Speed and Direction')
axarr[2].set_ylabel('Wind Speed (kts)', color='b')
axarr_2.set_ylabel('Wind Direction ($^\circ$)', color='r')
axarr[2].grid(axis='y')

# solar radiation
axarr[3].plot(t_all[:inow+1], srad[:inow+1], 'orange')
axarr[3].set_title('Solar Radiation')
axarr[3].set_ylabel('Solar Radiation (W m$^{-2}$)')
axarr[3].xaxis.set_major_locator(mpdates.MinuteLocator(interval=60))
axarr[3].xaxis.set_major_formatter(mpdates.DateFormatter('%H'))
axarr[3].set_xlabel('Time UTC')
axarr[3].grid(axis='y')

# Show Plot
plt.show(block=False)

# Save CSV
s = raw_input('>>Save csv? y/n ')
while s != 'y' and s != 'n':
    s = raw_input('>>Save csv? y/n ')
if s == 'y':
    saveFileName = '%s%s.%s.1min.csv' % (saveDir, datetime.strftime(dt_latest, 
    	'%Y%m%d'), 'NWCM')
    headers = ('time', 'relh', 'tair', 'wspd', 'wdir', 'wmax', 'rain', 'pres', 
    	'srad', 'ta9m', 'ws2m', 'skin')
    fw = open(saveFileName,'wb')
    writer = csv.writer(fw, delimiter=',')
    writer.writerow(headers)
    for i in range(1440):
        writer.writerow( (time[i], relh[i], tair[i], wspd[i], wdir[i], wmax[i], 
        	rain[i], pres[i], srad[i], ta9m[i], ws2m[i], skin[i]) )

    fw.close()
    print 'Finished saving %s' % saveFileName.split('/')[-1]

