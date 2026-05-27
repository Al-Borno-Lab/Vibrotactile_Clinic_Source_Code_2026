from typing import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ..plotter import IndividualPlotter
from ...signal_processor.filter import BandpassFilterProcessor
from ...signal_processor.psd import PowerSpectralDensityProcessor

@IndividualPlotter.register
def plot_full_beta_ipsi_contra_mean_psd(pt_data_obj):
    idx = pd.IndexSlice
    freqRange = (12, 30)
    
    
    def bandpass_and_calculate_mean_psd(*, signal:Iterable, freqRange:Tuple) -> float:

        sampling_freq = 250
        signal = np.array(signal)

        filter_processor = BandpassFilterProcessor(
            freq_range=freqRange,
            sampling_freq=sampling_freq
        )
        psd_processor = PowerSpectralDensityProcessor(
            sampling_freq=sampling_freq
        )
        signal = filter_processor(data=signal)
        freq, psd = psd_processor(data=signal)
        
        masked_psd = psd[np.logical_and(freq>=freqRange[0], freq<=freqRange[1])]
        mean_psd = masked_psd.mean()

        return mean_psd
    
    
    df = pt_data_obj.get_dataframe()

    df_pivot = df.pivot(
        index=["PatientNumber", "TreatmentBranch", "FirstPacketDateTime"],
        columns=["IpsiContra"],
        values=["TimeDomainData"],
    )
    
    df_pivot = df_pivot.sort_index(axis=0, level=2)
    
    df_pivot = df_pivot.map(lambda element: bandpass_and_calculate_mean_psd(signal=element, freqRange=freqRange))
    
    # display(df_pivot)

    stages = df_pivot.index.get_level_values(1).unique()
    ipsicontras = df_pivot.columns.get_level_values(1).unique()
    nrows, ncols, inches, xyratio = 1, len(stages), 3, 1.5 
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharey=True, sharex=False)
    
    for idx_row, ipsicontra in enumerate(ipsicontras):
        for idx_col, stage in enumerate(stages):
            
            ax = axs[idx_col]
            
            data = df_pivot.loc[idx[:, stage, :], idx[:, ipsicontra]]
            y = data.values
            # x = data.index.get_level_values(2)
            x = range(len(y))
            label = f"{stage} - {ipsicontra} - freqRange {freqRange}"

            ax.set_title(f"{stage} - freqRange {freqRange}")
            ax.scatter(x, y, marker=".", s=10, label=ipsicontra)
            ax.plot(x, y, alpha=0.3)
            ax.legend()
            
            ax.set_ylabel("Mean PSD")
            ax.set_xlabel("Session Number")
            
    fig.set_layout_engine("constrained")
    pt_prefix = "-".join(pt_data_obj.__class__.__name__.split("_")[:2])
    fig.suptitle(f"{pt_prefix} - Ipsi/Contra average PSD in freqRange {freqRange}")

    return fig