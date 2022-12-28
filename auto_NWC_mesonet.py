#!/Users/briangreene/anaconda3/bin/python
"""
Script to automate running NWCmesonet.py each day to create a figure and file
for the previous day

Author: Brian R. Greene
Created: 11 June 2019
Modified: 28 December 2022 - adapt for updates to NWCmesonet.py
"""
import os
import yaml
from datetime import datetime, timedelta
from NWCmesonet import plot_NWC

# load yaml file
with open("NWCmesonet.yaml") as f:
    config = yaml.safe_load(f)

# Get today's date
dt_now = datetime.utcnow()
dt_yesterday = dt_now - timedelta(days=1)

# Save file and figure directory
sdir = f"{config['sdir_local']}{dt_yesterday.year:04d}/"

# Run NWCmesonet()
plot_NWC(dt_yesterday, sdir)

# rsync to upload figures
# build strings for save paths from yaml file
alias = config["alias"]
sdir_remote = config["sdir_remote"]
sdir_r_full = f"{alias}:{sdir_remote}{dt_yesterday.year:04d}/"
rs = f"rsync -avh --ignore-existing -e ssh {sdir}* {sdir_r_full}"
# execute
os.system(rs)