from pathlib import Path
import numpy as np
import pandas as pd
import json
from typing import Dict
from MedtronicPerceptAnalysisTool.utility.constants import PROTOCOL_STAGES

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
    
    assert isinstance(df["FirstPacketDateTime"].iloc[0], datetime), f"The `FirstPacketDateTime` column is not in `datetime` format."

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
    mask_normal_treatmentbranches = df.TreatmentBranch.isin(PROTOCOL_STAGES)
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
    
    df.loc[:, "TreatmentNumber"] = df.loc[:, "TreatmentBranch"].replace(mapper)
    return df

def add_recordinghemisphere_column_based_on_channel(df):
    for hemisphere in ["left", "right"]:        
        mask = df["Channel"].str.lower().str.contains(hemisphere)
        df.loc[mask, "RecordingHemisphere"] = hemisphere
    return df

def add_treatmentorder_column(df):
    treatment_order = df.sort_values(by="FirstPacketDateTime").TreatmentBranch.unique().tolist()  # Does NOT sort, according to documentation
    df.loc[:, "TreatmentOrder"] = ",".join(treatment_order)
    return df

def add_ipsicontra_column(df):
    ipsicontra_mask = df.StimGloveHand == df.RecordingHemisphere
    df.loc[:, "IpsiContra"] = ipsicontra_mask.replace({True: "ipsi", False: "contra"})
    return df

from MedtronicPerceptAnalysisTool.signal_processor.filter import BandpassFilterProcessor
from MedtronicPerceptAnalysisTool.signal_processor.psd import PowerSpectralDensityProcessor
from MedtronicPerceptAnalysisTool.utility.constants import FrequencyRange
from .utility import get_sampling_freq

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
        .query("TreatmentBranch == 'dbs_off'")
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
from ..signal_processor.burst import detect_burst_tinkhauser_2017, calculate_burst_statistics
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