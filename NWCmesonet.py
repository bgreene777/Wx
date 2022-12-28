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
import yaml
import requests
import os
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
def get_bounds(value_lo, value_hi, multiple):
    """
    Calculate upper and lower bound for plotting by rounding up/down 
    to nearest multiple
    Return list of 2 values [bound_lo, bound_hi]
    """
    bound_lo = multiple * np.floor(value_lo/multiple)
    bound_hi = multiple * np.ceil(value_hi/multiple)
    return [bound_lo, bound_hi]
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
    mts_URL = f"{base_URL}{yr:04d}/{mo:02d}/{da:02d}/{yr:04d}{mo:02d}{da:02d}nwcm.mts"
    print(f"Fetching file from {mts_URL}")
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
    times = pd.date_range(start=f"{yr:04d}{mo:02d}{da:02d} 12:00AM", 
                          end=f"{yr:04d}{mo:02d}{da:02d} 11:59PM", freq="min")
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
    df["TAIR"].attrs["name_long"] = "1.5m Air Temperature"
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
                                     "name_long": "1.5m Dewpoint Temperature"})
    # convert TAIR, TA9M, and TDEW to degF
    df["TAIR_F"] = 1.8 * df.TAIR + 32.
    df["TA9M_F"] = 1.8 * df.TA9M + 32.
    df["TDEW_F"] = 1.8 * df.TDEW + 32.
    # convert WSPD, WMAX, WS2M to mph
    df["WSPD_mph"] = 2.24 * df.WSPD
    df["WMAX_mph"] = 2.24 * df.WMAX
    df["WS2M_mph"] = 2.24 * df.WS2M
    # # calculate wind chill (1.5m temp, 10m wspd)
    # df["CHIL_F"] = 35.74 + (0.6215*df.TAIR_F) - (35.75*(df.WSPD_mph**0.16)) +\
    #                (0.4275*df.TAIR_F*(df.WSPD_mph**0.16))
    # # calculate heat index (1.5m temp and RH)
    # T = df.TAIR_F
    # RH = df.RELH/100.
    # HI = -42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH -\
    #      .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH +\
    #      .00085282*T*RH*RH - .00000199*T*T*RH*RH
    # # HI adjustments
    # if ((RH.values < 0.13) & (T.values > 80.) & (T.values < 112.)):
    #     HI -=  ((13.-RH)/4.)*np.sqrt((17.-abs(T-95.))/17.)
    # elif ((RH.values > 0.85) & (T.values > 80.) & (T.values < 87.)):
    #     HI += ((RH-85.)/10.) * ((87.-T)/5.)
    # assign to df
    # df["HEAT_F"] = HI
    # update metadata
    df["TAIR_F"].attrs["units"] = "$^\\circ$F"
    df["TA9M_F"].attrs["units"] = "$^\\circ$F"
    df["TDEW_F"].attrs["units"] = "$^\\circ$F"
    # df["CHIL_F"].attrs["units"] = "$^\\circ$F"
    # df["HEAT_F"].attrs["units"] = "$^\\circ$F"
    df["WSPD_mph"].attrs["units"] = "mph"
    df["WMAX_mph"].attrs["units"] = "mph"
    df["WS2M_mph"].attrs["units"] = "mph"
    # define colors for selected parameters
    df["TAIR"].attrs["color"] = (204./255, 102./255, 102./255)
    df["TA9M"].attrs["color"] = (133./255, 22./255, 23./255)
    df["TDEW"].attrs["color"] = (84./255, 83./255, 179./255)
    # df["CHIL"].attrs["color"] = (0, 0, 0)
    # df["HEAT"].attrs["color"] = (0, 0, 0)
    df["PRES"].attrs["color"] = (0, 0, 0)
    df["WSPD"].attrs["color"] = (42./255, 37./255, 113./255)
    df["WDIR"].attrs["color"] = (195./255, 194./255, 122./255)  #(213./255, 94./255, 0)
    df["SRAD"].attrs["color"] = (255./255, 154./255, 52./255)
    df["SRAD"].attrs["color2"] = (245./255, 170./255, 95./255)

    # begin plotting
    print("Begin plotting...")
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(14.8, 12),
                           constrained_layout=True)
    # title figure
    figtitle = f"NWC Mesonet {date.strftime('%d %B %Y')}"
    fig.suptitle(figtitle)
    # T, Td
    ax[0].plot(df.time, df.TAIR_F, c=df.TAIR.color, lw=2, label=df.TAIR.name_long)
    ax[0].plot(df.time, df.TDEW_F, c=df.TDEW.color, lw=2, label=df.TDEW.name_long)
    ax[0].plot(df.time, df.TA9M_F, c=df.TA9M.color, lw=2, label=df.TA9M.name_long)
    ax[0].tick_params(labeltop=False, right=True, labelright=True)
    ax[0].set_ylabel(f"Temperature [{df.TAIR_F.units}]")
    # y-axis limits
    # lowest value
    Tlo = np.min([np.nanmin(df.TAIR_F), np.nanmin(df.TDEW_F), 
                  np.nanmin(df.TA9M_F)])
    Thi = np.max([np.nanmax(df.TAIR_F), np.nanmax(df.TDEW_F), 
                  np.nanmax(df.TA9M_F)])
    Tlim = get_bounds(Tlo, Thi, 5)
    ax[0].set_ylim(Tlim)
    # check how wide range of Tlim is
    if np.diff(Tlim) > 40.:
        Tmul = 10.
    else:
        Tmul = 5.
    ax[0].yaxis.set_major_locator(MultipleLocator(Tmul))
    ax[0].grid(axis="y")
    ax[0].legend(frameon=False, labelspacing=0.10, ncol=3, columnspacing=1,
                 handletextpad=0.4, handlelength=1, fontsize=14,
                 loc="lower center", bbox_to_anchor=(0.5, 0.95))

    # pressure
    ax[1].plot(df.time, df.PRES, c="k", lw=2)
    ax[1].tick_params(labeltop=False, right=True, labelright=True)
    ax[1].set_ylabel("Pressure [hPa]")
    ax[1].grid(axis="y")
    # y-axis limits
    plim = get_bounds(np.nanmin(df.PRES), np.nanmax(df.PRES), 2)
    ax[1].set_ylim(plim)
    # check how wide plim is
    if np.diff(plim) > 10:
        pmul = 4
    else:
        pmul = 2
    ax[1].yaxis.set_major_locator(MultipleLocator(pmul))

    # wind speed and direction
    ax[2].plot(df.time, df.WSPD_mph, c=df.WSPD.color, lw=2)
    ax2_2 = ax[2].twinx()
    ax2_2.plot(df.time, df.WDIR, c=df.WDIR.color, 
               ls="", marker="o", markersize=2)
    ax[2].set_ylabel(f"{df.WSPD.name_long} [mph]", c=df.WSPD.color)
    ax2_2.set_ylabel(f"{df.WDIR.name_long}", c=df.WDIR.color)
    ax2_2.set_yticks(range(0, 405, 45))
    ax2_2.set_ylim(0, 360)
    ax2_2.set_yticklabels(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])
    ax[2].grid(axis="y")
    # y-axis limits
    wslim = get_bounds(0, np.nanmax(df.WSPD_mph), 5)
    ax[2].set_ylim(wslim)
    # check how wide wslim is
    if np.diff(wslim) > 35:
        wsmul = 10
    else:
        wsmul = 5
    ax[2].yaxis.set_major_locator(MultipleLocator(wsmul))

    # solar radiation
    ax[3].plot(df.time, df.SRAD, c=df.SRAD.color, lw=2, zorder=1001)
    ax[3].fill_between(df.time, df.SRAD, color=df.SRAD.color2, zorder=1000)
    ax[3].set_ylabel(f"{df.SRAD.name_long} [{df.SRAD.units}]")
    ax[3].tick_params(labeltop=False, right=True, labelright=True)
    ax[3].grid(axis="y")
    # y-axis limits
    slim = get_bounds(0, np.nanmax(df.SRAD), 100)
    ax[3].set_ylim(slim)
    # check how wide slim is
    if np.diff(slim) > 1200:
        smul = 400
    else:
        smul = 200
    ax[3].yaxis.set_major_locator(MultipleLocator(smul))

    # x-axis format
    ax[3].set_xlim([df.time[0].values, df.time[0].values+np.timedelta64(1, "D")])
    ax[3].xaxis.set_major_locator(HourLocator(byhour=range(0, 24, 1)))
    ax[3].xaxis.set_major_formatter(DateFormatter("%H"))
    ax[3].set_xlabel("Time UTC")
    
    # copyright statement bottom of figure
    cw = "Copyright 1994-2022 Board of Regents of the University of Oklahoma. All Rights Reserved."
    ax[3].text(0.5, -0.35, cw, ha="center", va="center", fontsize=14,
               transform=ax[3].transAxes)

    # Save plot if saveFig = True, else just show
    if savedir is not None:
        # make sure path exists
        if not os.path.exists(savedir):
            os.mkdir(savedir)
        fig_name = f"{savedir}NWC_Meteogram_{date.strftime('%Y%m%d')}.pdf"
        fig.savefig(fig_name, format="pdf")
        print(f"Finished saving {fig_name}")

    plt.close("all")

# --------------------------------
# Run script if desired
# --------------------------------
if __name__ == "__main__":
    # load yaml file
    with open("NWCmesonet.yaml") as f:
        config = yaml.safe_load(f)
    # day = datetime(2022, 12, 22)
    days = pd.date_range(start="20210101", end="20211231", freq="D")
    for day in days:
        plot_NWC(day, config["sdir_local"])