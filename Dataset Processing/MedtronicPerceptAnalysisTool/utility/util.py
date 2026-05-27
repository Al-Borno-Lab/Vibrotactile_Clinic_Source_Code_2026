################################################################################
## Utilities code for parsing Medtronic BrainSense JSON output.
##
## Author: Anthony Lee anthony8lee@gmail.com
################################################################################

import numpy as np
from pathlib import Path
from typing import Union, Tuple, Any, List
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import time
from datetime import datetime, tzinfo, timezone, timedelta, time
from zoneinfo import ZoneInfo
from scipy import signal 
import itertools

plt.ioff()

def plot_lfp_raw_and_psd(df_period:pd.DataFrame, session:str = None) -> List[plt.Figure]: 
    """Takes a Pandas dataframe and return a list of figures.

    This function takes in a dataframe of raw LFP recording, calculates the PSD and then
    returns an LFP timeseries plot along with the PSD analysis plot.
    """
    ylabel_fontsize = 20
    xlabel_fontsize = ylabel_fontsize
    n_sessions = df_period["Session Number"].unique().size
    list_of_fig = []
    
    for idx_session in range(n_sessions):
        fig, axs = plt.subplot_mosaic([["raw", "raw", "power"]], figsize=(50, 5), layout="tight")
        df_session_left = df_period[ (df_period["Session Number"]==idx_session) & (df_period["DBS Channel"]=="ZERO_THREE_LEFT") ] 
        df_session_right = df_period[ (df_period["Session Number"]==idx_session) & (df_period["DBS Channel"]=="ZERO_THREE_RIGHT") ] 
        ax_lfp_raw = axs["raw"]
        ax_lfp_power = axs["power"]
        freq = 250
        subset = int( 30 / (1/freq) )  # First 30sec worth of recordings, 1/250 because recording is done at 250Hz

        #################### 
        ## Plot LFP raw
        #################### 
        x_left = df_session_left["Timestamps (UTC)"].iloc[:subset]
        y_left = df_session_left["LFP (uV)"].iloc[:subset]
        x_right = df_session_right["Timestamps (UTC)"].iloc[:subset]
        y_right = df_session_right["LFP (uV)"].iloc[:subset]
    
        ax_lfp_raw.plot(x_left, y_left, ".-", c="blue", label="Left", alpha=0.3)
        ax_lfp_raw.plot(x_right, y_right, ".-", c="red", label="Right", alpha=0.3)

        ## Adding other artists
        ax_lfp_raw.set_title(f"{session} - Raw LFP - Recording Session {idx_session}", fontsize = 30)
        ax_lfp_raw.set_ylabel("LFP (uV)", fontsize=ylabel_fontsize)
        ax_lfp_raw.set_xlabel("Timestamp (UTC)", fontsize=ylabel_fontsize)
        ax_lfp_raw.legend(fontsize=ylabel_fontsize, loc="upper right")
        
        ## Adjust y-axis
        ax_lfp_raw.set_ylim((-23, 23)) # For consistent comparisons
        ax_lfp_raw.yaxis.set_tick_params(which="major", length=10)
        for ytickLabel in ax_lfp_raw.yaxis.get_ticklabels():
            ytickLabel.set(fontsize=ylabel_fontsize)
        
        ## Adjust x-axis
        ax_lfp_raw.xaxis.set_major_locator(mdates.SecondLocator())
        ax_lfp_raw.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        ax_lfp_raw.xaxis.set_tick_params(which="major", length=10)
        for xtickLabel in ax_lfp_raw.xaxis.get_ticklabels():
            xtickLabel.set(fontsize=xlabel_fontsize, rotation=45, ha="right")

        #################### 
        ## Plot LFP power
        #################### 
        lfp_raw_left = df_session_left["LFP (uV)"].iloc[:subset]
        lfp_raw_right = df_session_right["LFP (uV)"].iloc[:subset]

        ## Manual calculation - SOMETHING IS WRONG
        # psd_n = len(lfp_raw_left)
        # x_left, y_left = psd_analysis(lfp_raw_left, psd_n)
        # x_right, y_right = psd_analysis(lfp_raw_right, psd_n)
        
        ## Welch's method: 
        x_left, y_left = signal.welch(lfp_raw_left, fs=freq, scaling="density")  # Default to Hanning window
        x_right, y_right = signal.welch(lfp_raw_right, fs=freq, scaling="density")  # Default to Hanning window
        
        ## Peridogram - Equivalent to Matlab pspectrum()
        # x_left, y_left = signal.periodogram(lfp_raw_left, fs=freq, scaling="density")
        # x_right, y_right = signal.periodogram(lfp_raw_right, fs=freq, scaling="density")
        
        ax_lfp_power.plot(x_left, y_left, ".-", c="blue", label="Left", alpha=0.4)
        ax_lfp_power.plot(x_right, y_right, ".-", c="red", label="Right", alpha=0.4)

        ## Adding other artists
        ax_lfp_power.set_title(f"{session} - PSD (Welch Method) - Recording Session {idx_session}", fontsize=30)
        ax_lfp_power.set_ylabel("PSD ( (uV)^2/Hz )", fontsize=ylabel_fontsize)
        ax_lfp_power.set_xlabel("Frequency (Hz)", fontsize=ylabel_fontsize)
        ax_lfp_power.legend(fontsize=ylabel_fontsize, loc="upper right")

        ## Adjust y-axis
        ax_lfp_power.set_ylim(0, 8)
        ax_lfp_power.yaxis.set_tick_params(which="major", length=10)
        # ax_lfp_power.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x: d}'))
        for ytickLabel in ax_lfp_power.yaxis.get_majorticklabels():
            ytickLabel.set(fontsize=ylabel_fontsize)
    
        ## Adjust x-axis
        nyquist_freq = int(np.ceil(freq/2))
        ax_lfp_power.set_xlim(0, 50)
        ax_lfp_power.xaxis.set_tick_params(which="major", length=10)
        ax_lfp_power.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax_lfp_power.xaxis.set_minor_locator(ticker.MultipleLocator(1))
        ax_lfp_power.xaxis.set_minor_formatter(ticker.NullFormatter())
        for xtickLabel in ax_lfp_power.xaxis.get_majorticklabels():
            xtickLabel.set(fontsize=xlabel_fontsize)

        ## Add Beta Band shade
        beta_range = (12.5, 30)
        ymin, ymax = ax_lfp_power.get_ylim()
        beta_band_color = "orange"
        rect = patches.Rectangle((beta_range[0], 0), beta_range[1]-beta_range[0], ymax, facecolor=beta_band_color, alpha=0.1)
        ax_lfp_power.add_patch(rect)

        ## Add annotation
        ymin, ymax = ax_lfp_power.get_ylim()
        ax_lfp_power.annotate("Beta range", (15, (ymax-ymin)*0.90), color = beta_band_color, fontsize=ylabel_fontsize) 

        #################### 
        ## Append to placeholder
        #################### 
        list_of_fig.append(fig)
    
    return list_of_fig


