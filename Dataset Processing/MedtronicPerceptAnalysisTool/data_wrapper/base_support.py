from pathlib import Path
import numpy as np
import pandas as pd
import json
from typing import Dict
from ..utility import constants
from datetime import datetime, timedelta
from MedtronicPerceptAnalysisTool.signal_processor.filter import BandpassFilterProcessor
from MedtronicPerceptAnalysisTool.signal_processor.psd import PowerSpectralDensityProcessor
from MedtronicPerceptAnalysisTool.utility.constants import FrequencyRange
from .utility import get_sampling_freq
from ..signal_processor.burst import detect_burst_tinkhauser_2017, calculate_burst_statistics
from datetime import timezone
import xarray as xr

def parse_BrainSenseTimeDomain_from_path(json_path: Path) -> pd.DataFrame:

    with open(json_path, "r") as file:
        unserialized_dict = json.load(file)
        output_df = pd.json_normalize(
            data=unserialized_dict,
            record_path=["BrainSenseTimeDomain"],
            meta=[
                "ProgrammerUtcOffset",
                "ProgrammerVersion",
                "BatteryInformation",
                "LeadConfiguration",
                "Impedance",
            ],
            meta_prefix="Metadata.",
        )

    return output_df

def add_treatment_branch_column(df:pd.DataFrame, mapping_stage_to_range:Dict)->pd.DataFrame: 
    
    from datetime import datetime
    
    assert isinstance(df["FirstPacketDateTime"].iloc[0], datetime), "The `FirstPacketDateTime` column is not in `datetime` format."

    reversed_map = {}
    for treatment, idx_range in mapping_stage_to_range.items():
        for idx in idx_range:
            reversed_map[str(idx)] = treatment
        
    df_holder = []
    
    for channel in df.Channel.unique():
        temp_df = df.query(f"Channel == '{channel}'")
        temp_df = temp_df.sort_values(["Channel", "FirstPacketDateTime"], ascending=True).reset_index(drop=True)
        temp_df["TreatmentBranch"] = [reversed_map[str(index)] for index in temp_df.index]
        df_holder.append(temp_df)
    
    df = pd.concat(df_holder, axis=0)
    df = df.sort_values(["FirstPacketDateTime", "Channel"]).reset_index(drop=True)
    
    return df

def convert_firstpacketdatetime_to_datetime_obj(df):
    # df.loc[:, "FirstPacketDateTime"] = pd.to_datetime(df.FirstPacketDateTime, format="ISO8601")
    df["FirstPacketDateTime"] = pd.to_datetime(df.FirstPacketDateTime, format="ISO8601")
    return df

def remove_non_standard_sessions_based_on_treatment_branch(df):
    protocol_defined_treatment_stages = [str(stage) for stage in constants.TreatmentStage]
    mask_normal_treatmentbranches = df.TreatmentBranch.isin(protocol_defined_treatment_stages)
    df = df.loc[mask_normal_treatmentbranches, :]
    return df

def add_patient_number_column(df, classname:str):
    # patient_number = int(self.__class__.__name__.split("_")[1])
    patient_number = int( classname.split("_")[1] )
    df.loc[:, "PatientNumber"] = patient_number
    return df

def add_column_treatment_number(df,):
    treatment_order = df.TreatmentOrder.iloc[0].split(",")
    mapper = {treatment_branch: treatment_num for treatment_branch, treatment_num in zip(treatment_order, ["dbs_off", "treatment_1", "treatment_2"]) }
    # mapper = {treatment_branch: treatment_num for treatment_branch, treatment_num in zip(treatment_order, [str(0), str(1), str(2)]) }
    
    df.loc[:, "TreatmentNumber"] = df.loc[:, "TreatmentBranch"].replace(mapper)
    return df

def add_recordinghemisphere_column_based_on_channel(df):
    for hemisphere in ["left", "right"]:        
        mask = df["Channel"].str.lower().str.contains(hemisphere)
        df.loc[mask, "RecordingHemisphere"] = hemisphere
    return df

def add_treatmentorder_column(df, treatment_order_from_obj:str):
    """Add a treatment order column
    
    Args:
      treatment_order_from_obj (str): The treatment order to check against.
    """
    treatment_order = df.sort_values(by="FirstPacketDateTime").TreatmentBranch.unique().tolist()  # Does NOT sort, according to documentation
    treatment_order = ",".join(treatment_order)
    
    if treatment_order != treatment_order_from_obj:
        raise ValueError(
            f"Provided treatment order does not match the treatment order found in the dataframe. "
            f"Provided: {treatment_order_from_obj}; From Dataframe: {treatment_order}"
        )
    
    df.loc[:, "TreatmentOrder"] = treatment_order
    return df

