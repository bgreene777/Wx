'''
Automatically fetch grb2 files from nomads ncdc/ncei ftp server and save to
directory of choosing. Optionally will convert files to netCDF4 and remove
grib files.

Note: requires python 3 environment with pynio - pyn_env

Author: Brian R. Greene, University of Oklahoma
Updated: 11 September 2019
'''
import os
import xarray as xr
from datetime import datetime, timedelta
from argparse import ArgumentParser
from glob import glob

# command line arguments
parser = ArgumentParser()
parser.add_argument('-ds', required=True, action='store', dest='d_s',
    nargs=1, type=str, help='Start date YYYYMMDD')
parser.add_argument('-de', required=True, action='store', dest='d_e',
    nargs=1, type=str, help='End date YYYYMMDD')
parser.add_argument('-s', required=True, action='store', dest='s',
    nargs=1, type=str, help='Save folder name')
parser.add_argument('--netCDF', action='store_true', dest='convert', 
    help='Convert to netCDF4?')
parser.add_argument('--clean', action='store_true', dest='clean',
    help='Remove grib files?')
args = parser.parse_args()

# base url for ftp server
url_base = 'ftp://nomads.ncdc.noaa.gov/GFS/analysis_only/'
# save directory
save_path = os.path.join(f'{os.path.expanduser("~")}', 'Documents', 'Data',
    'GFS', args.s[0])
# create directory if it does not already exist
if not os.path.exists(save_path):
    os.mkdir(save_path)

# convert to datetime objects for easier handling
dt_s = datetime.strptime(args.d_s[0], '%Y%m%d')
dt_e = datetime.strptime(args.d_e[0], '%Y%m%d')

# create array of datetime objects between start and end dates
dt_range = []
i_dt = dt_s
while i_dt <= dt_e:
    dt_range.append(i_dt)
    i_dt += timedelta(days=1)

# download files
# for dt in dt_range:
#     url = f'{url_base}{dt.strftime("%Y%m")}/{dt.strftime("%Y%m%d")}/gfsanl_3_*000.grb2'
#     os.system(f'cd {save_path}; wget {url}')

print('Finished saving grib files.')

# convert to netCDF if selected
if args.convert:
    grib = glob(os.path.join(save_path, '*.grb2'))
    for f in grib:
        f_new = ''.join(f.split('.')[:-1]) + '.nc'
        ds = xr.open_dataset(f, engine='pynio')
        print(f'Saving {f_new.split(os.sep)[-1]}')
        ds.to_netcdf(f_new)
        ds.close()

    print('Finished saving netCDF files.')

# remove grib files if selected
if args.clean:
    os.system(f'cd {save_path}; rm *.grb2')
    print('Finished removing grib files.')

print('get_gfs.py complete.')





