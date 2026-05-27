import numpy as np
from pathlib import Path
from typing import Union, Tuple, Any, List, Iterable
import pandas as pd
from tqdm import tqdm
from ..data_wrapper.utility import parse_naive_utc_time_str
from matplotlib import figure, axes
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.dates import DateFormatter
from matplotlib.ticker import NullFormatter, AutoLocator, ScalarFormatter, MultipleLocator, StrMethodFormatter
import matplotlib.patches as patches
from datetime import datetime, tzinfo, timezone, timedelta, time
from zoneinfo import ZoneInfo
import scipy as sp
from scipy import signal 
from ..utility.constants import (
    COLOR_LEFT_HEMISPHERE, 
    COLOR_RIGHT_HEMISPHERE,
    COLOR_STAGE_DBS_OFF,
    COLOR_STAGE_ALL_ON,
    COLOR_STAGE_RVS
    )



## TODO: Note the mdates locator and formatter in the commented code and delete the commented-out code.

def plot_lfp(x:Iterable, y:Iterable, ax_title:str=None, ax:axes.Axes=None, **kwargs) -> axes.Axes: 
    """Plots the raw LFP data and returns a Axes object."""

    if ax is None: fig, ax = plt.subplots(figsize=(50, 5), layout='tight')
    if ax_title is None: ax_title = "Local Field Potential (LFP) (uV) Time Series"
    
    ax_title_fontsize = 30
    ylabel_fontsize = 20
    legend_fontsize = ylabel_fontsize
    xlabel_fontsize = ylabel_fontsize
    y_major_ticklabel_fontsize = ylabel_fontsize * .6
    y_minor_ticklabel_fontsize = y_major_ticklabel_fontsize * .9
    x_major_ticklabel_fontsize = y_major_ticklabel_fontsize
    x_minor_ticklabel_fontsize = x_major_ticklabel_fontsize * .9

    # ## Plot the LFP timeseries
    ax.plot(x, y, '.-', c=kwargs.get("color", "green"), label=kwargs.get("label", 'LFP (uV)'), alpha=0.5,)

    # ## Adding other artists
    ax.set_title(ax_title, fontsize=ax_title_fontsize)
    ax.set_ylabel("LFP (uV)", fontsize=ylabel_fontsize)
    # ax.set_xlabel("Time (ms)", fontsize=xlabel_fontsize)
    ax.set_xlabel("Data point (~4ms)", fontsize=xlabel_fontsize)
    ax.legend(fontsize=legend_fontsize, loc="upper right")
    ax.grid(visible=True, which="both", axis="both", alpha=0.3)
    ax.set_xmargin(0)

    
    # ## Adjust y-axis
    ax.set_ylim((-23, 23)) # For consistent comparisons
    # ax.yaxis.set_tick_params(which="major", length=10)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_formatter(ScalarFormatter())
    for y_major_ticklabel in ax.yaxis.get_ticklabels(which="major"):
        y_major_ticklabel.set(fontsize=y_major_ticklabel_fontsize)
    for y_minor_ticklabel in ax.yaxis.get_ticklabels(which="minor"): 
        y_minor_ticklabel.set(fontsize=y_minor_ticklabel_fontsize)
    
    # ## Adjust x-axis
    # ax.xaxis.set_tick_params(which="major", length=10)
    ax.xaxis.set_major_locator(MultipleLocator(500))
    ax.xaxis.set_minor_locator(MultipleLocator(250))
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.xaxis.set_minor_formatter(StrMethodFormatter("{x:,.0f}"))

    for x_major_ticklabel in ax.xaxis.get_ticklabels(which="major"):
        x_major_ticklabel.set(fontsize=x_major_ticklabel_fontsize, rotation=90, ha="center")
    for x_minor_ticklabel in ax.xaxis.get_ticklabels(which="minor"):
        x_minor_ticklabel.set(fontsize=x_minor_ticklabel_fontsize, rotation=90, ha="center")

    return ax