def calculate_psd_statistics(df): 
    """Calculate the statistics within the biomaker beta-band.
    
    This function only takes the first 30sec worth of LFP data using the subset mask.
    """
    ## Variables
    beta_range = (12.5, 30)
    freq = 250
    uniq_sessions = df["Session Number"].unique()
    uniq_channels = ["ZERO_THREE_LEFT", "ZERO_THREE_RIGHT"]
    subset = int( 30 / (1/250) )  # 30 seconds worth of data points - 7500 data points

    ## Placeholders
    left_power_metric_mean = []
    right_power_metric_mean = []
    left_power_metric_median = []
    right_power_metric_median = []
    left_power_metric_sum = []
    right_power_metric_sum = []
    left_power_metric_max = []
    right_power_metric_max = []
    
    for session_idx in uniq_sessions:
        mask_left = (df["Session Number"] == session_idx) & (df["DBS Channel"] == "ZERO_THREE_LEFT")
        mask_right = (df["Session Number"] == session_idx) & (df["DBS Channel"] == "ZERO_THREE_RIGHT")
        raw_lfp_left = df.loc[ mask_left, "LFP (uV)" ].iloc[:subset]
        raw_lfp_right = df.loc[ mask_right, "LFP (uV)" ].iloc[:subset]

        ## Calculate power
        x_left, y_left = signal.periodogram(raw_lfp_left, fs=freq, scaling="density")
        x_right, y_right = signal.periodogram(raw_lfp_right, fs=freq, scaling="density")

        ## Subset power
        freq_mask_left = (x_left >= beta_range[0]) & (x_left <= beta_range[1])
        freq_mask_right = (x_right >= beta_range[0]) & (x_right <= beta_range[1])
        y_left = y_left[freq_mask_left]
        y_right = y_right[freq_mask_right]

        ## Calculate the statistic
        # Mean 
        left_power_metric_mean.append( np.mean(y_left) )
        right_power_metric_mean.append( np.mean(y_right) )
        # Median
        left_power_metric_median.append( np.median(y_left) )
        right_power_metric_median.append( np.median(y_right) )
        # Sum
        left_power_metric_sum.append( np.sum(y_left) ) 
        right_power_metric_sum.append( np.sum(y_right) ) 
        # Max
        left_power_metric_max.append( np.max(y_left) )
        right_power_metric_max.append( np.max(y_right) )
        
    return pd.DataFrame({
        "left_beta_mean": left_power_metric_mean, 
        "right_beta_mean": right_power_metric_mean, 
        "left_beta_median": left_power_metric_median,
        "right_beta_median": right_power_metric_median,
        "left_beta_sum": left_power_metric_sum,
        "right_beta_sum": right_power_metric_sum,
        "left_beta_max": left_power_metric_max,
        "right_beta_max": right_power_metric_max,
    })


