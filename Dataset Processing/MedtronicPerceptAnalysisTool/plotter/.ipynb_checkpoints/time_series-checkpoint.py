from ..data_wrapper.base import Patient_Dataset_Base
import matplotlib.pyplot as plt
from matplotlib import ticker
from ..utility.constants import COLOR_LEFT_HEMISPHERE, COLOR_RIGHT_HEMISPHERE, BIOMARKER_BANDS_FASANO_2024
from matplotlib.axes import Axes
from ..filter.iir import IIR_butterworth_filter_hammer_2022
from ..spectral.psd import psd_welch_contaldi_2023            
import numpy.typing as npt
import numpy as np
from matplotlib import patches
        

def plot_recording_sessions_seconds(pt_data_obj: Patient_Dataset_Base):
    """Convenience function to plot the summary of a patient's dataset"""
    # TODO: Add function name to top-right of figure with alpha = 0.5
    
    obj = pt_data_obj
    df = obj.get_dataframe()
    sampling_rate = 250
    
    treatment_order = df.loc[0, "TreatmentOrder"].split(sep=",")
    channels = df.loc[:, "Channel"].unique()
    df = df.loc[:, ["Channel", "FirstPacketDateTime", "TreatmentBranch", "TimeDomainData"]]
    df = df.set_index(["TreatmentBranch", "Channel", "FirstPacketDateTime"])

    nrows, ncols, inches, xyratio = 1, 3, 5, 1.3
    fig, axs = plt.subplot_mosaic(
        mosaic=[treatment_order],
        gridspec_kw=dict(width_ratios=[1, 2, 2]),
        layout="constrained", 
        figsize=(ncols*inches*xyratio, nrows*inches),
        sharey=True,
    )

    session_count_offset = 0
    
    for treatment in treatment_order:
        max_session_count = 0
        ax: Axes = axs[treatment]
        for channel in channels:
            
            # Determine color
            match channel.split('_')[-1].upper():
                case "LEFT":
                    color = COLOR_LEFT_HEMISPHERE
                case "RIGHT":
                    color = COLOR_RIGHT_HEMISPHERE
                case _:
                    raise ValueError(f"Expect LEFT/RIGHT, got {channel.split('_')[-1].upper()}")
            
            # Extract data
            df_temp = df.loc[(treatment, channel, slice(None))].sort_index(level=2)
            sample_counts = df_temp.apply(func=lambda row: len(row["TimeDomainData"]), axis=1)
            session_durations = sample_counts / sampling_rate
            session_count = len(session_durations)
            if session_count > max_session_count: 
                max_session_count = session_count
            
            # Plot
            x = range(session_count_offset, session_count_offset+max_session_count)
            y = session_durations
            label = channel
            ax.bar(x=x, height=y, label=label, alpha=0.3, color=color)
            ax.legend()
            ax.xaxis.set_major_locator(ticker.FixedLocator(x))
            
        session_count_offset += max_session_count
        ax.set_title(treatment.upper())
        ax.set_title(f"{treatment.upper()} Session durations")
        ax.set_xlabel("Recording Session")
        ax.set_ylabel("Duration (sec)")
    
    fig_title = "_".join(obj.__class__.__name__.split("_")[:2])
    fig.suptitle(fig_title)
    
    return fig
            

