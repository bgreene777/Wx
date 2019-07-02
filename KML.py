import numpy as np
import netCDF4
import simplekml
import os
from argparse import ArgumentParser

# load data
parser = ArgumentParser()
parser.add_argument('-i', required=True, action='store', dest='files',
    nargs='*', help='Input file names')
args = parser.parse_args()

# directories
home = os.path.expanduser('~')
figpath = f'{home}/Desktop/KML_LAPSERATE/'
if not os.path.exists(figpath):
    os.mkdir(figpath)

for i, f in enumerate(np.asarray(args.files)):
    print(f'Reading file: {f.split("/")[-1]}')
    df = netCDF4.Dataset(f, 'r')

    lat = df.variables['lat'][:].data
    lon = df.variables['lon'][:].data
    alt = df.variables['alt_AGL'][:].data

    coords = list(zip(lon, lat, alt))
    throwaway = [coords.pop() for i in range(2)]

    # start kml
    kml = simplekml.Kml()
    ls = kml.newlinestring(name='CopterSonde')
    ls.coords = coords
    ls.extrude = 0
    ls.altitudemode = simplekml.AltitudeMode.relativetoground
    ls.style.linestyle.width = 2
    ls.style.linestyle.color = simplekml.Color.blue
    kml.save(f'{figpath}CS_flight_{i}.kml')