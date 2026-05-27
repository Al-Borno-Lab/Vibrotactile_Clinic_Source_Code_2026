# Plots for each patient's data
#
# Plotting functions are separated to ones that plot just a single patient and 
# ones that plots multiple patients at the same time.

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from ...utility.constants import FrequencyRange
from ...utility.stats import get_stat_test_string, wilcoxon_ind, ttest_ind, anova_test
from scipy.stats import f_oneway
import inspect
from ...data_wrapper.base import PatientObjAbstractBase
from ...utility import constants
import logging

logger = logging.getLogger(__name__)

# TODO: Update this plotting function to take a patient object instead of a dataframe. Since I cannot guarantee the dataframe columns.
# TODO: Check if this function work and add to plot_registry
def plot_per_patient_power_mean_percentage_change(df, freq_range):
    nrows, ncols, inches, aspect = 3, 2, 5, 1.3
    sns.set_context("paper")
    sns.set_style("whitegrid")
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols * inches * aspect, nrows * inches), sharey=True)
    fig.suptitle(f"Patient {df.PatientNumber[0]}")
    fig.text(1, 1, s=inspect.currentframe().f_code.co_name, alpha=0.3, ha="right")
    axs = axs.flatten()

    ax = axs[0]

    for ax, ipsi_contra, y_colname in zip(
        axs[:2], ["ipsi", "contra"], [f"PowerMean_PercentageChange_{freq_range}", f"PowerMean_PercentageChange_{freq_range}"]
    ):
        ax.set_title(f"{ipsi_contra.upper()}-PowerMean_PercentageChange_{freq_range}")
        df_filtered = df.query(f"IpsiContra == '{ipsi_contra}'")

        if df_filtered.shape[0] == 0:
            continue

        sns.scatterplot(
            data=df_filtered,
            x="FirstPacketDateTime",
            y=y_colname,
            hue="TreatmentBranch",
            ax=ax,
        )
        sns.lineplot(
            data=df_filtered,
            x="FirstPacketDateTime",
            y=y_colname,
            hue="TreatmentBranch",
            ax=ax,
        )

    for ax, ipsi_contra, y_colname in zip(
        axs[2:], ["ipsi", "contra"], [f"PowerMean_PercentageChange_{freq_range}", f"PowerMean_PercentageChange_{freq_range}"]
    ):
        ax.set_title(f"{ipsi_contra.upper()}-PowerMean_PercentageChange_{freq_range}")
        df_filtered = df.query(f"IpsiContra == '{ipsi_contra}'")

        if df_filtered.shape[0] == 0:
            continue

        sns.violinplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            hue="TreatmentBranch",
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            inner=None,
            alpha=0.3,
            ax=ax,
        )
        sns.boxplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            hue="TreatmentBranch",
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            width=0.4,
            ax=ax,
        )
        sns.swarmplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            color="tab:cyan",
            ax=ax,
        )
        sns.pointplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            color="tab:red",
            ax=ax,
            errorbar="sd",
        )

        data_list = df_filtered.groupby(by=["TreatmentBranch"])[y_colname].apply(list).to_dict().values()
        text_str = anova_test(data_list=data_list)
        ax.text(x=0, y=-0.2, s=text_str, transform=ax.transAxes)
        text_str = get_stat_test_string(
            df_filtered.groupby(by=["TreatmentBranch"])[y_colname].apply(list).to_dict(), stat_test_func=wilcoxon_ind
        )
        ax.text(x=0, y=-0.4, s=text_str, transform=ax.transAxes)

    for ax, ipsi_contra, y_colname in zip(
        axs[4:], ["ipsi", "contra"], [f"PowerMean_PercentageChange_{freq_range}", f"PowerMean_PercentageChange_{freq_range}"]
    ):
        ax.set_title(
            f"{ipsi_contra.upper()}-PowerMean_PercentageChange_{freq_range}\n(Baseline: Session 4-6)   (Treatment: Session 10-12)"
        )
        df_filtered_dbs_off = (
            df.query(f"IpsiContra == '{ipsi_contra}'")
            .query(f"TreatmentBranch == 'dbs_off'")
            .groupby("TreatmentBranch")
            .nth(range(3, 6))
        )
        df_filtered_treatment = (
            df.query(f"IpsiContra == '{ipsi_contra}'")
            .query(f"TreatmentBranch != 'dbs_off'")
            .groupby("TreatmentBranch")
            .nth(range(9, 12))
        )
        df_filtered = pd.concat([df_filtered_dbs_off, df_filtered_treatment], axis=0)

        if df_filtered.shape[0] == 0:
            continue

        sns.violinplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            hue="TreatmentBranch",
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            inner=None,
            alpha=0.3,
            ax=ax,
        )
        sns.boxplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            hue="TreatmentBranch",
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            width=0.4,
            ax=ax,
        )
        sns.swarmplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            color="tab:cyan",
            ax=ax,
        )
        sns.pointplot(
            data=df_filtered,
            x="TreatmentBranch",
            y=y_colname,
            order=df_filtered.TreatmentOrder.iloc[0].split(","),
            color="tab:red",
            ax=ax,
            errorbar="sd",
        )

        data_list = df_filtered.groupby(by=["TreatmentBranch"])[y_colname].apply(list).to_dict().values()
        text_str = anova_test(data_list=data_list)
        ax.text(x=0, y=-0.2, s=text_str, transform=ax.transAxes)
        text_str = get_stat_test_string(
            df_filtered.groupby(by=["TreatmentBranch"])[y_colname].apply(list).to_dict(), stat_test_func=wilcoxon_ind
        )
        ax.text(x=0, y=-0.4, s=text_str, transform=ax.transAxes)

    fig.set_layout_engine("constrained")

    return fig