def plot_mean_beta_time_series(pt_data_obj: Patient_Dataset_Base):
    """Plots the unadjusted mean beta power time series.
    
    The goal for this plot was to use as an sanity check 

    """
    # TODO: Add function name to top-right of figure with alpha = 0.5
    def get_mean_beta_power(lfp_data:npt.NDArray):
        """Given an array of LFP signal return the beta PSD mean of the beta range."""
        
        assert isinstance(lfp_data, np.ndarray), f"Input has to be of `np.ndarray` type, got {type(lfp_data)}"
        
        fs = 250
        freqRange = (12, 30)

        # TODO: Read this function function from the patient data object
        filtered_signal = IIR_butterworth_filter_hammer_2022(
            data=lfp_data,
            freqRange=freqRange,
            fs=fs,
        )
        # TODO: Read this function function from the patient data object
        freq, psd = psd_welch_contaldi_2023(
            data=filtered_signal,
            fs=fs,
        )
        mask = (freq >= freqRange[0]) & (freq <= freqRange[1])
        psd = psd[mask]
        mean_beta_psd = psd.mean()

        return mean_beta_psd

    def get_patient_mean_beta_psd(patient_data_obj):
        base_key = 'MeanBetaPSD'
        pt = patient_data_obj
        df = pt.get_dataframe()
        
        treatment_order = df.TreatmentOrder[0].split(',')
        hemispheres = df.RecordingHemisphere.unique()
        holder = {}
        
        for idx_treatment, treatment in enumerate(treatment_order):
            
            for hemisphere in hemispheres:
                holder[f'{idx_treatment}-{base_key}-{treatment}-{hemisphere}'] = []
                mask = (df.TreatmentBranch == treatment) & (df.RecordingHemisphere == hemisphere)
                lfp_datas = df.loc[mask, 'TimeDomainData']
                
                for lfp_data in lfp_datas:
                    lfp_data = np.array(lfp_data)
                    mean_beta_psd = get_mean_beta_power(lfp_data=lfp_data)
                    
                    holder[f'{idx_treatment}-{base_key}-{treatment}-{hemisphere}'].append(mean_beta_psd)
                
        return holder
    
    pt = pt_data_obj
    pt_results = get_patient_mean_beta_psd(patient_data_obj=pt)
    
    print(pt_results.keys())
    base_keys = set(['-'.join(key.split('-')[0:3]) for key in pt_results.keys()])
    base_keys = sorted(base_keys)
    # print(bases)  # DEBUG
    
    nrows, ncols, inches, xyratio = 1, len(base_keys), 5, 1.3
    # fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharey=True)
    fig, axs = plt.subplot_mosaic(
        mosaic=[base_keys],
        gridspec_kw=dict(width_ratios=[1, 2, 2]),
        layout="constrained", 
        figsize=(ncols*inches*xyratio, nrows*inches),
        sharey=True,
    )
    

    for base_key in base_keys:
        
        ax = axs[base_key]
        for hemisphere in ['left', 'right']:
            try:
                key = f'{base_key}-{hemisphere}'
                value = pt_results[key]
            except KeyError:
                continue
            
            match hemisphere:
                case "left":
                    color = COLOR_LEFT_HEMISPHERE
                case "right":
                    color = COLOR_RIGHT_HEMISPHERE
                case _:
                    raise ValueError(f"Expected either `left` or `right`, got {hemisphere}")
            
            ax.scatter(range(len(value)), value, c=color, label=f'Mean beta PSD - {hemisphere}')
            ax.plot(value, alpha=0.3, c=color)
            ax.legend()
            ax.set_title(key)
            ax.xaxis.set_major_locator(ticker.FixedLocator(range(len(value))))
            
    fig.suptitle(f'{pt.__class__.__name__} | Glove Hand: {pt.glove_hand}')
    fig.set_layout_engine('constrained')
    
    # save_path = Path(save_path)
    # fig.savefig(save_path/Path(f'{constructor.__name__}_mean_beta_timeseries_quickcheck.svg'))
        
    return fig


