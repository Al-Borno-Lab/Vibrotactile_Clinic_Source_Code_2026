
# TOOD: First-order boxplot (not normalized) - plot 4 - Later, these are the cross patient plots

# TODO: First-order boxplot (normalized) - plot 5 - Later, these are the cross patient plots


# TODO: Box plot for per patient (not normalized) with jitter to show diff between treatments
# TODO: Box plot for per patient (normalized) with jitter to show diff between treatments

from .support_functions import calculate_mean_psd_of_freqRange
from ..data_wrapper.base import Patient_Dataset_Base
import matplotlib.pyplot as plt
from ..utility.constants import BIOMARKER_BANDS_FASANO_2024
import scipy as scp

def plot_boxplot_with_mean(pt_data_obj: Patient_Dataset_Base, freqRange: tuple):

    def pairwise_t_test(in_order_data:list, in_order_treatment_names:list) -> dict:
        
        holder = {}
        data0, data1, data2 = in_order_data
        stage0, stage1, stage2 = in_order_treatment_names
        stage0, stage1, stage2 = stage0.upper(), stage1.upper(), stage2.upper()
        
        holder[f"{stage0} v {stage1} (Welch ind t-test)"] =  round(scp.stats.ttest_ind(data0, data1, equal_var=False).pvalue, 5)
        holder[f"{stage0} v {stage2} (Welch ind t-test)"] =  round(scp.stats.ttest_ind(data0, data2, equal_var=False).pvalue, 5)
        holder[f"{stage1} v {stage2} (Welch ind t-test)"] =  round(scp.stats.ttest_ind(data1, data2, equal_var=False).pvalue, 5)

        return holder
    
    def add_stat_sig_stars(data_holder_dict:dict) -> dict:
        
        for key, value in data_holder_dict.items():
            
            if value < 0.001:
                data_holder_dict[key] = f"{value} **"
                continue
            if value < 0.05:
                data_holder_dict[key] = f"{value} *"
                continue
            
        return data_holder_dict
            
    
    df = calculate_mean_psd_of_freqRange(pt_data_obj=pt_data_obj, freqRange=freqRange)
    hemispheres = df.loc[:, "RecordingHemisphere"].unique()
    # treatmentOrder = df.loc[:, "TreatmentOrder"].unique()[0].split(',')
    treatmentOrder = df.loc[0, "TreatmentOrder"].split(',')
    data_colname = df.columns[-1]
    
    nrows, ncols, inches, xyratio = 1, 2, 5, .8
    fig, axs = plt.subplots(
        nrows, 
        ncols, 
        figsize=(ncols*inches*xyratio, nrows*inches), 
        sharey=True,
        # layout="constrained",
    )

    for ax, hemisphere in zip(axs, hemispheres):
        
        data_holder = []
        
        for idx, treatment in enumerate(treatmentOrder):
            mask = (df.loc[:, "TreatmentBranch"] == treatment) & (df.loc[:, "RecordingHemisphere"] == hemisphere)
            data = df.loc[mask, data_colname].to_numpy()
            data_holder.append(data)
            
            
        # Boxplot
        ax.boxplot(
            x = data_holder, 
            labels=treatmentOrder,
            positions=range(len(treatmentOrder)),
            widths=.9,
            showmeans=True,  # SHOW MEAN!!!
            meanline=False,   # SHOW MEAN!!!
        )
        ax.set_title(hemisphere)
        ax.grid(visible=True, which="major", axis="y")
        ax.set_ylabel(data_colname)

        # Violin plot
        ax.violinplot(
            dataset = data_holder, 
            positions = range(len(data_holder)), 
            showmeans = True,
        )
        ax.set_title(hemisphere)
        ax.grid(visible=True, which="major", axis="y")
        ax.set_ylabel(data_colname)
        ax.set_xticks(range(len(treatmentOrder)), labels=treatmentOrder)
        
        # Add text
        ttest_result_dict = pairwise_t_test(data_holder, treatmentOrder)
        ttest_result_dict = add_stat_sig_stars(ttest_result_dict)
        text = [f"{key}: {value}" for key, value in ttest_result_dict.items()]
        ax.text(
            0.1, -0.1, "\n".join(text), 
            fontsize="x-small",
            horizontalalignment='left', 
            verticalalignment='top',
            transform=ax.transAxes)

    fig.set_layout_engine("constrained")
    
    return fig

def plot_boxplot_with_mean_low_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = BIOMARKER_BANDS_FASANO_2024["low-beta"]
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of low-beta mean PSD")
    return fig
    

def plot_boxplot_with_mean_high_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = BIOMARKER_BANDS_FASANO_2024["high-beta"]
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of high-beta mean PSD")
    return fig

def plot_boxplot_with_mean_beta(pt_data_obj: Patient_Dataset_Base):
    freqRange = (BIOMARKER_BANDS_FASANO_2024["low-beta"][0], BIOMARKER_BANDS_FASANO_2024["high-beta"][1])
    fig = plot_boxplot_with_mean(pt_data_obj=pt_data_obj, freqRange=freqRange)
    patient_label = "_".join(pt_data_obj.__class__.__name__.split("_")[0:2])
    fig.suptitle(f"{patient_label} - Distribution of beta mean PSD")
    return fig