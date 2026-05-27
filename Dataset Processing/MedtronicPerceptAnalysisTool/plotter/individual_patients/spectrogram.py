import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from MedtronicPerceptAnalysisTool.data_wrapper.base import Patient_Dataset_Base
from ...signal_processor.stft import stft_method
from matplotlib import colors, ticker
from ..plotter import IndividualPlotter

@IndividualPlotter.register
def plot_spectrogram(pt_data_obj: Patient_Dataset_Base):
    """Plot patient's spectrogram in order of recording session time."""
    
    pt_obj = pt_data_obj
    
    df = pt_obj.get_dataframe()
    treatment_order = df.TreatmentOrder[0].split(',')
    n_sessions = 0
    df_grouped = df.groupby(by=["Channel"])

    for group in df_grouped.groups:
        temp = df_grouped.get_group((group,)).sort_values(by="FirstPacketDateTime")
        if temp.shape[0] > n_sessions:
            n_sessions = temp.shape[0]

    nrows, ncols, inches, xyratio = (len(df_grouped.groups), n_sessions, 5, 1)
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharey=True, sharex=True)

    spec_holder = {}
    total_max, total_min = 0, 0
    
    for idx_channel, channel in enumerate(df_grouped.groups):
        df_channel = df_grouped.get_group((channel, )).sort_values(by="FirstPacketDateTime")
        
        spec_datas = (df_channel
            .loc[:, "TimeDomainData"]
            .apply(lambda signal: stft_method(signal=signal))
        )
        
        spec_holder[channel] = spec_datas
        channel_max = spec_datas.apply(np.max).max()
        channel_min = spec_datas.apply(np.min).min()
        
        total_max = channel_max if channel_max > total_max else total_max
        total_min = channel_min if channel_min < total_min else total_min
        

    colornorm = colors.Normalize(vmin=total_min, vmax=total_max)

    for idx_channel, channel in enumerate(df_grouped.groups):
        specs = spec_holder[channel]
        
        for idx_session, spec in enumerate(specs):
            match len(axs.shape):
                case 1:
                    ax = axs[idx_session]
                case 2:
                    ax = axs[idx_channel, idx_session]
                case _:
                    raise ValueError(f"Expect either one or two dimensional plots, got {len(axs.shape)} dimensions instead")
                
            treatment = df_grouped.get_group((channel,)).iloc[idx_session].loc["TreatmentBranch"]
            
            freqRange = range(10, 51)
            img = ax.imshow(
                spec[freqRange, :],
                aspect="auto",
                cmap="viridis",
                origin="lower",
                norm=colornorm,
            )
            ax.set_title(f"Channel {channel} - Session {idx_session} - {treatment}")
            ax.set_ylabel("Freq (Hz)")
            ax.set_xlabel("n-th data point")
            ax.yaxis.set_major_locator(ticker.MultipleLocator(base=1, offset=freqRange[0]))
            # ax.yaxis.set_major_formatter(ticker.FixedFormatter(freqRange))

    fig.colorbar(img, ax=axs)
    
    patient_prefix = "-".join(pt_obj.__class__.__name__.split("_")[:2])
    fig.suptitle(f"{patient_prefix} Spectrogram")
    
    fig.set_layout_engine("constrained")
    return fig
        
    