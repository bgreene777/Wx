import numpy as np
import urllib2
from datetime import datetime, timedelta

'''
Fetches 1-minute data from National Weather Center Mesonet tower.
Displays most recent observations as well as a time series of current day's
T, Td, wind speed, and wind direction.

Written by Brian Greene
University of Oklahoma
Last edit: 22 Jan 2018
'''

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

# Convert this timestep to datetime object
delta_latest = timedelta(minutes=time[inow])
dt_latest = datetime(yr, mo, da) + delta_latest

# Print current conditions
print 'Current conditions at NWC Mesonet:'
print 'Date: %s' % (datetime.strftime(dt_latest, '%A, %d %B %Y'))
print 'Time: %s' % (datetime.strftime(dt_latest, '%H:%M UTC'))
print 'Temperature: %3.1fC' % tair[inow]
print 'Relative Humidity: %.0f%%' % relh[inow]
print 'Wind Speed: %3.1f m s-1' % wspd[inow]
print 'Wind Direction: %.0f deg' % wdir[inow]