def psd_analysis(input_array:np.ndarray, n:int=None) -> np.ndarray: 
    """Power Spectral Density analysis."""
    fft = np.fft.fft(input_array, n)
    psd = np.abs( np.conj(fft) * fft / n )
    # freq = np.array(np.arange(n)) # xaxis
    freq = np.arange(n)

    return np.array([freq, psd])

def psd_plot(freq:np.ndarray, power:np.ndarray) -> plt.Figure: 
    fig, ax = plt.subplots()
    ax.plot(freq, power)
    xmax = int(np.ceil(freq.max()/2))
    ax.set_xlim(1, xmax)

    ax.set_title("PSD")
    ax.set_ylabel("Power")
    ax.set_xlabel("Frequency (Hz)")

    ## Add Beta Band shade
    ymin, ymax = ax.get_ylim()
    beta_band_color = "orange"
    rect = patches.Rectangle((13, 0), 31-13, ymax, facecolor=beta_band_color, alpha=0.1)
    ax.add_patch(rect)
    
    ## Add annotation
    # ax.annotate("Beta range", (15, (ymax-ymin)*0.70), color = beta_band_color) 

    return fig

def extract_nested_dict(a_dict: dict, search_seq: list[str]) -> Any:
    """Walk the nested dict and return the value.

    The extraction is able to handle cases when dict value is encoded as
    a list
    """
    ## Check a_dict type
    assert isinstance(
        a_dict, dict
    ), f"a_dict has to be of type <dict> but received {type(a_dict)}"

    ## Variables
    traverse_depth = 0
    temp_value = a_dict

    for search_term in search_seq:
        if (
            isinstance(search_term, int) or search_term.isnumeric()
        ):  # Logical operator is short-circuiting
            search_term = int(search_term)
            temp_value = temp_value[search_term]
            traverse_depth += 1
        elif isinstance(search_term, str):
            temp_value = temp_value[search_term]
            traverse_depth += 1
        else:
            raise KeyError(f"Key at index {traverse_depth} of search_seq is not found.")
    return temp_value

def remove_patient_info(a_dict: dict) -> dict:
    """Deletes patient information."""

    del a_dict["PatientInformation"]
    return a_dict