def plot_psd(x:List, y:List[float], ax_title:str=None, ax:axes.Axes=None, **kwargs) -> axes.Axes: 
    if ax is None: fig, ax = plt.subplots(figsize=(50, 5), layout='tight')
    if ax_title is None: ax_title = "Power Spectral Density (PSD)"

    ax_title_fontsize = 30
    ylabel_fontsize = 20
    legend_fontsize = ylabel_fontsize
    xlabel_fontsize = ylabel_fontsize
    y_major_ticklabel_fontsize = ylabel_fontsize * .6
    y_minor_ticklabel_fontsize = y_major_ticklabel_fontsize * .9
    x_major_ticklabel_fontsize = y_major_ticklabel_fontsize
    x_minor_ticklabel_fontsize = x_major_ticklabel_fontsize * .9

    ## Plot the PSD
    # ax.plot(x, y, '.-', c=kwargs.get("color", "green"), label=kwargs.get("label", 'LFP'), alpha=0.8,)
    ax.bar(x, y, width=0.5, color=kwargs.get("color", "green"), label=kwargs.get("label", 'PSD'), alpha=0.25,)
    ax.plot(x, y, color=kwargs.get("color", "green"), label=kwargs.get("label", 'PSD'), alpha=0.8,)
    
    ## Adding other artists
    ax.set_title(ax_title, fontsize=ax_title_fontsize)
    ax.set_ylabel(r"PSD ( $\frac{(\mu V)^2}{Hz}$ )", fontsize=ylabel_fontsize)
    ax.set_xlabel("Frequency (Hz)", fontsize=xlabel_fontsize)
    ax.legend(fontsize=legend_fontsize, loc="upper right")
    ax.grid(which="both", axis="both", alpha=0.3)
    ax.set_xmargin(0)

    ## Adjust y-axis
    ax.set_ylim(0, 8)
    # ax.yaxis.set_tick_params(which="major", length=10)
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator())
    ax.yaxis.set_minor_formatter(ScalarFormatter())
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    for y_major_ticklabel in ax.yaxis.get_ticklabels(which="major"):
        y_major_ticklabel.set(fontsize=y_major_ticklabel_fontsize)
    for y_minor_ticklabel in ax.yaxis.get_ticklabels(which="minor"): 
        y_minor_ticklabel.set(fontsize=y_minor_ticklabel_fontsize)

    ## Adjust x-axis
    # nyquist_freq = int(np.ceil(samplingFreq/2))
    ax.set_xlim(0, 125)
    ax.xaxis.set_tick_params(which="major", length=5)
    ax.xaxis.set_tick_params(which="minor", length=1)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_minor_formatter(ScalarFormatter())
    for x_major_ticklabel in ax.xaxis.get_ticklabels(which="major"):
        x_major_ticklabel.set(fontsize=x_major_ticklabel_fontsize)
    for x_minor_ticklabel in ax.xaxis.get_ticklabels(which="minor"): 
        x_minor_ticklabel.set(fontsize=x_minor_ticklabel_fontsize)

    ## Add Beta Band shade
    beta_range = (12.5, 30)
    ymin, ymax = ax.get_ylim()
    beta_band_color = "orange"
    rect = patches.Rectangle((beta_range[0], 0), beta_range[1]-beta_range[0], ymax, facecolor=beta_band_color, alpha=0.1)
    ax.add_patch(rect)

    ## Add annotation
    ymin, ymax = ax.get_ylim()
    ax.annotate("Beta range", (15, (ymax-ymin)*0.90), color = beta_band_color, fontsize=ylabel_fontsize)

    return ax

