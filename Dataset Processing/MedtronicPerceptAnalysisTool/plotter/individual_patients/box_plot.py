from ...data_wrapper.base import Patient_Dataset_Base
import matplotlib.pyplot as plt
from ...utility.constants import BIOMARKER_BANDS_FASANO_2024
import scipy as scp
import typing
import pandas as pd
import itertools
import numpy as np
from ..plotter import IndividualPlotter
from MedtronicPerceptAnalysisTool.signal_processor.filter import BandpassFilterProcessor
from MedtronicPerceptAnalysisTool.signal_processor.psd import PowerSpectralDensityProcessor
from MedtronicPerceptAnalysisTool.signal_processor.psd import PowerSpectralDensity
import logging
from MedtronicPerceptAnalysisTool.utility.stats import ttest

# TOOD: First-order boxplot (not normalized) - plot 4 - Later, these are the cross patient plots
# TODO: First-order boxplot (normalized) - plot 5 - Later, these are the cross patient plots
# TODO: Box plot for per patient (not normalized) with jitter to show diff between treatments
# TODO: Box plot for per patient (normalized) with jitter to show diff between treatments

SAMPLING_FREQUENCY = 250

logger = logging.getLogger(__name__)

def last_3_session_mean_psd_and_pvalue(pt_data_obj: Patient_Dataset_Base, freqRange: typing.Tuple):

    # Integrity check
    assert isinstance(freqRange, tuple), f"'freqRange' type has to be tuple, got {type(freqRange)} instead."
    assert len(freqRange) == 2, f"Length of tuple has to be 2, got {len(freqRange)} instead."

    def bandpass_psd_mean(signal:typing.Iterable) -> float:
        # freq, psd = pt_data_obj._bandpassFilter_calculatePSD_mask(signal=signal, freqRange=freqRange, samplingFreq=SAMPLING_FREQUENCY)
        # return psd.mean()

        filter_processor = BandpassFilterProcessor(freq_range=freqRange, sampling_freq=SAMPLING_FREQUENCY)
        psd_processor = PowerSpectralDensityProcessor(sampling_freq=SAMPLING_FREQUENCY)

        result = np.array(signal)
        result = filter_processor(result)
        result = psd_processor(result)
        freq, psd = result.filter_freq_range(freq_range=freqRange)
        result = psd.mean()
        
        return result


        
        
    df = pt_data_obj.get_dataframe()
    
    df = (df
          .pivot(
            index=["TreatmentBranch", "FirstPacketDateTime"],
            columns=["IpsiContra"],
            values="TimeDomainData")
          .sort_index(axis=0, level=1)
          .groupby(level=0)
          .tail(3)
          .map(lambda cell: bandpass_psd_mean(signal=cell))
    )


    # t-Test
    grouped = df.droplevel(axis=0, level=1).groupby("TreatmentBranch")

    treatmentBranches = df.index.get_level_values(level=0).unique().values
    sides = df.columns.get_level_values(level=0).unique().values

    combos = itertools.combinations(treatmentBranches, 2)
    combos = itertools.product(combos, sides)
    combos = [[treat1, treat2, side] for (treat1, treat2), side in combos]
    pvalue_holder = []
    
    for treatment1, treatment2, side in combos:
        group1 = grouped.get_group(treatment1).loc[:, side].to_numpy()
        group2 = grouped.get_group(treatment2).loc[:, side].to_numpy()
        pvalue = scp.stats.ttest_ind(group1, group2, equal_var=False).pvalue  # Pairwise t-test
        pvalue_holder.append(pvalue)
        
    multi_index = pd.MultiIndex.from_tuples(combos, names = ["Treatment1", "Treatment2", "IpsiContra"])
    pvalue_df = pd.DataFrame(data=pvalue_holder, index=multi_index)
    
    # Pivot
    pvalue_df = pvalue_df.reset_index().rename({0: "pvalue"}, axis=1)
    pvalue_df = pvalue_df.pivot(index="Treatment1", columns=["IpsiContra", "Treatment2"], values="pvalue").sort_index(axis=1, level=0)

    return df, pvalue_df



def plot_boxplot_with_mean(pt_data_obj: Patient_Dataset_Base, freqRange):
    # Calcualte last 3 session mean PSD (with specified freqRange) and t-test pvalue
    df_last_3_psd_mean, df_pvalue = last_3_session_mean_psd_and_pvalue(pt_data_obj=pt_data_obj, freqRange=freqRange)
    data_colname = f"Mean PSD of range {freqRange}"
    
    # Plot
    nrows, ncols, inches, xyratio = 2, 2, 5, 1
    mosaic = [["ipsi", "contra"], ["table", "table"]]
    fig, axs = plt.subplot_mosaic(mosaic, sharey=True, figsize=(ncols*inches*xyratio, nrows*inches))
    
    sides, treatments = df_last_3_psd_mean.columns.unique(), df_last_3_psd_mean.index.get_level_values(0).unique(0)
    
    for side in sides:
        
        data_holder = []
        
        # match side: 
        #     case "ipsi":
        #         ax = axs[0]
        #     case "contra": 
        #         ax = axs[1]
        ax = axs[side]
        for treatment in treatments:
            data = df_last_3_psd_mean.loc[(treatment, slice(None)), side].to_numpy()
            data_holder.append(data)
        
        # Boxplot
        ax.boxplot(
            x = data_holder, 
            tick_labels=treatments,
            positions=range(len(treatments)),
            widths=.6,
            showmeans=True,  # SHOW MEAN!!!
            meanline=False,   # SHOW MEAN!!!
        )
        ax.set_title(side)
        ax.grid(visible=True, which="major", axis="y")
        ax.set_ylabel(data_colname)

        # Violin plot
        # ax.violinplot(
        #     dataset = data_holder, 
        #     positions = range(len(data_holder)), 
        #     showmeans = True,
        # )
        # ax.set_title(side)
        # ax.grid(visible=True, which="major", axis="y")
        # ax.set_ylabel(data_colname)
        # ax.set_xticks(range(len(treatments)), labels=treatments)

        # Scatter
        for idx_scatter, data in enumerate(data_holder): 
            x = np.random.normal(loc=idx_scatter, scale=0.05, size=len(data))
            y = data
            ax.scatter(x, y, color="red")
        
    # Add table
    # ax = axs[2]
    ax = axs["table"]
    ax.axis('off')
    df_pvalue = df_pvalue.T
    pvalues = df_pvalue.to_numpy()
    colors = np.where(pvalues<0.05, "green", "red")

    ax.table(
        cellText = pvalues.round(8),
        cellLoc="center",
        cellColours=colors,
        rowLabels=df_pvalue.index,
        colLabels=df_pvalue.columns,
        loc="center",
    )

    fig.set_layout_engine("constrained")
    
    return fig
            
            
    
@IndividualPlotter.register
def plot_boxplot_with_mean_low_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = BIOMARKER_BANDS_FASANO_2024["low-beta"]
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of low-beta mean PSD")
    return fig
    

@IndividualPlotter.register
def plot_boxplot_with_mean_high_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = BIOMARKER_BANDS_FASANO_2024["high-beta"]
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of high-beta mean PSD")
    return fig

@IndividualPlotter.register
def plot_boxplot_with_mean_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = (BIOMARKER_BANDS_FASANO_2024["low-beta"][0], BIOMARKER_BANDS_FASANO_2024["high-beta"][1])
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of beta mean PSD")
    return fig