def json_to_dict(path_to_json: Union[str, Path]) -> dict:
    """Takes either a Path or string of a JSON and return a Python dictionary."""

    ## Convert to Path object
    if not isinstance(path_to_json, Path):
        path_to_json = Path(path_to_json)

    ## Load the json
    with open(path_to_json, "r") as file:
        parsed_dict = json.load(file)

    return parsed_dict

## Function to parse naive time string
def parse_naive_utc_time_str(time_str: str, format: str = None) -> datetime:
    """Parse string from UTC to an aware datetime object.

    Args:
      time_str (str) : The string is assumed to be in UTC.
    """

    if format == None:
        format = "%Y-%m-%dT%H:%M:%S.%fZ"
    assert (isinstance(time_str, str) 
            & isinstance(format, str), 
            "Both inputs have to be of type str."
            )

    str_parsed_time = datetime.strptime(time_str, format)      # TZ naive time
    aware_time = str_parsed_time.replace(tzinfo=timezone.utc)  # TZ aware time (by adding tzinfo)

    return aware_time


## Parse LFP time-domain data from the JSON to dataframe
def extract_lfp_raw_timedomain_to_df(path_to_json: Union[str, Path]) -> pd.DataFrame:
    """Extract the LFP raw timedomain data from specified JSON to a Pandas dataframe.

    Depending on the electrode configuration, the session number may mean different things. 
    For example, in our experiment we have one channel in each hemisphere, thus the 
    recording sessions are paired up to indicate the left and right hemisphere. In other 
    words, in our dataset, the odd session number refers to the left hemisphere and the 
    even session number refers to the right hemisphere.

    """
    parsed_dict = json_to_dict(path_to_json)
    parsed_dict = remove_patient_info(parsed_dict)

    df_recording_sessions = pd.json_normalize(parsed_dict, "BrainSenseTimeDomain")

    n_row = df_recording_sessions.shape[0]

    # Placeholders - Pandas recommends creating lists instead of concatenating multiple dataframes.
    holderSessionNum = []
    holderChannel = []
    holderGain = []
    holderTimeStamp = []
    holderSampleRateInHz = []
    holderLfp = []

    for idx in range(n_row):
        # TOOD: Future - Use apply() to improve performance b/c iterating through a pd dataframe is anti-pattern
        session_data = df_recording_sessions.iloc[idx, :]
        firstPacketSize = np.fromstring(
            session_data["GlobalPacketSizes"], dtype=int, sep=","
        )[0]
        channel = session_data["Channel"]
        gain = session_data["Gain"]
        firstPacketDateTime = parse_naive_utc_time_str(
            session_data["FirstPacketDateTime"]
        )
        sampleRateInHz = session_data["SampleRateInHz"]
        samplePeriod = 1 / sampleRateInHz * 1000  # millisecond
        samplePeriodDelta = timedelta(milliseconds=samplePeriod)
        timeDomainData = session_data["TimeDomainData"]
        lenTimeDomainData = len(timeDomainData)

        # Create list of session number
        holderSessionNum.extend([idx] * lenTimeDomainData)

        # Create list of channel
        holderChannel.extend([channel] * lenTimeDomainData)

        # Create list of gain
        holderGain.extend([gain] * lenTimeDomainData)

        # Create list of timestamps
        firstTimeStamp = (
            firstPacketDateTime - (samplePeriodDelta * (firstPacketSize - 1))
        ).timestamp()  # POSIX timestamp
        listTimestamp = np.arange(0, lenTimeDomainData) * 4 / 1000 + firstTimeStamp
        listDateTime = [
            datetime.fromtimestamp(time, tz=timezone.utc) for time in listTimestamp
        ]
        assert (
            len(listDateTime) == lenTimeDomainData
        ), "Datetime list length does not match the number of data."
        holderTimeStamp.extend(listDateTime)

        # Create list of SampleRateInHz
        holderSampleRateInHz.extend([sampleRateInHz] * lenTimeDomainData)

        # Create list of LFP
        holderLfp.extend(timeDomainData)

    # Assemble the dataframe
    df_final = pd.DataFrame(
        data={
            "Session Number": holderSessionNum,
            "DBS Channel": holderChannel,
            "Gain": holderGain,
            "Timestamps (UTC)": holderTimeStamp,
            "Sample Rate (Hz)": holderSampleRateInHz,
            "LFP (uV)": holderLfp,
        }
    )

    return df_final