def plot_boxplot(stage_datas:Iterable[np.ndarray], stage_names:Iterable[np.ndarray], hemisphere:str, ax_title:str=None, ax:plt.Axes=None) -> plt.Axes: 
# def plot_psd_statistics(stats_dbs_off:np.ndarray, stats_treat_1:np.ndarray, stats_treat_2:np.ndarray, ax_title:str=None, ax:axes.Axes=None) -> axes.Axes:
    """Plot and return the Axes of the statistics in a boxplot."""

    if ax is None: 
        fig, ax = plt.subplots(1, figsize = (5, 4), layout="tight")

    baseline_data, baseline_name = stage_datas[0], stage_names[0]
    treatment1_data, treatment1_name = stage_datas[1], stage_names[1]
    treatment2_data, treatment2_name = stage_datas[2], stage_names[2]

    hemisphere = hemisphere.lower()
    if ax_title is None: 
        ax_title = hemisphere

    colors = {"left": COLOR_LEFT_HEMISPHERE, 
              "right": COLOR_RIGHT_HEMISPHERE}

    ## Calculate the T-test p-values
    ## Baseline vs Treat1 - Welch's T-test
    stat1 = sp.stats.ttest_ind(baseline_data, treatment1_data, equal_var=False)
    string1 = f"p-value - {baseline_name} v {treatment1_name} (Welch's T-test): {round(stat1.pvalue, 6)}"
    
    ## Baseline vs Treat2 - Welch's T-test
    stat2 = sp.stats.ttest_ind(baseline_data, treatment2_data, equal_var=False)
    string2 = f"p-value - {baseline_name} v {treatment2_name} (Welch's T-test): {round(stat2.pvalue, 6)}"
    ## Treat1 vs Treat2 - Welch's T-test
    stat3 = sp.stats.ttest_ind(treatment1_data, treatment2_data, equal_var=False)
    string3 = f"p-value - {treatment1_name} vs {treatment2_name} (Welch's T-test): {round(stat3.pvalue, 6)}"

    ## Plot the boxplot
    ax.set_title(f"{ax_title}")
    ax.boxplot(baseline_data,   positions=[1], widths=0.4, showmeans=True)
    ax.boxplot(treatment1_data, positions=[2], widths=0.4, showmeans=True)
    ax.boxplot(treatment2_data, positions=[3], widths=0.4, showmeans=True)
    ax.scatter([1]*len(baseline_data),   baseline_data, marker=".", color=colors[hemisphere], label=hemisphere)
    ax.scatter([2]*len(treatment1_data), treatment1_data, marker=".", color=colors[hemisphere],)
    ax.scatter([3]*len(treatment2_data), treatment2_data, marker=".", color=colors[hemisphere],)
    ax.set_xticklabels([f"{baseline_name}", f"{treatment1_name}", f"{treatment2_name}"])
    
    ax.text(0.1, -0.3, "\n".join([string1, string2, string3]), transform=ax.transAxes)  # https://stackoverflow.com/questions/63153629/use-data-coords-for-x-axis-coords-for-y-for-text-annotations

    ax.legend() 
    return ax

def plot_session_start_times(df_lfp:pd.DataFrame) -> plt.Axes:

    df = df_lfp
    channels = df.Channel.unique()

    fig, ax = plt.subplots(1,1, figsize=(20, 5))
    for channel_y, channel in enumerate(channels):
        channel_y += 1
        mask = df.Channel == channel
        session_numbers = df.index[mask]
        datetimes = df.loc[mask, "FirstPacketDateTime"]
        datetimes = [parse_naive_utc_time_str(datetime) for datetime in datetimes]
        ys = [channel_y]*len(datetimes)
        ax.scatter(datetimes, ys, label=channel)
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_major_formatter(NullFormatter())
        ax.xaxis.set_major_formatter(DateFormatter(fmt="%Y-%m-%d_%H:%M:%S"))
        ax.grid(visible=True, which="major", axis="x")
        ax.legend()
        ax.set_title("Session start times for each channel")
        for x_major_ticklabel in ax.xaxis.get_ticklabels(which="major"): 
            x_major_ticklabel.set(rotation=90, ha="center")
        for datetime, y, session_number in zip(datetimes, ys, session_numbers):
            ax.annotate(text=session_number, 
                        xy=(datetime, y), 
                        xytext=(0, 5), textcoords="offset points")
    return ax