def add_ipsicontra_column(df):

    mask_is_ipsi = df.StimGloveHand == df.RecordingHemisphere
    mapper = {
        True: str( constants.LateralSide.IPSILATERAL ), 
        False: str( constants.LateralSide.CONTRALATERAL ),
    }
    df.loc[:, "IpsiContra"] = mask_is_ipsi.replace(mapper)
    return df

def add_column_PSD(df, freq_range):
    """Medtronic hardware has builtin filter of 1-100hz. Check documentation."""
   
    dest_colname = f"PSD_{freq_range}"
    sampling_freq = get_sampling_freq(df)
    
    filter_processor = BandpassFilterProcessor(
        freq_range = freq_range, 
        sampling_freq = sampling_freq,
    )

    psd_processor = PowerSpectralDensityProcessor(
        sampling_freq = sampling_freq,
    )

    def lambda_pipeline(signal):
        signal = np.array(signal)
        signal = filter_processor(signal)
        result = psd_processor(signal).filter_freq_range(freq_range=freq_range)
        return result

    df.loc[:, dest_colname] = df.apply(
        lambda row: lambda_pipeline(row.TimeDomainData),
        axis=1,
    )

    return df

def add_column_PSD_Baseline_InterTreatment(df):

    medtronic_range = FrequencyRange.MedtronicPerceptRange.value
    psd_colname = f"PSD_{medtronic_range}"
    dest_colname = f"PSD_Baseline_InterTreatment_{medtronic_range}"
    groupby_colnames = [
        "PatientNumber",
        "Channel",
        "RecordingHemisphere",
        "StimGloveHand",
        "IpsiContra",
    ]

    df_baseline = (
        df
        .query(f"TreatmentBranch == '{str(constants.TreatmentStage.DBS_OFF)}'")
        .sort_values("FirstPacketDateTime", ascending=True)
        .groupby(by=groupby_colnames)
        .tail(3)
        .groupby(by=groupby_colnames)[[psd_colname]]
        .agg(lambda series: np.mean(series.to_numpy()))
        .rename({psd_colname: dest_colname}, axis="columns")
        .reset_index(drop=False)
    )

    df_merged = df.merge(
        df_baseline, 
        how = "left",
        on = groupby_colnames,
        sort=False, 
        suffixes = ('_og', '_baseline'),
        validate = "many_to_one",
    )

    return df_merged

def add_column_PSD_Baseline_IntraTreatment(df):

    medtronic_range = FrequencyRange.MedtronicPerceptRange.value
    psd_colname = f"PSD_{medtronic_range}"
    dest_colname = f"PSD_Baseline_IntraTreatment_{medtronic_range}"
    groupby_colname = [
        "PatientNumber", 
        "Channel", 
        "TreatmentBranch",
    ]

    df_intratreatment_baseline = (
        df
        .groupby(groupby_colname)
            .nth(range(3))

        .groupby(groupby_colname)
            .apply(lambda row: np.mean(row[psd_colname].to_numpy()), include_groups=False)
            
        .rename(dest_colname)
        .reset_index()
        
    )

    df_new = df.merge(
        df_intratreatment_baseline, 
        'left', 
        groupby_colname,
        validate="many_to_one",
    )

    return df_new

def add_column_PowerMean(df, freq_range):
    """Add the mean power of the specified freq band.
    
    The mean power is calculated as the mean of a filtered PSD. The PSD of the
    range (1, 100) inclusive is filtered by the specified freq_range and then
    a mean power within this range is calculated.
    """
    
    medtronic_range = FrequencyRange.MedtronicPerceptRange.value
    dest_colname = f"PowerMean_{freq_range}" 
    src_colnme = f"PSD_{medtronic_range}"
    
    df.loc[:, dest_colname] = (
        df[src_colnme]
        .apply(lambda cell: np.mean(cell.filter_freq_range(freq_range)))
    )
    
    return df

def add_column_PowerMean_Baseline_InterTreatment(df, freq_range):
    
    medtronic_range = FrequencyRange.MedtronicPerceptRange.value
    dest_colname = f"PowerMean_Baseline_InterTreatment_{freq_range}"
    src_colname = f"PSD_Baseline_InterTreatment_{medtronic_range}"
    
    df.loc[:, dest_colname] = (
        df[src_colname]
        .apply(lambda cell: np.mean(cell.filter_freq_range(freq_range)))
    )

    return df

def add_column_PowerMean_PercentageChange_InterTreatment(df, freq_range):

    dest_colname = f"PowerMean_PercentageChange_InterTreatment_{freq_range}"
    src_colname = f"PowerMean_{freq_range}"
    baseline_colname = f"PowerMean_Baseline_InterTreatment_{freq_range}"
    
    df.loc[:, dest_colname] = (
        (df[src_colname] - df[baseline_colname])
        / df[baseline_colname]
        * 100
    )

    return df

