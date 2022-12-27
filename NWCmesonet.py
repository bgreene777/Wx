#!/Users/briangreene/anaconda3/bin/python
# --------------------------------
# Name: NWCmesonet.py
# Author: Brian R. Greene
# University of Oklahoma
# Updated: 26 December 2022
# Purpose: Fetches 1-minute data from National Weather Center Mesonet tower.
# Displays most recent observations as well as a time series of current day's
# T, Td, wind speed, and wind direction.
# --------------------------------
import requests
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import HourLocator, DateFormatter
from matplotlib import rc
from datetime import datetime, timedelta
# --------------------------------
rc('font',weight='normal',size=20,family='serif',serif='Times New Roman')
rc('text',usetex='True')
# --------------------------------
def plot_NWC(date, savedir=None):
    """
    Grab data from NWC mesonet tower and plot
    input date: datetime object for desired date to plot (UTC)
    input savedir: str directory path for where to save figure, default=None
    """
    # Base URL
    base_URL = "http://www.mesonet.org/data/public/nwc/mts-1m/"
    # grab year, month, day from datetime object
    yr = date.year
    mo = date.month
    da = date.day
    # Construct url for mts file
    mts_URL = f"{base_URL}{yr}/{mo:02d}/{da:02d}/{yr:02d}{mo:02d}{da:02d}nwcm.mts"
    # Fetch data
    r = requests.get(mts_URL)
    # parse data
    dat = r.text.split("\n")
    # headers
    headers = dat[2].split()[2:]
    # define dictionary to store data
    nwc = {}
    for h in headers:
        nwc[h] = []
    # grab data and store: loop over lines 3:-1
    for line in dat[3:-1]:
        [nwc[h].append(float(ll)) for ll, h in zip(line.split()[2:], nwc.keys())]
    # convert to numpy arrays
    for key in nwc.keys():
        nwc[key] = np.array(nwc[key])
    # remove bad data
    for val in nwc.values():
        val[val < -100.] = np.nan
    # convert dictionary to xarray Dataset
    # define time coordinate
    times = pd.date_range(start=f"{yr}{mo}{da} 12:00AM", 
                          end=f"{yr}{mo}{da} 11:59PM", freq="min")
    # define dataset
    df = xr.Dataset(data_vars=None, coords=dict(time=times))
    # loop and assign data
    for key, val in nwc.items():
        df[key] = xr.DataArray(data=val, dims="time", coords=dict(time=times))
    # assign metadata
    # units
    df["RELH"].attrs["units"] = "$\\%$"
    df["TAIR"].attrs["units"] = "$^\\circ$C"
    df["WSPD"].attrs["units"] = "m s$^{-1}$"
    df["WDIR"].attrs["units"] = "degrees"
    df["WMAX"].attrs["units"] = "m s$^{-1}$"
    df["RAIN"].attrs["units"] = "" # TODO: update
    df["PRES"].attrs["units"] = "hPa"
    df["SRAD"].attrs["units"] = "W m$^{-2}$"
    df["TA9M"].attrs["units"] = "$^\\circ$C"
    df["WS2M"].attrs["units"] = "m s$^{-1}$"
    df["SKIN"].attrs["units"] = "$^\\circ$C"
    # full name
    df["RELH"].attrs["name_long"] = "Relative Humidity"
    df["TAIR"].attrs["name_long"] = "Air Temperature"
    df["WSPD"].attrs["name_long"] = "Wind Speed"
    df["WDIR"].attrs["name_long"] = "Wind Direction"
    df["WMAX"].attrs["name_long"] = "Wind Gust"
    df["RAIN"].attrs["name_long"] = "Rainfall"
    df["PRES"].attrs["name_long"] = "Pressure"
    df["SRAD"].attrs["name_long"] = "Solar Radiation"
    df["TA9M"].attrs["name_long"] = "9m Air Temperature"
    df["WS2M"].attrs["name_long"] = "2m Wind Speed"
    df["SKIN"].attrs["name_long"] = ""
    # calculate dewpoint temperature
    es = 6.112 * np.exp(17.67 * df.TAIR / (df.TAIR + 243.5))
    e = df.RELH * es / 100.
    Td = (243.5*np.log(e/6.112)) / (17.67 - np.log(e/6.112))
    df["TDEW"] = xr.DataArray(data=Td, dims="time", coords=dict(time=times),
                              attrs={"units": "$^\\circ$C",
                                     "name_long": "Dewpoint Temperature"})
    # convert TAIR, TA9M, and TDEW to degF
    df["TAIR_F"] = 1.8 * df.TAIR + 32.
    df["TA9M_F"] = 1.8 * df.TA9M + 32.
    df["TDEW_F"] = 1.8 * df.TDEW + 32.
    # convert WSPD, WMAX, WS2M to mph
    df["WSPD_mph"] = 2.24 * df.WSPD
    df["WMAX_mph"] = 2.24 * df.WMAX
    df["WS2M_mph"] = 2.24 * df.WS2M
    # update metadata
    df["TAIR_F"].attrs["units"] = "$^\\circ$F"
    df["TA9M_F"].attrs["units"] = "$^\\circ$F"
    df["TDEW_F"].attrs["units"] = "$^\\circ$F"
    df["WSPD_mph"].attrs["units"] = "mph"
    df["WMAX_mph"].attrs["units"] = "mph"
    df["WS2M_mph"].attrs["units"] = "mph"

    # begin plotting
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(14.8, 15))
    # title figure
    figtitle = f"NWC Mesonet {datetime.strftime(date, '%d %B %Y')}"
    fig.suptitle(figtitle)
    # T, Td
    ax[0].plot(df.time, df.TAIR_F, c=(213./255, 94./255, 0), lw=2)
    ax[0].plot(df.time, df.TDEW_F, c=(0, 158./255, 115./255), lw=2)
    ax[0].set_title(f"{df.TAIR.name_long} and {df.TDEW.name_long}")
    ax[0].tick_params(labeltop=False, right=True, labelright=True)
    ax[0].set_ylabel(f"Temperature [{df.TAIR_F.units}]")
    ax[0].grid(axis="y")
    ax[0].yaxis.set_major_locator(MultipleLocator(5))
    # pressure
    ax[1].plot(df.time, df.PRES, c="k", lw=2)
    ax[1].set_title(df.PRES.name_long)
    ax[1].tick_params(labeltop=False, right=True, labelright=True)
    ax[1].set_ylabel("Pressure [hPa]")
    ax[1].grid(axis="y")
    ax[1].yaxis.set_major_locator(MultipleLocator(4))
    # wind speed and direction
    ax[2].plot(df.time, df.WSPD_mph, c=(0, 114./255, 178./255), lw=2)
    ax2_2 = ax[2].twinx()
    ax2_2.plot(df.time, df.WDIR, c=(213./255, 94./255, 0), 
               ls="", marker="o", markersize=1)
    ax[2].set_title(f"{df.WSPD.name_long} and {df.WDIR.name_long}")
    ax[2].set_ylabel(f"{df.WSPD.name_long} [mph]", c=(0, 114./255, 178./255))
    ax2_2.set_ylabel(f"{df.WDIR.name_long}", c=(213./255, 94./255, 0))
    ax2_2.set_yticks(range(0, 405, 45))
    ax2_2.set_yticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax[2].grid(axis="y")
    ax[2].yaxis.set_major_locator(MultipleLocator(5))
    # solar radiation
    ax[3].plot(df.time, df.SRAD, c=(230./255, 159./255, 0), lw=2)
    ax[3].set_title(df.SRAD.name_long)
    ax[3].set_ylabel(f"{df.SRAD.name_long} [{df.SRAD.units}]")
    ax[3].tick_params(labeltop=False, right=True, labelright=True)
    ax[3].grid(axis="y")
    # x-axis format
    ax[3].set_xlim([df.time[0].values, df.time[0].values+np.timedelta64(1, "D")])
    ax[3].xaxis.set_major_locator(HourLocator(byhour=range(0, 24, 1)))
    ax[3].xaxis.set_major_formatter(DateFormatter("%H"))
    ax[3].set_xlabel("Time UTC")
    fig.tight_layout()

    # Save plot if saveFig = True, else just show
    if savedir is not None:
        fig_name = f"{savedir}NWC_Meteogram_{date.strftime('%Y%m%d')}.pdf"
        fig.savefig(fig_name, format="pdf")
        print(f"Finished saving {fig_name}")

    plt.close("all")

# --------------------------------
# Run script if desired
# --------------------------------
if __name__ == "__main__":
    day = datetime(2022, 12, 25)
    dirsave = "/Users/briangreene/Documents/WxUAS/outputFigures/NWCmesonet/"
    plot_NWC(day, dirsave)