def plot_trend(stage_datas:Iterable[np.ndarray], stage_names, hemisphere:str, label:str, ax_title:str=None, ax:plt.Axes=None) -> plt.Axes: 
    hemisphere = hemisphere.lower()

    if hemisphere == "left": 
        color = COLOR_LEFT_HEMISPHERE
    elif hemisphere == "right": 
        color = COLOR_RIGHT_HEMISPHERE
    else: 
        color="green"
    
    stage_color_map = {
        "dbs_off": COLOR_STAGE_DBS_OFF, 
        "all_on": COLOR_STAGE_ALL_ON,
        "rvs": COLOR_STAGE_RVS,
    }
    
    if ax_title is None: 
        ax_title = "Time Series Trend"

    if ax is None:  
        fig, ax = plt.subplots(figsize=(8, 4))
    stage_lengths = [len(stage_data) for stage_data in stage_datas]
    stage_ends = np.cumsum(stage_lengths)
    stage_starts = stage_ends - stage_lengths
    stage_ranges = [range(stage_start, stage_end) for (stage_start, stage_end) in zip(stage_starts, stage_ends)]

    x = np.arange(np.sum(stage_lengths))
    y = np.hstack(stage_datas)
    ax.plot(x, y, "-.", alpha=0.3, color=color)
    ax.scatter(x, y, marker=".", alpha=1, color=color, label=label)

    ## Add stage marker
    for stage, stage_range in zip(stage_names, stage_ranges):
        color = stage_color_map[stage]
        xmin, xmax = stage_range[0], stage_range[-1]
        ymin, ymax = ax.get_ylim()
        rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, facecolor=color, alpha=0.1)
        ax.add_patch(rect)

        ax.annotate(
            text=f"{stage}", 
            xy=((xmin+xmax)/2, ymin*1.1), color=color, horizontalalignment='center', verticalalignment='bottom')

    ax.legend()
    ax.set_title(ax_title)

    return ax


# def plot_timeseries(trend_data, trend_name, stage_names:Iterable[str], hemisphere:str, ax_title:str=None, ax:plt.Axes=None):
#     from matplotlib import patches

#     hemisphere = hemisphere.lower()
#     colors = {'left': COLOR_LEFT_HEMISPHERE,
#               "right": COLOR_RIGHT_HEMISPHERE}
#     if ax_title is None: 
#         ax_title = hemisphere

#     fig, ax = plt.subplots(figsize=(8, 4))

#     for color_idx, (trend_y, trend_name) in enumerate(zip(trend_data, trend_names)):
#         trend_x = len(trend_y)
#         ax.plot(trend_x, trend_y, marker="-.", alpha=0.3, color=f"C{color_idx+4}")
#         ax.scatter(trend_x, trend_y, marker=".", alpha=1, label=trend_name, color=f"C{color_idx+4}")

#     ## Add stage marker
#     stage_ranges = [range(0, stage_ndata[0]), range(stage_ndata[0], stage_ndata[0]+stage_ndata[1]), range(stage_ndata[0]+stage_ndata[1], stage_ndata[2])]
#     for stage, stage_range, color in zip(stage_names, stage_ranges, ['C1', 'C2', 'C3']):   
#         xmin, xmax = stage_range[0], stage_range[-1]
#         ymin, ymax = ax.get_ylim()
#         rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, facecolor=color, alpha=0.1)
#         ax.add_patch(rect)

#         ax.annotate(
#             text=f"{stage}", 
#             xy=((xmin+xmax)/2, ymin*1.1), color=color, horizontalalignment='center', verticalalignment='bottom')


#     ax.legend()
#     return ax