# TODO: Check if this function work and add to plot_registry
def plot_lfp_psd_profile_from_groups(pt_obj: PatientObjAbstractBase):
    """Plots the BrainSense setup LFP PSD results using data from 'Groups'
    
    This plotting function is built for patient 1 but generalized to any
    
    """
    
    delimiter_old = "."
    delimiter_new = "_"
    
    colname_freq = "SensingSetup.ChannelSignalResult.SignalFrequencies".replace(delimiter_old, delimiter_new)
    colname_psd = "SensingSetup.ChannelSignalResult.SignalPsdValues".replace(delimiter_old, delimiter_new)
    colname_artifact = "SensingSetup.ChannelSignalResult.ArtifactStatus".replace(delimiter_old, delimiter_new)
    colname_initialFinal = "InitialOrFinalState"
    colname_group = "GroupId"
    colname_channel = "SensingSetup.ChannelSignalResult.Channel".replace(delimiter_old, delimiter_new)
    colnames_dupe_check = [
        colname_initialFinal,
        colname_group,
        colname_channel,
    ]
    colnames_to_keep = [
        colname_channel, 
        colname_artifact,
        colname_freq, 
        colname_psd,
    ]
    
    df = pt_obj.get_dataframe_brainSenseSetup_groups()
    colname_mapper = {old_colname: old_colname.replace(delimiter_old, delimiter_new) for old_colname in df.columns}
    df = df.rename(colname_mapper, axis=1)
    df = df.drop_duplicates(colnames_dupe_check, ignore_index=True)

    mask_row_final_only = df.loc[:, colname_initialFinal] == df.loc[:, colname_initialFinal].unique()[0]
    df = df.loc[mask_row_final_only, colnames_to_keep]

    df.loc[:, colname_channel] = df.loc[:, colname_channel].apply(lambda cell: cell.split(".")[-1])
    df.loc[:, colname_artifact] = df.loc[:, colname_artifact].apply(lambda cell: cell.split(".")[-1])

    nrows, ncols, inches, xyratio = 1, 1, 5, 2
    fig, ax = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))
    
    for row_tuple in df.itertuples():
        channel = getattr(row_tuple, colname_channel)
        artifact = getattr(row_tuple, colname_artifact)
        freq = getattr(row_tuple, colname_freq)
        psd = getattr(row_tuple, colname_psd)

        for enum_item in constants.PlotColorHemisphere:
            hemi = enum_item.name.lower()
            if hemi in channel.lower():
                color = enum_item.value.lower()

        ax.set_title(f"Patient_{pt_obj.patient_num} BrainSense setup Check Results")
        ax.set_xlabel("Freq (Hz)")
        ax.set_ylabel("PSD (μVp)")
        ax.scatter(freq, psd, label=f"{channel} - {artifact}", marker=".", c=color, s=8)
        ax.plot(freq, psd, c=color, alpha=.15)
        ax.legend()
        
    return fig
    

