#!/Users/briangreene/anaconda3/bin/python
'''
Script to automate running NWCmesonet.py each day to create a figure and file
for the previous day

Author: Brian R. Greene
Created: 11 June 2019
'''
import os
from datetime import datetime, timedelta

# Get today's date
dt_now = datetime.utcnow()
dt_yesterday = dt_now - timedelta(days=1)

str_yesterday = datetime.strftime(dt_yesterday, '%Y%m%d')

# Directory of NWCmesonet.py
file = '/Users/briangreene/Documents/Projects/Wx/NWCmesonet.py'

# Save file and figure directory
sdir = '/Users/briangreene/Desktop/NWCmesonet/'

# Anaconda 3 python path
py = '/Users/briangreene/anaconda3/bin/python'

# Command line argument
s = f'{py} {file} -n False -d {str_yesterday} -f True -s True -save {sdir} -si True'

# Execute command
os.system(s)