def plot_single_hemisphere_lfp_psd(lfp_datas:Iterable, psd_datas:Iterable, hemisphere:str, axs:Iterable[plt.Axes]=None): 
    if axs is None: 
        fig, axs = plt.subplots(1, 2, figsize=(90, 8), layout="tight")
    if (hemisphere.lower() != 'left') & (hemisphere.lower() != 'right'): 
        raise ValueError(f"Argument 'hemisphere' has to be either 'left' or 'right'; got {hemisphere}") 
    
    label = hemisphere
    if hemisphere.lower() == "left": color = COLOR_LEFT_HEMISPHERE
    if hemisphere.lower() == 'right': color = COLOR_RIGHT_HEMISPHERE

    lfp_x = lfp_datas[0]
    lfp_y = lfp_datas[1]
    lfp_ax = axs[0]
    
    psd_x = psd_datas[0]
    psd_y = psd_datas[1]
    psd_ax = axs[1]

    ax1 = plot_lfp(x=lfp_x, y=lfp_y, ax=lfp_ax, label=label, color=color)
    ax2 = plot_psd(x=psd_x, y=psd_y, ax=psd_ax, label=label, color=color, samplingFreq=250)

    return (ax1, ax2)


def plot_both_hemisphere_lfp_psd(left_lfp_datas, right_lfp_datas, left_psd_datas, right_psd_datas, axs=None): 
    if axs is None: 
        fig, axs = plt.subplots(1, 2, figsize=(90, 8), layout="tight")

    ax1, ax2 = plot_single_hemisphere_lfp_psd(left_lfp_datas, left_psd_datas, hemisphere='left', axs=axs)
    ax1, ax2 = plot_single_hemisphere_lfp_psd(right_lfp_datas, right_psd_datas, hemisphere='right', axs=axs)

    return (ax1, ax2)



# def single_hemisphere_statistic_boxplot(hemisphere:str, single_hemisphere_data:np.ndarray, statistic:str, session_stages:Dict, beta_type:str):
#     assert isinstance(single_hemisphere_data, np.ndarray), "single_hemisphere_data have to be np.ndarray"
#     hemisphere = hemisphere.lower()
#     assert (hemisphere=='left') | (hemisphere=='right'), "hemisphere has to be either 'left' or 'right'"

#     hemisphere_colors = {
#         "left": "blue", 
#         "right": "red",
#     }

#     fig, axs = plt.subplots(
#         1, len(hemisphere_colors.keys()), 
#         figsize = (5*len(hemisphere_colors.keys()), 4), 
#         layout="tight"
#     )

#     stat_dbs_off = single_hemisphere_data[ stages["DBS-off"][0]:stages["DBS-off"][-1]+1 ]
#     stat_all_on = single_hemisphere_data[ stages['All-on'][0]:stages['All-on'][-1]+1 ]
#     stat_rvs = single_hemisphere_data[ stages['RVS'][0]:stages['RVS'][-1]+1 ]
    
#     ## DBS_off vs All-on - Welch's T-test
#     stat1 = scp.stats.ttest_ind(stat_dbs_off, stat_all_on, equal_var=False)
#     string1 = f"DBS-off v All-On (Welch T-test): {round(stat1.pvalue, 6)}"

#     ## DBS_off vs RVS - Welch's T-test
#     stat2 = scp.stats.ttest_ind(stat_dbs_off, stat_rvs, equal_var=False)
#     string2 = f"DBS-off v RVS (Welch T-test): {round(stat2.pvalue, 6)}"

#     ## All-on vs RVS - Welch's T-test
#     stat3 = scp.stats.ttest_ind(stat_all_on, stat_rvs, equal_var=False)
#     string3 = f"All-on vs RVS (Welch T-test): {round(stat3.pvalue, 6)}"
        
#     # Plot
#     ax_idx = 0 if hemisphere=='left' else 1
#     axs[ax_idx].set_title(f"{hemisphere.capitalize()} PSD {beta_type.capitalize()} {statistic.capitalize()}")

#     axs[ax_idx].boxplot(stat_dbs_off, positions=[1], widths=0.4)
#     axs[ax_idx].boxplot(stat_all_on, positions=[2], widths=0.4)
#     axs[ax_idx].boxplot(stat_rvs, positions=[3], widths=0.4)
    