# TODO: Check if this function work and add to plot_registry
def plot_lfp_psd_profile_from_brainSenseSetup_psd(pt_obj: PatientObjAbstractBase):
    """Plot the LFP PSD gathered from BrainSense setup stored under 'MostRecentInSessionSignalCheck
    
    This function plots the data stored under the 'MostRecentInSessionSignalCheck'
    key and contrasts the plotting function that uses data stored in 'Groups'.
    
    All patients but patient 1 have data stored in 'MostRecentInSessionSignalCheck'
    thus all but patient 1 can use this function to create a plot for the LFP
    PSD gathered during the BrainSense setup step.
    
    """
    colname_channel = "Channel"
    colname_artifact = "ArtifactStatus"
    colname_freq = "SignalFrequencies"
    colname_psd = "SignalPsdValues"
    
    df = pt_obj.get_dataframe_brainSenseSetup_psd()

    nrows, ncols, inches, xyratio = 1, 1, 5, 2
    fig, ax = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))

    for tuple_row in df.itertuples():
        channel = getattr(tuple_row, colname_channel)
        artifact = getattr(tuple_row, colname_artifact)
        freq = getattr(tuple_row, colname_freq)
        psd = getattr(tuple_row, colname_psd)

        # for enum_item in constants.PlotColorHemisphere:
        #     hemi = enum_item.name.lower()
        #     if hemi in channel.lower():
        #         color = enum_item.value.lower()

        ax.set_title(f"Patient_{pt_obj.patient_num} BrainSense setup Check Results")
        ax.set_xlabel("Freq (Hz)")
        ax.set_ylabel("PSD (μVp)")
        ax.scatter(freq, psd, label=f"{channel} - {artifact}", marker=".", s=8)
        # ax.scatter(freq, psd, label=f"{channel} - {artifact}", marker=".", c=color, s=8)
        ax.plot(freq, psd, alpha=.15)
        # ax.plot(freq, psd, c=color, alpha=.15)
        ax.legend()

    return fig

# TODO: Check if this function work and add to plot_registry
def plot_lfp_psd(pt_obj: PatientObjAbstractBase):
    """Convenience function to call the best plotting function for the PSD gathered during BrainSense setup
    
    This function codifies the logic of which patient number uses which plotting
    function since they use different functions to extract the data from their
    JSON files.
    """
    
    pt_num_groups = [1, ]
    pt_num_mostRecent = [idx for idx in range(2, 14) if idx != 6]
    
    if pt_obj.patient_num in pt_num_groups:
        fig = plot_lfp_psd_profile_from_groups(pt_obj)
    elif pt_obj.patient_num in pt_num_mostRecent:
        fig = plot_lfp_psd_profile_from_brainSenseSetup_psd(pt_obj)
        
    return fig


## TODO: Check that all the commented section below works and fix them.
# import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
# from . import IndividualPlotter
# import pandas as pd
# import numpy as np
# from ..signal_analyzer.psd import FrequencyRangePSDBaselineAnalyzer
# from ..utility import constants
# from ..data_wrapper.base import Patient_Dataset_Base
# import matplotlib.pyplot as plt
# from matplotlib import ticker
# from ..utility.constants import (
#     COLOR_LEFT_HEMISPHERE,
#     COLOR_RIGHT_HEMISPHERE,
#     BIOMARKER_BANDS_FASANO_2024,
# )
# from matplotlib.axes import Axes
# from ..signal_processor.filter_support import IIR_butterworth_filter_hammer_2022
# from ..signal_processor.psd_support import psd_welch_contaldi_2023
# import numpy.typing as npt
# import numpy as np
# from matplotlib import patches
# from ..old_plotter import IndividualPlotter
# import logging
# from MedtronicPerceptAnalysisTool.data_wrapper.base import Patient_Dataset_Base as BasePatientObject
# from MedtronicPerceptAnalysisTool.signal_analyzer.psd import FrequencyRangeNormalizedPSDAnalyzer
# import itertools
# from ..signal_analyzer import psd
# from ..utility import constants

# # def get_treatment_order(patient_obj:BasePatientObject):
# #     result = (
# #         patient_obj
# #         .get_dataframe()
# #         .sort_values(by="FirstPacketDateTime")
# #         .loc[:, "TreatmentBranch"]
# #         .unique()
# #     )
# #     return result
    

# # logger = logging.getLogger(__name__)


# @IndividualPlotter.register
# def plot_baseline_psd_profile_of_each_channel(pt_data_obj):

