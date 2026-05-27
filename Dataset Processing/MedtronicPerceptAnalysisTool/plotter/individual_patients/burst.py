from matplotlib.figure import Figure
from ..plotter import IndividualPlotter
from MedtronicPerceptAnalysisTool.signal_processor.burst import DualThresholdBurstProcessor
from MedtronicPerceptAnalysisTool.signal_analyzer.burst import DualThresholdFullBetaBurstAnalyzer

import matplotlib.pyplot as plt
from pprint import pprint
import pandas as pd
from itertools import product

@IndividualPlotter.register
def plot_burst_stat(pt_obj) -> Figure:
    
    
    def get_figure_title_prefix(pt_obj):
        return " ".join(pt_obj.__class__.__name__.split("_")[:2])

    def get_df_mosaic(df): 
        df = df.sort_values(by="FirstPacketDateTime")
        ipsicontra_unique = df.IpsiContra.unique()
        treatment_unique = df.TreatmentBranch.unique()

        return [[ str(item) for item in product(ipsicontra_unique, treatment_unique)],]
    
    def get_mosaic_ax(axs, mosaic_key):
        return axs[str(mosaic_key)]
    
    
    def plot_burst_stats(df):
        
        df = df.stack(future_stack=True).reset_index(drop=False)#.filter(["TreatmentBranch", "IpsiContra", "n_bursts", "duration_mean", "duration_std", "percent_burst", "bursts_per_second"], axis=1)
        
        burst_colnames = df.columns[-5:]
        nrows, ncols, inches, xyratio = 1, 2, 5, 1.3
        fig, axs = plt.subplot_mosaic(
            mosaic=get_df_mosaic(df),
            sharey=True,
            figsize=(ncols*inches*xyratio, nrows*inches), 
            # gridspec_kw={"width_ratios": [1, 2, 2, 1, 2, 2]}
        )
        
        grouped = df.groupby(by=["IpsiContra", "TreatmentBranch"])
        for groupname, group in grouped:
            ax = group[burst_colnames].plot(ax=get_mosaic_ax(axs, groupname), legend=False)
            ax.set_title(groupname)

        ax.legend()

        return fig

    analyzer = DualThresholdFullBetaBurstAnalyzer()
    fig = plot_burst_stats(analyzer(pt_obj))
    fig.suptitle(f"{get_figure_title_prefix(pt_obj)} Burst Stats    freq_range={analyzer.freq_range}    detection_threshold={analyzer.dual_threshold}")
    fig.set_layout_engine("constrained")
    
    return fig

    
    def plot_burst_raw(pt_obj):
        pass