import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from ..data_wrapper import * 
from ..plot.plotter import plot_lfp, plot_psd
from ..utility import constants
from ..data_wrapper.base import Patient_Dataset_Base

def plot_lfp_and_psd(pt_data_obj: Patient_Dataset_Base) -> Figure:

    df = pt_data_obj.get_dataframe()
    # display(df.head())

    treatment_order = df.loc[0, "TreatmentOrder"].split(",")
    # channels = df.Channel.unique()
    
    
    session_count = (df
        .pivot_table(values="SessionNumber", index="Channel", columns="TreatmentBranch", aggfunc="count")
        .rename(mapper={"SessionNumber": "SessionCount"}, axis=1)
    )
    n_subplots = session_count.iloc[0, :].sum()

    match session_count.shape[0]:
        case 1:
            pass
        case 2: 
            assert (session_count.iloc[0, :] == session_count.iloc[1, :]).all(), f"Expected recording session for each channel and each treatment branch to be the same."
        case _:
            raise ValueError(f"Expected either 1 or 2 channels in recording records, got {session_count.shape[0]} instead.")
    

    nrows, ncols, inches, xyratio = n_subplots, 2, 5, 10
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))

    # Plot LFP and PSD
    grouped = df.groupby(by="Channel")
    for channel in grouped.groups:
        df_by_channel = grouped.get_group(channel).sort_values("FirstPacketDateTime")
        
        if 'left' in channel.lower():
            color = constants.COLOR_LEFT_HEMISPHERE
        if 'right' in channel.lower():
            color = constants.COLOR_RIGHT_HEMISPHERE

        for idx_session in range(n_subplots):
            treatment = df_by_channel.loc[:, "TreatmentBranch"].iloc[idx_session]
            
            # Plot LFP
            ax = axs[idx_session, 0]
            lfp_data = df_by_channel.loc[:, "TimeDomainData"].iloc[idx_session]
            x = range(len(lfp_data))
            
            plot_lfp(
                x=x, 
                y=lfp_data, 
                ax=ax,
                label=channel,
                color=color, 
                ax_title=f"RecordingSession {idx_session} - {treatment}",
            )

            # Plot PSD
            ax = axs[idx_session, 1]
            lfp_data = np.array(lfp_data)
            # TODO: Add bandpass to both raw LFP and PSD and add to figure title
            freq, psd_data = pt_data_obj._calculate_psd(data=lfp_data, fs=250)

            plot_psd(
                x=freq,
                y=psd_data,
                ax=ax,
                label=channel,
                color=color,
                ax_title=f"RecordingSession {idx_session} - {treatment}",
            )
            
    
    pt_prefix = "_".join(pt_data_obj.__class__.__name__.split('_')[:2])
    fig.suptitle(f"{pt_prefix} - LFP and PSD (NOT BANDPASS'D YET)")
    
    fig.set_layout_engine("constrained")
    return fig