#     axs[ax_idx].scatter([1]*len(stat_dbs_off), stat_dbs_off, marker=".", c=hemisphere_colors[hemisphere])
#     axs[ax_idx].scatter([2]*len(stat_all_on), stat_all_on, marker=".", c=hemisphere_colors[hemisphere])
#     axs[ax_idx].scatter([3]*len(stat_rvs), stat_rvs, marker=".", c=hemisphere_colors[hemisphere])
    
#     axs[ax_idx].set_xticklabels(["DBS Off", "All-On", "RVS"])
#     axs[ax_idx].text(0.1, -0.3, "\n".join([string1, string2, string3]), transform=axs[ax_idx].transAxes)
        
#     return fig

# for beta_type in ["whole-beta", "high-beta", "low-beta"]: 
#     # for statistic in ['mean', 'median', 'sum', 'max', 'min']:
#     for statistic in ['mean', 'sum']:
#         single_hemisphere_data = df_stats[f"session_{beta_type}_{statistic}"].values
#         fig = single_hemisphere_statistic_boxplot('left', single_hemisphere_data, statistic, stages, beta_type)
#         plt.show(fig)

# for beta_type in ["whole-beta", "high-beta", "low-beta"]: 
#     # for statistic in ['mean', 'median', 'sum', 'max', 'min']:
#     for statistic in ['mean', 'sum']:
#         single_hemisphere_data = df_stats[f"session_{beta_type}_{statistic}"].values
#         fig = single_hemisphere_statistic_boxplot('right', single_hemisphere_data, statistic, stages, beta_type)
#         plt.show(fig)




## NOTE: Note the mdates locator and formatter
# def plot_lfp(x:Iterable, y:Iterable, ax_title:str=None, ax:axes.Axes=None, **kwargs) -> axes.Axes: 
#     """Plots the raw LFP data and returns a Axes object.

#     By providing an Axes object, this function is capable of plotting the LFP
#     raw datapoints directly onto the Axes object and return it. In such a case
#     this function encapsulates the plotting format and logic thus serving like
#     a transformer.
    
#     Args:
#         x (List[datetime]): UTC Timestamps of each LFP data point.
#         y (List[float]): LFP (uV) data point corresponding to each element of x.
#         ax (axes.Axes): Optional - Matplotlib Axes object to be plotted on.

#     Returns:
#         (axes.Axes): A Matplotlib Axes object. 
#     """
#     if ax is None: fig, ax = plt.subplots(figsize=(50, 5), layout='tight')
#     if ax_title is None: ax_title = "LFP (uV) Time Series"
    
#     ax_title_fontsize = 30
#     ylabel_fontsize = 20
#     xlabel_fontsize = ylabel_fontsize

#     # ## Plot the LFP timeseries
#     ax.plot(x, y, '.-', c=kwargs.get("color", "green"), label=kwargs.get("ax_label", 'LFP'), alpha=0.5,)

#     # ## Adding other artists
#     ax.set_title(ax_title, fontsize=ax_title_fontsize)
#     ax.set_ylabel("LFP (uV)", fontsize=ylabel_fontsize)
#     ax.set_xlabel("Timestamp (UTC)", fontsize=ylabel_fontsize)
#     ax.legend(fontsize=ylabel_fontsize, loc="upper right")
    
#     # ## Adjust y-axis
#     ax.set_ylim((-23, 23)) # For consistent comparisons
#     ax.yaxis.set_tick_params(which="major", length=10)
#     for ytickLabel in ax.yaxis.get_ticklabels():
#         ytickLabel.set(fontsize=ylabel_fontsize)
    
#     # ## Adjust x-axis
#     ax.xaxis.set_major_locator(mdates.SecondLocator())
#     ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
#     ax.xaxis.set_tick_params(which="major", length=10)
#     for xtickLabel in ax.xaxis.get_ticklabels():
#         xtickLabel.set(fontsize=xlabel_fontsize, rotation=45, ha="right")

#     return ax