## Parse LFP power frequency-domain data from the JSON to dataframe
def extract_lfp_power_timedomain_to_df(path_to_json: Union[str, Path]) -> pd.DataFrame:
    """Extract the LFP power from the JSON and return a Pandas dataframe."""

    parsed_dict = json_to_dict(path_to_json)
    parsed_dict = remove_patient_info(parsed_dict)

    df_recording_sessions = pd.json_normalize(parsed_dict, "BrainSenseLfp")

    n_row = df_recording_sessions.shape[0]

    ## Prebuilt list of data for pd.DataFrame constructor
    list_datetime = []
    list_Seq = []
    list_TicksInMs = []
    list_Left_Hz = []
    list_Left_LFP = []
    list_Left_mA = []
    list_Right_Hz = []
    list_Right_LFP = []
    list_Right_mA = []

    ## Iterate through all the records
    for idx in range(n_row):
        session_data = df_recording_sessions.iloc[idx, :]
        lfpdata = pd.json_normalize(session_data["LfpData"])
        n_lfpdata = lfpdata.shape[0]

        ## Creating list of datetime in UTC
        first_packet_datetime = [
            parse_naive_utc_time_str(session_data["FirstPacketDateTime"])
        ] * n_lfpdata
        time_deltas = (
            [timedelta(milliseconds=500)] * n_lfpdata * np.arange(0, n_lfpdata)
        )  ## TODO: Use the SampleRateInHz instead of hard-coding 500ms
        final_datetime = first_packet_datetime + time_deltas
        list_datetime.extend(final_datetime)

        ## Creating list of seq
        list_Seq.extend(lfpdata["Seq"])

        ## Creating Ticks in milliseconds
        list_TicksInMs.extend(lfpdata["TicksInMs"])

        ## Creating left and right recording Hz
        list_Left_Hz.extend(
            [session_data["TherapySnapshot.Left.FrequencyInHertz"]] * n_lfpdata
        )
        list_Right_Hz.extend(
            [session_data["TherapySnapshot.Right.FrequencyInHertz"]] * n_lfpdata
        )

        ## Creating Left LFP and mA
        list_Left_LFP.extend(lfpdata["Left.LFP"])
        list_Left_mA.extend(lfpdata["Left.mA"])

        ## Creating Right LFP and mA
        list_Right_LFP.extend(lfpdata["Right.LFP"])
        list_Right_mA.extend(lfpdata["Right.mA"])

    ## Create final dataframe

    df_final = pd.DataFrame(
        data={
            "Timestamp (UTC)": list_datetime,
            "Seq": list_Seq,
            "TicksInMs": list_TicksInMs,
            "Left Hz": list_Left_Hz,
            "Right Hz": list_Right_Hz,
            "Left LFP Power": list_Left_LFP,
            "Right LFP Power": list_Right_LFP,
            "Left mA": list_Left_mA,
            "Right mA": list_Right_mA,
        }
    )

    return df_final

## TODO: Migrate the extraction code from notebook to the module here.
## Parse the PSD frequency-domain data from the JSON to dataframe
# plot_extracted_data - Used in 0th notebook
# def extract_psd_frequencydomain_to_df(path_to_json: Union[str, Path]) -> pd.DataFrame:
#     """Extract PSD (power spectral density) analysis plot from JSON to Pandas dataframe.
    
#     The PSD analysis is done by the BrainSense tablet and was also the plot that 
#     was used by the clinician to select the frequency for the left/right electrode
#     for recording.
#     """
#     parsed_dict = json_to_dict(path_to_json)
#     parsed_dict = remove_patient_info(parsed_dict)