def add_column_PowerMean_Baseline_IntraTreatment(df, freq_range):

    medtronic_range = FrequencyRange.MedtronicPerceptRange.value
    dest_colname = f"PowerMean_Baseline_IntraTreatment_{freq_range}"
    src_colname = f"PSD_Baseline_IntraTreatment_{medtronic_range}"
    
    
    df.loc[:, dest_colname] = (
        df[src_colname]
        .apply(lambda cell: np.mean( cell.filter_freq_range(freq_range) ))
    )
    return df

def add_column_PowerMean_PercentageChange_IntraTreatment(df, freq_range):
    
    dest_colname = f"PowerMean_PercentageChange_IntraTreatment_{freq_range}"
    src_colname = f"PowerMean_{freq_range}"
    baseline_colname = f"PowerMean_Baseline_IntraTreatment_{freq_range}"
    
    df.loc[:, dest_colname] = (
        (df[src_colname] - df[baseline_colname])
        / df[baseline_colname]
        * 100
    )
    
    return df

# def add_burst_detection_column(df): 
#     # TODO: Create a burst object that makes plotting the burst easier
#     freq_ranges = [
#         FrequencyRange.LowBeta.value,
#         FrequencyRange.HighBeta.value,
#         FrequencyRange.Beta.value,
#     ]
#     dual_threshold = (1, 1.3)  # TODO: Justify this threshold
#     magnitude_type = "power"
#     sampling_freq = get_sampling_freq(df)
    
#     def lambda_func_burst(signal, freq_range, sampling_freq):
        
#         bandpass_filter_processor = BandpassFilterProcessor(
#             freq_range = freq_range, 
#             sampling_freq = sampling_freq,
#         )
        
#         signal = np.array(signal)
#         signal = bandpass_filter_processor(signal)
        
#         burst_indicator = detect_bursts_dual_threshold(
#             sig = signal, 
#             fs = sampling_freq, 
#             dual_thresh = dual_threshold,
#             f_range = freq_range,
#             magnitude_type = magnitude_type,
#             avg_type = "mean"
#         )

#         return {
#             "signal": signal,
#             "burst_indicator": burst_indicator,
#         }

#     def lambda_func_burst_stat(burst_detection_dict, sampling_freq):
#         return compute_burst_stats(bursting=burst_detection_dict["burst_indicator"], fs=sampling_freq)
    
#     for freq_range in freq_ranges:
#         df.loc[:, f"Burst_detection_{freq_range}"] = df.loc[:, "TimeDomainData"].apply(lambda signal: lambda_func_burst(signal, freq_range, sampling_freq))
#         df.loc[:, f"Burst_stats_{freq_range}"] = df.loc[:, f"Burst_detection_{freq_range}"].apply(lambda value: lambda_func_burst_stat(value, sampling_freq))
    
#     return df

def add_column_burst_detection_array_and_stats(df, freq_range):
    
    sampling_freq = get_sampling_freq(df)
    burst_threshold_percentile = 75
    min_burst_duration_ms = 100 # milisecond

    def lambda_pipeline(signal):
        
        result = detect_burst_tinkhauser_2017(
            signal = signal,
            freq_range=freq_range,
            sampling_freq=sampling_freq,
            burst_threshold_percentile=burst_threshold_percentile,
            min_burst_duration_ms=min_burst_duration_ms
        )
        return result 

    def lambda_pipeline_stat(burst_detection):
        result = calculate_burst_statistics(burst_detection_array=burst_detection, sampling_freq=sampling_freq)
        return result

    dest_colname = f"Burst_Detection_{freq_range}_{burst_threshold_percentile}_Percentile_{min_burst_duration_ms}_MinDuration"
    dest_colname_stat = f"Burst_Statistics_{freq_range}_{burst_threshold_percentile}_Percentile_{min_burst_duration_ms}_MinDuration"
    
    df.loc[:, dest_colname] = df["TimeDomainData"].apply(lambda signal: lambda_pipeline(signal))
    df.loc[:, dest_colname_stat] = df.loc[:, dest_colname].apply(lambda burst_detection: lambda_pipeline_stat(burst_detection))
        
    return df


def reorder_columns(df):

    first_few_colnames = [
    'PatientNumber',
    'FirstPacketDateTime',
    'Channel',
    'TreatmentBranch',
    'StimGloveHand',
    'TreatmentOrder',
    'RecordingHemisphere',
    'IpsiContra',
    ]
    
    colnames = df.columns.to_list()
    
    for colname in first_few_colnames:
        search_result = np.where(np.array(colnames) == colname)[0]
        assert len(search_result) < 2, f"Found more than one column for {colname}"
        assert len(search_result) > 0, f"Found no {colname}"
        
        colnames.pop(search_result[0])

    desired_colname_order = first_few_colnames + colnames
    
    return df[desired_colname_order]