#     def plot_baseline_psd(baseline_psd: pd.DataFrame):
#         mosaic_names = np.array([["left", "right"]])
#         nrows, ncols, inches, xyratio = 1, mosaic_names.shape[1], 3, 2
#         fig, axs = plt.subplot_mosaic(
#             mosaic=mosaic_names,
#             figsize=(ncols * inches * xyratio, nrows * inches),
#             sharex=True,
#             sharey=True,
#         )

#         for row in baseline_psd.itertuples():

#             if "left" in row.Channel.lower():
#                 ax = axs["left"]
#             if "right" in row.Channel.lower():
#                 ax = axs["right"]

#             ax.set_title(f"Baseline PSD Profile for {row.Channel}")
#             ax.set_ylabel("PSD")
#             ax.set_xlabel("Freq (Hz)")

#             freq, psd = row[-1]
#             ax.scatter(freq, psd, label=row.Channel, marker=".", s=2, color="red")
#             ax.plot(freq, psd, alpha=0.3, color="grey")

#         return fig

#     analyzer = FrequencyRangePSDBaselineAnalyzer(
#         freq_range=constants.FrequencyRange.MedtronicPerceptRange.value,
#     )
#     df_intermediary = analyzer(patient_obj=pt_data_obj)
#     fig = plot_baseline_psd(df_intermediary)

#     patient_prefix = "-".join(pt_data_obj.__class__.__name__.split("_")[:2])
#     fig.suptitle(f"{patient_prefix} - Baseline PSD profile for each channel")

#     fig.set_layout_engine("constrained")

#     return fig


# @IndividualPlotter.register
# def plot_recording_sessions_seconds(pt_data_obj: Patient_Dataset_Base):
#     """Convenience function to plot the summary of a patient's dataset"""
#     # TODO: Add function name to top-right of figure with alpha = 0.5

#     obj = pt_data_obj
#     df = obj.get_dataframe()
#     sampling_rate = 250

#     treatment_order = df.loc[0, "TreatmentOrder"].split(sep=",")
#     channels = df.loc[:, "Channel"].unique()
#     df = df.loc[
#         :, ["Channel", "FirstPacketDateTime", "TreatmentBranch", "TimeDomainData"]
#     ]
#     df = df.set_index(["TreatmentBranch", "Channel", "FirstPacketDateTime"])

#     nrows, ncols, inches, xyratio = 1, 3, 5, 1.3
#     fig, axs = plt.subplot_mosaic(
#         mosaic=[treatment_order],
#         gridspec_kw=dict(width_ratios=[1, 2, 2]),
#         layout="constrained",
#         figsize=(ncols * inches * xyratio, nrows * inches),
#         sharey=True,
#     )

#     session_count_offset = 0

#     for treatment in treatment_order:
#         max_session_count = 0
#         ax: Axes = axs[treatment]
#         for channel in channels:

#             # Determine color
#             match channel.split("_")[-1].upper():
#                 case "LEFT":
#                     color = COLOR_LEFT_HEMISPHERE
#                 case "RIGHT":
#                     color = COLOR_RIGHT_HEMISPHERE
#                 case _:
#                     raise ValueError(
#                         f"Expect LEFT/RIGHT, got {channel.split('_')[-1].upper()}"
#                     )

#             # Extract data
#             df_temp = df.loc[(treatment, channel, slice(None))].sort_index(level=2)
#             sample_counts = df_temp.apply(
#                 func=lambda row: len(row["TimeDomainData"]), axis=1
#             )
#             session_durations = sample_counts / sampling_rate
#             session_count = len(session_durations)
#             if session_count > max_session_count:
#                 max_session_count = session_count

#             # Plot
#             x = range(session_count_offset, session_count_offset + max_session_count)
#             y = session_durations
#             label = channel
#             ax.bar(x=x, height=y, label=label, alpha=0.3, color=color)
#             ax.legend()
#             ax.xaxis.set_major_locator(ticker.FixedLocator(x))

#         session_count_offset += max_session_count
#         ax.set_title(treatment.upper())
#         ax.set_title(f"{treatment.upper()} Session durations")
#         ax.set_xlabel("Recording Session")
#         ax.set_ylabel("Duration (sec)")

#     fig_title = "_".join(obj.__class__.__name__.split("_")[:2])
#     fig.suptitle(fig_title)

#     return fig



# @IndividualPlotter.register
# def plot_mean_beta_time_series(pt_data_obj: Patient_Dataset_Base):