#     temp = pd.json_normalize(parsed_dict, ["Groups", "Initial"])
#     # temp = pd.json_normalize(temp, ["ProgramSettings", "SensingChannel"])

#     # n_row = df_recording_sessions.shape[0]

#     return temp

def plot_lfp_raw_timedomain(df_lfp_raw_timedomain: pd.DataFrame) -> plt.Figure:
    """Convenience function to plot the LFP raw timedomain data and return a figure.

    TODO: To Implement:
    The goal of this function is to plot a single pair of left/right hemisphere LFP
    raw data in the timedomain. This is tricky to implement becuase the left and right
    hemisphere's data are recorded in different session number and according to the
    recording configuration, one may need to access more than one session data.
    """
    ## TODO: To implement
    pass


def plot_lfp_raw_timedomain_series(df_lfp_raw_timedomain: pd.DataFrame, ) -> List[plt.Figure]:
    """Convenience function to plot a whole series of LFP raw timedomain data."""
    df = df_lfp_raw_timedomain
    total_sessions = max(df["Session Number"]) + 1
    list_of_fig = []

    for i in range(total_sessions):
        # print(f"Plotting {i}-th plot.")

        subsetDf = df[df["Session Number"] == i]

        x = subsetDf["Timestamps (UTC)"]
        y = subsetDf["LFP (uV)"]
        channel = subsetDf["DBS Channel"].iloc[0]

        if i % 2 == 0:
            fig, ax = plt.subplots(figsize=(50, 10))
        if "LEFT" in channel:
            ax.plot(x, y, color="blue", label=channel)
        elif "RIGHT" in channel:
            ax.plot(x, y, color="red", label=channel)

        ax.set_title(f"Session {int((i+1)/2)}", fontsize=36)
        ax.set_xlabel("Datetime (UTC)", fontsize=30)
        ax.set_ylabel("LFP (uV)", fontsize=30)
        ax.set_ylim(-25, 25)
        # temp = ax.get_xlim()
        # print(temp[1]-temp[0])
        ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[0] + 70e-5)  # Seconds * 1e-5
        ax.xaxis.set_major_locator(ticker.LinearLocator(numticks=45))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        # ax.tick_params(axis="x", which="minor", bottom=False)
        ax.legend(prop={"size": 25})
        ax.xaxis.set_major_locator(mdates.SecondLocator())
        # for xtick, ytick in zip(ax.xaxis.get_major_ticks(), ax.yaxis.get_major_ticks()):
        #     xtick.label.set_fontsize(25)
        #     ytick.label.set_fontsize(25)
        for xtickLabel in ax.xaxis.get_ticklabels():
            xtickLabel.set(fontsize=18, rotation=45, ha="right")
        for ytickLabel in ax.yaxis.get_ticklabels():
            ytickLabel.set(fontsize=20)
        list_of_fig.append(fig)

    return list_of_fig


def plot_lfp_power_timedomain_series(
    df_lfp_power_timedomain: pd.DataFrame,
) -> List[plt.Figure]:
    df = df_lfp_power_timedomain

    fig, ax = plt.subplots(figsize=(30, 5), dpi=300)
    ax.set_title("LFP Power", fontsize=36)
    ax.set_xlabel("Date time in UTC", fontsize=18)  # FIX
    ax.set_ylabel("LFP Power", fontsize=18)
    ax.minorticks_on()
    # ax.scatter(df_lfp.index, df_lfp["Right_LFP"], s=3, color="blue", label="Right_LFP at 18.55 Hz")
    # ax.scatter(df_lfp.index, df_lfp["Left_LFP"], s=3, color="red", label="Left_LFP at 19.53 Hz")
    ax.plot(
        df["Timestamp (UTC)"],
        df["Left LFP Power"],
        ".-",
        color="blue",
        label=f"Left LFP Power at {df['Left Hz'][0]} Hz",
    )
    ax.plot(
        df["Timestamp (UTC)"],
        df["Right LFP Power"],
        ".-",
        color="red",
        label=f"Right LFP Power at {df['Right Hz'][0]} Hz",
    )
    ax.legend(prop={"size": 25})

    return fig