def plot_mean_beta_psd_normalized(pt_data_obj: Patient_Dataset_Base):
    # TODO: Add function name to top-right of figure with alpha = 0.5
    
    patient = pt_data_obj
    betaRange = (BIOMARKER_BANDS_FASANO_2024["low-beta"][0], BIOMARKER_BANDS_FASANO_2024["high-beta"][1])
    lowbeta = BIOMARKER_BANDS_FASANO_2024["low-beta"]
    highbeta = BIOMARKER_BANDS_FASANO_2024["high-beta"]

    freqRanges = [lowbeta, highbeta, betaRange]

    def get_session_ranges(df):
            range_dicts = []
            treatment_order = df.TreatmentOrder[0].split(',')  # Get the first record of the treatment order list

            for channel in df.Channel.unique():
                range_dict = {}
                temp = df.loc[df.Channel == channel, :]
                temp = (temp
                        .pivot_table(values="SessionNumber", index=["Channel", "TreatmentBranch"], aggfunc="count")
                        .reset_index(level=0, drop=True)
                        .loc[treatment_order, :]  # Match the treatment order list
                        .cumsum(axis=0)
                )

                ends = temp.to_numpy().squeeze()

                range_dict[treatment_order[0]] = range(0, ends[0])
                range_dict[treatment_order[1]] = range(ends[0], ends[1])
                range_dict[treatment_order[2]] = range(ends[1], ends[2])

                range_dicts.append(range_dict)

            match len(range_dicts):
                case 1:
                    return range_dicts[0]
                case 2: 
                    if range_dicts[0] != range_dicts[1]: raise ValueError("The session mapping for each channel is different.")
                    return range_dicts[0]
                case _:
                    raise ValueError("There are more than two channels in this dataframe!")
                    return
    dfs_ = ((freqRange, patient._get_dataframe_with_psd_norm(freqRanges=freqRanges)) for freqRange in freqRanges)
    
    # Plot
    nrows, ncols, inches, xyratio = 1, 2, 4, 3
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharey=True, sharex=True)
    stage_markers_marked = False

    for freqRange, df in dfs_:
        # Point norms - Tuple's second element is PSD, first is freq
        pointDivNorm = df[f"BaselineNormalizedMeanPSD_{freqRange}"].to_numpy()
        # pointDivNorm = df[f"BaselineNormalizedMeanPSD_{freqRange}"].apply(lambda cell: cell[1].mean()).to_numpy()


        # Plot each channel (hemisphere)
        for idx_channel, channel in enumerate(df["Channel"].unique()):
            mask = df["Channel"] == channel

            if "left" in channel.lower():
                ax = axs[0]  # Left graph
            elif "right" in channel.lower():
                ax = axs[1]  # Right graph
            else:
                raise ValueError

            # Point div norm
            y2 = (pointDivNorm[mask] - 1) * 100 # Percentage change from baseline
            x2 = np.arange(len(y2))  # 0 indexed
            ax.plot(x2, y2, label=f"Baseline Normalized mean PSD - band = {freqRange}")
            ax.bar(x2, y2, alpha=0.05)

            # Add artists
            ax.hlines(y=0, xmin=x2.min(), xmax=x2.max(), colors="red")
            ax.set_xlabel("Session number")
            ax.set_ylabel("Percentage change from baseline")
            ax.set_title(channel)
            ax.legend()

            # Add stage markers
            if not stage_markers_marked:
                stage_names = df.TreatmentOrder[0].split(',')
                stage_ranges = get_session_ranges(df=df).values()
                for stage, stage_range, color in zip(stage_names, stage_ranges, ['C4', 'C4', 'C4']):   
                    xmin, xmax = stage_range[0], stage_range[-1]
                    ymin, ymax = ax.get_ylim()
                    rect = patches.Rectangle((xmin, ymin), xmax-xmin, ymax-ymin, facecolor=color, alpha=0.1)
                    ax.add_patch(rect)

                    ax.annotate(
                        text=f"{stage}", 
                        xy=((xmin+xmax)/2, ymin*1.1), color=color, horizontalalignment='center', verticalalignment='bottom')

        stage_markers_marked = True

    fig.suptitle(f"{patient.__class__.__name__}\nStimGloveHand={patient.glove_hand}\nTreatmentOrder={df.TreatmentOrder[0]}")
    fig.tight_layout()


    return fig

# def plot_lfp_and_psd(pt_data_obj: Patient_Dataset_Base):