#     def get_treatment_order(patient_df) -> list:
#         # result = patient_df.TreatmentOrder.iloc[0].split(',')
#         result = patient_df.sort_values("FirstPacketDateTime").TreatmentBranch.unique()
#         result = [item.upper() for item in result]
#         return result

#     def find_target_colname(
#         patient_df: pd.DataFrame, search_term: str = "PSDMean"
#     ) -> str:
#         assert isinstance(search_term, str), f"`search_term` has to be a str."

#         found = [colname for colname in patient_df.columns if search_term in colname]
#         assert len(found) != 0, f"Did not find any match of colname with 'PSDMean'"
#         assert len(found) == 1, f"Found multiple match of colname with 'PSDMean'"

#         return found[0]

#     freq_range = constants.FrequencyRange.Beta.value
#     analyzer = psd.FrequencyRangePSDMeanAnalyzer(freq_range=freq_range)
#     df = analyzer(patient_obj=pt_data_obj)
#     grouped = analyzer(patient_obj=pt_data_obj).groupby(
#         by=["TreatmentBranch", "Channel"]
#     )[find_target_colname(df)]

#     mosaic_layout = np.array(get_treatment_order(df))[np.newaxis, :]
#     nrows, ncols, inches, xyratio = 1, mosaic_layout.shape[1], 5, 1.3
#     fig, axs = plt.subplot_mosaic(
#         mosaic=mosaic_layout,
#         gridspec_kw=dict(width_ratios=[1, 2, 2]),
#         layout="constrained",
#         figsize=(ncols * inches * xyratio, nrows * inches),
#         sharey=True,
#     )

#     for (treatment, channel), group_df in grouped:
#         hemisphere = channel.split("_")[-1].upper()
#         color = constants.PlotColorHemisphere[f"{hemisphere}"].value
#         ax = axs[treatment.upper()]
#         y = group_df.to_numpy()
#         x = range(len(y))
#         ax.plot(x, y, color=color)
#         ax.bar(x, y, color=color, label=channel, alpha=0.1)
#         ax.set_xlabel(treatment.upper())
#         ax.legend()
#         ax.xaxis.set_major_locator(ticker.FixedLocator(x))

#     fig.suptitle(
#         f"{pt_data_obj.__class__.__name__} Beta PSD Mean | Glove Hand: {pt_data_obj.glove_hand} | Treatment Order: {get_treatment_order(df)}"
#     )
#     fig.set_layout_engine("constrained")

#     return fig

# @IndividualPlotter.register
# def plot_mean_beta_psd_normalized(patient_obj: BasePatientObject):
#     result_colname = "RESULT"
#     combo = [ str(list(item)) for item in itertools.product(['left', 'right'], get_treatment_order(patient_obj)) ]
#     mosaic_layout = np.array( [combo] )
#     #logger.info(mosaic_layout)
#     nrows, ncols, inches, xyratio = 1, mosaic_layout.shape[1], 4, 1.5
#     fig, axd = plt.subplot_mosaic(
#         mosaic=mosaic_layout,
#         sharey=True,
#         figsize=(ncols*inches*xyratio, nrows*inches),
#         gridspec_kw={"width_ratios": [1, 2, 2, 1, 2, 2]}
#     )

#     freq_ranges = [
#         constants.FrequencyRange.LowBeta.value,
#         constants.FrequencyRange.HighBeta.value,
#         constants.FrequencyRange.Beta.value,
#     ]

#     for freq_range in freq_ranges:
#         analyzer = FrequencyRangeNormalizedPSDAnalyzer(
#             freq_range=freq_range,
#             last_n_sessions=3,
#             dest_colname=result_colname,
#         )
#         df = analyzer(patient_obj=patient_obj)
#         df[result_colname] = df[result_colname].apply(lambda cell: np.mean(cell))
#         grouped = df.groupby(by=["PatientNumber", "Channel", "TreatmentBranch"])
        
#         for (patient_number, channel, treatment), grouped_data in grouped:
#             hemi = channel.lower().split('_')[-1]
#             ax = axd[str([hemi, treatment])]
#             y = grouped_data[result_colname].to_numpy()
#             x = range(len(y))

#             ax.bar(x, y, alpha=0.2, label=str(freq_range))
#             ax.plot(x, y)
#             ax.set_xlim(0, len(x))


#             # ax.legend()
#             ax.set_title(channel)
    
#     ax.legend()
#     fig.suptitle(f"{patient_obj.__class__.__name__} Baseline Normalized PSD Mean")
#     return fig