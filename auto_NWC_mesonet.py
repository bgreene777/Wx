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
file = './NWCmesonet.py'

# Save file and figure directory
sdir = '/Users/briangreene/Desktop/NWCmesonet/'

# Command line argument
s = f'python {file} -n False -d {str_yesterday} -f True -s True -save {sdir} -si True'

# Execute command
os.system(s)