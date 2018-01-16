import numpy as np
import urllib2

state = raw_input('>>Enter state: ').upper()
model = raw_input('>>Enter 1 for NAM, 2 for GFS MOS: ')
if model == '1':
	mos = 'NAM'
elif model == '2':
	mos = 'AVN'
else:
	print 'uhhh'

stid = raw_input('>>Enter airport station id: ').upper()

URL = 'http://www.nws.noaa.gov/mdl/forecast/text/state/%s.%s.htm' % (state, mos)
fd = urllib2.urlopen(URL)
data_long = fd.read()
data = data_long.split('\n')

istation = [i for i,item in enumerate(data) if stid in item][0]

for j in np.arange(istation-1, istation+23):
	print data[j]