def create_tick_array(packet_size_array, packet_tick_array):
    """Expand ticks in ms using array of packet sizes and array of Percept hardware ticks
    
    The packet sequence number, packet sizes, and global ticks in ms 
    (50 ms resolution) are recorded by the Medtronic Percept for each data
    packet. This function expands the ticks labeled for each packet to each 
    data point by aligning the timestamp and tick to the last data point of each
    packet (further details is laid out on p.28 of the Medtronic Percept white 
    paper found in the Medtronic Academy portal.)
    
    Because the "TicksInMses" has 50 ms resolution and each packet has a global
    tick duration of 250 ms the 250 hz sampling rate results in 62.5 data points
    per packet. Because it does not make sense to split a single data point, the
    0.5 is shifted to one of the packet before or after result in the packet
    sizes to be 63, 62, 63, 62, etc. Thus, to properly align the ticks for each
    data points, the ticks for packets of size 62 are shifted by 2 ms.
    
    P.S., the notes on p.28 of the white paper seems to have quite a few typo
    and thus is incomplete. However, the following interpretation seems to make
    the most sense.
    
    """

    assert len(packet_size_array) == len(packet_tick_array)
    
    prev_idx = 0
    sampling_freq_hz = 250
    sampling_period_ms = int( 1000/sampling_freq_hz )
    packet_count = len(packet_size_array)
    output_size = np.sum(packet_size_array)
    result = np.empty(output_size, dtype=np.int32)
    
    for packet_idx in range(packet_count):

        size = np.flip(packet_size_array)[packet_idx]
        tick = np.flip(packet_tick_array)[packet_idx]

        full_tick_array = np.arange(tick, tick-size*sampling_period_ms, -sampling_period_ms)
        
        if size == 62:  # Shift 2 ms to align properly (see docstring for details)
            full_tick_array -= 2
        
        result[prev_idx:prev_idx+size] = full_tick_array
        
        prev_idx += size

    result -= result.min()
    result = np.flip(result).copy()
    
    return result

def create_datetime_array(first_packet_datetime, packet_size_array, packet_tick_array): 
    """Create an array of datetiem object aligning with the time domain data points
    
    This function finds the datetime object of the very first data point and
    then use the tick array to offset the ticks of each data point thus creating
    the final array of datetime object.
    
    """
    
    output_size = np.sum(packet_size_array)
    result = np.empty(output_size, dtype=datetime)
    first_packet_size = packet_size_array[0]
    sampling_rate_hz = 250
    sampling_period_ms = int(1000 / sampling_rate_hz)

    first_packet_datetime = first_packet_datetime.astimezone(tz=timezone.utc)
    first_data_point_datetime = first_packet_datetime - timedelta(milliseconds=sampling_period_ms) * (first_packet_size-1)
    
    tick_array = create_tick_array(packet_size_array, packet_tick_array)
    
    result = first_data_point_datetime + np.array( [timedelta(milliseconds=tick.item()) for tick in tick_array] )
    
    return result

def create_xarray(df_row_tuple):
    """Creates an Xarray of the LFP data points with timestamp
    
    The Xarray datastructure is convenient for working with data in more
    efficient format and labeled with metadata.
    
    The first few packets of the LFP data have more than 63x data points thus
    causing certain data points to overlap in timestamp or ticks. There is no 
    clear guidance from Medtronic's Percept whitepaper in how to resolve such
    overlap issue. See the Medtronic Percept whitepaper p.28 for more details.
    
    """
    
    time_domain_data = getattr(df_row_tuple, "TimeDomainData")
    first_packet_datetime = getattr(df_row_tuple, "FirstPacketDateTime")
    packet_size_array = np.fromstring(
        getattr(df_row_tuple, "GlobalPacketSizes"), 
        dtype=int, 
        sep=','
    )
    packet_tick_array = np.fromstring(
        getattr(df_row_tuple, "TicksInMses"), 
        dtype=np.int32, 
        sep=','
    )
    
    datetime_array = create_datetime_array(
        first_packet_datetime, 
        packet_size_array, 
        packet_tick_array,
    )
    tick_array = create_tick_array(packet_size_array, packet_tick_array)
    
    
    xr_result = xr.DataArray(
        data = time_domain_data,
        dims = "time",
        coords = {
            "time": datetime_array,
        },
        attrs={
            "name": "LFP_TimeDomainData",
            "unit": "microvolt (µV)",
        },
    )
    
    # Add a non-dimension coordinate
    xr_result.coords['tick'] = ("time", tick_array, {"name": "tick_in_ms"})
    
    return xr_result


def add_column_of_xarray_lfp_data(df):
    
    column_holder = []
    
    for named_tuple in df.itertuples():
        xr_result = create_xarray(named_tuple)
        column_holder.append(xr_result)
        
    df["TimeDomainData_Xarray"] = column_holder
    
    return df