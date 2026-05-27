
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings
from ..utility.stats import get_stat_test_string, ttest_independent, wilcoxon_paired, wilcoxon_ind
import inspect
from ..utility.constants import FrequencyRange

def plot_all_patients_all_sessions_various_splits(df, dest_colname): 
    nrows, ncols, inches, aspect = 1, 4, 6, 1
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*aspect, nrows*inches), sharey=True)
    fig.text(1, 1, ha='right', alpha=0.3, s=inspect.currentframe().f_code.co_name)


    # Plot 
    ax = axs[0]
    sns.pointplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        alpha=0.7,
        color='orange',
        ax=ax,
    )
    sns.violinplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        ax=ax,
    )
    sns.swarmplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        c='red',
        size=3,
        alpha=.7,
        ax=ax,
    )
    # ax.set_title(title)
    ax.text(0, -0.2, 
            get_stat_test_string(df.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind), 
            transform=ax.transAxes, ha='left', va='top'
    )

    # Plot
    ax=axs[1]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='IpsiContra',
        # col = 'TreatmentOrder',
        ax=ax,
    )

    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='IpsiContra',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title)
    text_holder = []
    for groupname, groupdata in df.groupby("IpsiContra"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )




    # Plot
    ax=axs[2]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='RecordingHemisphere',
        # col = 'TreatmentOrder',
        ax=ax,
    )
    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='RecordingHemisphere',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title+" RecordingHemisphere")
    text_holder = []
    for groupname, groupdata in df.groupby("RecordingHemisphere"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )


    # Plot
    ax=axs[3]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='StimGloveHand',
        # col = 'TreatmentOrder',
        ax=ax,
    )
    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='StimGloveHand',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title+" StimGloveHand")
    text_holder = []
    for groupname, groupdata in df.groupby("StimGloveHand"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )
    
    
    fig.suptitle(dest_colname)
    fig.set_layout_engine("constrained")

    return fig

def plot_all_patients_10_11_12_various_splits(df, dest_colname): 
    nrows, ncols, inches, aspect = 1, 4, 6, 1
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*aspect, nrows*inches), sharey=True)
    fig.text(1, 1, ha='right', alpha=0.3, s=inspect.currentframe().f_code.co_name)

    df_dbs_off = (
        df
        .query("TreatmentBranch == 'dbs_off'")
        .groupby(["PatientNumber", "Channel", "TreatmentBranch"])
        .nth(range(3, 6))
    )
    df_treatment = (
        df
        .query("TreatmentBranch != 'dbs_off'")
        .groupby(["PatientNumber", "Channel", "TreatmentBranch"])
        .nth(range(9, 12))
    )
    df = pd.concat([df_dbs_off, df_treatment], axis=0)

    # Plot 
    ax = axs[0]
    sns.pointplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        alpha=0.7,
        color='orange',
        ax=ax,
    )
    sns.violinplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        ax=ax,
    )
    sns.swarmplot(
        df,
        y=dest_colname,
        x='TreatmentBranch',
        c='red',
        size=3,
        alpha=.7,
        ax=ax,
    )
    # ax.set_title(title)
    ax.text(0, -0.2, 
            get_stat_test_string(df.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind), 
            transform=ax.transAxes, ha='left', va='top'
    )

    # Plot
    ax=axs[1]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='IpsiContra',
        # col = 'TreatmentOrder',
        ax=ax,
    )

    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='IpsiContra',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title)
    text_holder = []
    for groupname, groupdata in df.groupby("IpsiContra"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )




    # Plot
    ax=axs[2]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='RecordingHemisphere',
        # col = 'TreatmentOrder',
        ax=ax,
    )
    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='RecordingHemisphere',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title+" RecordingHemisphere")
    text_holder = []
    for groupname, groupdata in df.groupby("RecordingHemisphere"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )


    # Plot
    ax=axs[3]
    sns.violinplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='StimGloveHand',
        # col = 'TreatmentOrder',
        ax=ax,
    )
    sns.pointplot(
        df,
        y=dest_colname,
        x="TreatmentBranch", 
        hue='StimGloveHand',
        # col = 'TreatmentOrder',
        dodge=True,
        ax=ax,
    )
    # ax.set_title(title+" StimGloveHand")
    text_holder = []
    for groupname, groupdata in df.groupby("StimGloveHand"):
        text_holder.append( f"{groupname.upper()}\n" + get_stat_test_string(groupdata.groupby("TreatmentBranch")[dest_colname].apply(list).to_dict(), wilcoxon_ind) )
    ax.text(0, -0.2, 
            "\n".join(text_holder), 
            transform=ax.transAxes, ha='left', va='top'
    )
    
    
    fig.suptitle(dest_colname)
    fig.set_layout_engine("constrained")

    return fig

def plot_all_patients_all_sessions_treatment_order_split(df, freq_range):
    def annotate(data, **kwargs):
        shape = data.shape
        ax = plt.gca()
        ax.text(0, -0.3, s=shape, transform=ax.transAxes)

    def annotate1(data, **kwargs):
        
        df = data
        
        for idx, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("TreatmentOrder")):
            data_dict = treatemnt_order_data.groupby("TreatmentBranch")[f"PowerMean_PercentageChange_{freq_range}"].apply(list).to_dict()
            result = get_stat_test_string(data_dict, wilcoxon_ind)
            
            text_string = "\n".join(
                [
                    "#"*10,
                    "Wilcoxon independent".upper(),
                    f"{treatment_order.upper()}",
                    result,
                    "#"*10,
                    "\n",
                ]
            )

            ax = plt.gca()
            ax.text(x=0, y=1, ha='left', va='top', s=text_string, transform=ax.transAxes)
        

    def annotate2(data, **kwargs):
        df = data
        for treatment_order, treatemnt_order_data in df.groupby("TreatmentOrder"):
            data_dict = treatemnt_order_data.groupby("TreatmentBranch")[f"PowerMean_PercentageChange_{freq_range}"].apply(list).to_dict()
            result = get_stat_test_string(data_dict, ttest_independent)
            
            text_string = "\n".join(
                [
                    "#"*10,
                    "ttest independent".upper(),
                    f"{treatment_order.upper()}",
                    result,
                    "#"*10,
                    "\n"
                ]
                
            )
        
            ax = plt.gca()
            ax.text(x=0, y=0, ha='left', va='bottom', s=text_string, transform=ax.transAxes)

    ## Plot
    # fg = sns.catplot(
    #     df,
    #     x="TreatmentBranch", 
    #     y=f"PowerMean_PercentageChange_{freq_range}", 
    #     col = "TreatmentOrder", 
    #     kind='violin', 
    #     # order=['dbs_off', 'rvs', 'all_on'],
    # )
    fg = sns.FacetGrid(
        df, 
        col="TreatmentOrder",
        height=8,
    )
    fg.figure.suptitle(f"All sessions - {freq_range}")
    fg.figure.text(1, 1, s=inspect.currentframe().f_code.co_name, alpha=.3, ha='right')
    fg.map_dataframe(
        sns.violinplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        hue="TreatmentBranch",
        palette=sns.color_palette(),
        inner=None,
        alpha=.3
        # order = ['dbs_off', 'rvs', 'all_on'],
    )
    fg.map_dataframe(
        sns.boxplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        palette=sns.color_palette(),
        width=.3,
    )
    fg.map_dataframe(
        sns.swarmplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        color='tab:pink',
        alpha=.6,
    )
    fg.map_dataframe(
        sns.pointplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        color='tab:red',
        errorbar="sd"
    )

    fg.map_dataframe(annotate1)
    fg.map_dataframe(annotate2)

    fig = fg.figure
    fig.set_layout_engine('constrained')
    
    return fig
    
def plot_all_patients_10_11_12_sessions_treatment_order_split(df, freq_range):
    def annotate(data, **kwargs):
        shape = data.shape
        ax = plt.gca()
        ax.text(0, -0.3, s=shape, transform=ax.transAxes)

    def annotate1(data, **kwargs):
        
        df = data
        
        for idx, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("TreatmentOrder")):
            data_dict = treatemnt_order_data.groupby("TreatmentBranch")[f"PowerMean_PercentageChange_{freq_range}"].apply(list).to_dict()
            result = get_stat_test_string(data_dict, wilcoxon_ind)
            
            text_string = "\n".join(
                [
                    "#"*10,
                    "Wilcoxon independent".upper(),
                    f"{treatment_order.upper()}",
                    result,
                    "#"*10,
                    "\n",
                ]
            )

            ax = plt.gca()
            ax.text(x=0, y=1, ha='left', va='top', s=text_string, transform=ax.transAxes)
        

    def annotate2(data, **kwargs):
        df = data
        for treatment_order, treatemnt_order_data in df.groupby("TreatmentOrder"):
            data_dict = treatemnt_order_data.groupby("TreatmentBranch")[f"PowerMean_PercentageChange_{freq_range}"].apply(list).to_dict()
            result = get_stat_test_string(data_dict, ttest_independent)
            
            text_string = "\n".join(
                [
                    "#"*10,
                    "ttest independent".upper(),
                    f"{treatment_order.upper()}",
                    result,
                    "#"*10,
                    "\n"
                ]
                
            )
        
            ax = plt.gca()
            ax.text(x=0, y=0, ha='left', va='bottom', s=text_string, transform=ax.transAxes)

    
    ## Subset for session 3-5 for dbs off and 9-11 for treatment branches
    df_dbs_off = (
        df
        .query("TreatmentBranch == 'dbs_off'")
        .groupby(["PatientNumber", "Channel", "TreatmentBranch"])
        .nth(range(3, 6))
    )
    df_treatment = (
        df
        .query("TreatmentBranch != 'dbs_off'")
        .groupby(["PatientNumber", "Channel", "TreatmentBranch"])
        .nth(range(9, 12))
    )
    df = pd.concat([df_dbs_off, df_treatment], axis=0)
    
    
    
    ## Plot
    # fg = sns.catplot(
    #     df,
    #     x="TreatmentBranch", 
    #     y=f"PowerMean_PercentageChange_{freq_range}", 
    #     col = "TreatmentOrder", 
    #     kind='violin', 
    #     # order=['dbs_off', 'rvs', 'all_on'],
    # )
    fg = sns.FacetGrid(
        df, 
        col="TreatmentOrder",
        height=8,
    )
    fg.figure.suptitle(f"10,11,12 sessions - {freq_range}")
    fg.figure.text(1, 1, s=inspect.currentframe().f_code.co_name, alpha=.3, ha='right')
    fg.map_dataframe(
        sns.violinplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        hue="TreatmentBranch",
        palette=sns.color_palette(),
        inner=None,
        alpha=.3
        # order = ['dbs_off', 'rvs', 'all_on'],
    )
    fg.map_dataframe(
        sns.boxplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        palette=sns.color_palette(),
        width=.3,
    )
    fg.map_dataframe(
        sns.swarmplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        color='tab:pink',
        alpha=.6,
    )
    fg.map_dataframe(
        sns.pointplot, 
        x="TreatmentBranch", 
        y=f"PowerMean_PercentageChange_{freq_range}",
        color='tab:red',
        errorbar="sd"
    )

    fg.map_dataframe(annotate1)
    fg.map_dataframe(annotate2)

    fig = fg.figure
    fig.set_layout_engine('constrained')
    
    return fig

def plot_freqRange_powerMean_of_treatment1_2_normalized_intertreatment_baseline(df, freqRange):
    """Plots all sessions' mean power of specified range each normalized to respective its inter-treatment baseline.
    
    """
    
    freq_range = freqRange
    
    fg = sns.FacetGrid(
        df,
        col = "IpsiContra", 
        height=5,
    )

    fg.map_dataframe(
        sns.violinplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_InterTreatment_{freq_range}",
        inner = None,
        alpha=.4,
    )
    
    fg.map_dataframe(
        sns.swarmplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_InterTreatment_{freq_range}", 
        color='C2', 
        # alpha=.4,
        size=3,
    )
    
    fg.map_dataframe(
        sns.pointplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_InterTreatment_{freq_range}", 
        color='C3', 
        errorbar='sd',
        alpha=.5,
        zorder=3,
    )
    
    fig = fg.figure

    for idx_ipsicontra, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("IpsiContra")):
        data_dict = treatemnt_order_data.groupby("TreatmentNumber")[f"PowerMean_PercentageChange_InterTreatment_{freq_range}"].apply(list).to_dict()
        result = get_stat_test_string(data_dict, wilcoxon_ind, left_width=50, right_width=30)
        

        ax = fig.get_axes()[idx_ipsicontra]
        ax.text(
            x=0, y=-.2,
            s = result,
            ha='left', va='top',
            transform = ax.transAxes,
            fontsize=8,
        ) 
            
    for idx_ipsicontra, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("IpsiContra")):
        data_dict = treatemnt_order_data.groupby("TreatmentNumber")[f"PowerMean_PercentageChange_InterTreatment_{freq_range}"].apply(list).to_dict()
        result = get_stat_test_string(data_dict, ttest_independent, left_width=50, right_width=30)
        
        ax = fig.get_axes()[idx_ipsicontra]
        ax.text(
            x=0, y=-.4,
            s = result,
            ha='left', va='top',
            transform = ax.transAxes,
            fontsize=8,
        ) 
    
    
    fig.suptitle(f"PowerMean Percentage Change (Normalized to InterTreatment baseline) - freq_range = {freq_range}")
    fig.set_layout_engine('constrained')

    return fig

def plot_freqRange_powerMean_of_treatment1_2_normalized_intratreatment_baseline(df, freqRange):
    """Plot the intra-treatment normalized treatment-1 and treatment-2 for the specified freq-range."""

    freq_range = freqRange

    fg = sns.FacetGrid(
        df,
        col = "IpsiContra", 
        height=5,
    )

    fg.map_dataframe(
        sns.violinplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_IntraTreatment_{freq_range}", 
        inner = None,
        alpha=.4,
    )
    
    fg.map_dataframe(
        sns.swarmplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_IntraTreatment_{freq_range}", 
        color='C2', 
        # alpha=.4,
        size=3,
    )
    
    fg.map_dataframe(
        sns.pointplot,
        x="TreatmentNumber", 
        y=f"PowerMean_PercentageChange_IntraTreatment_{freq_range}", 
        color='C3', 
        errorbar='sd',
        alpha=.5,
        zorder=3,
    )
    
    fig = fg.figure

    for idx_ipsicontra, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("IpsiContra")):
        data_dict = treatemnt_order_data.groupby("TreatmentNumber")[f"PowerMean_PercentageChange_IntraTreatment_{freq_range}"].apply(list).to_dict()
        result = get_stat_test_string(data_dict, wilcoxon_ind, left_width=50, right_width=30)
        

        ax = fig.get_axes()[idx_ipsicontra]
        ax.text(
            x=0, y=-.2,
            s = result,
            ha='left', va='top',
            transform = ax.transAxes,
            fontsize=8,
        ) 
            
    for idx_ipsicontra, (treatment_order, treatemnt_order_data) in enumerate(df.groupby("IpsiContra")):
        data_dict = treatemnt_order_data.groupby("TreatmentNumber")[f"PowerMean_PercentageChange_IntraTreatment_{freq_range}"].apply(list).to_dict()
        result = get_stat_test_string(data_dict, ttest_independent, left_width=50, right_width=30)
        
        ax = fig.get_axes()[idx_ipsicontra]
        ax.text(
            x=0, y=-.4,
            s = result,
            ha='left', va='top',
            transform = ax.transAxes,
            fontsize=8,
        ) 
    
    
    fig.suptitle(f"PowerMean Percentage Change (Normalized to IntraTreatment baseline) - freq_range = {freq_range}")
    fig.set_layout_engine('constrained')

    return fig
    
def plot_freqRange_powerMean_percentageChange_of_treatment1_2_normalized_intratreatment_split_by_treatment_order(df_all, freq_range):
    """Plot the power-mean percentage change of treatment-1 and treatment-2 normalized to intra-treatment baseline, and furhter split by treatment order."""
    df = df_all
    
    row_order=["dbs_off,all_on,rvs", "dbs_off,rvs,all_on"]
    col_order=["contra", "ipsi"]
    grouped = df.groupby(["TreatmentOrder", "IpsiContra"])
    target_colname = f"PowerMean_PercentageChange_IntraTreatment_{freq_range}"

    fg = sns.FacetGrid(
        df,
        col = "IpsiContra",
        row = "TreatmentOrder",
        row_order=row_order,
        col_order=col_order,
        height=5,
        aspect=1.1,
    )

    fg.map_dataframe(
        sns.violinplot,
        x="TreatmentNumber", 
        y=target_colname, 
        # hue="TreatmentBranch",
        inner = None,
        alpha=.4,
    )
    
    fg.map_dataframe(
        sns.swarmplot,
        x="TreatmentNumber", 
        y=target_colname, 
        # hue="TreatmentBranch",
        color='C2', 
        # alpha=.4,
        dodge=True,
        size=3,
    )
    fg.map_dataframe(
        sns.pointplot,
        x="TreatmentNumber", 
        y=target_colname, 
        # hue="TreatmentBranch",
        color='C3', 
        # alpha=.4,
        dodge=True,
        zorder = 3,
        errorbar = 'sd',
    )

    fig = fg.figure
    axs = fig.get_axes()
    
    for idx_ax, group_key in enumerate([(row_item, col_item) for row_item in row_order for col_item in col_order]):
        
        ax = axs[idx_ax]
        data_dict = grouped.get_group(group_key).groupby("TreatmentNumber")[target_colname].apply(list).to_dict()
        
        
        # Wilcoxon
        result = get_stat_test_string(
            data_dict,
            wilcoxon_ind,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.2,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
        # t-test
        result = get_stat_test_string(
            data_dict,
            ttest_independent,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.4,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
        
    fig.suptitle(f"PowerMean Percentage Change (Normalized to IntraTreatment baseline) - freq_range = {freq_range}")
    fig.set_layout_engine('constrained')

    return fig

def plot_all_hemi_type_intra(df_all, freq_range):
    """Plot power-mean percentage-change normalized to intra-treatment baseline, and split by treatment-type for each hemisphere.

    This plot looks at the average power-mean percentage-change for each of the 
    treatment type regardless whether they were administered as the first or
    second treatment.
    
    It is normalized by the intra-treatment baseline, which is defined as the
    avg of the first three session of the respective treatment type (i.e., rvs, 
    or all-on).
    
    TODO: Check if the definition of the intra-treatment baseline
    """

    category_colname ="TreatmentBranch"
    split_colname = "IpsiContra"
    value_colname =f"PowerMean_PercentageChange_IntraTreatment_{freq_range}"
    figure_super_title = f"Percentage Change of Power Mean for freq_range={freq_range} Split by Hemisphere and Treatment type"
    
    col_order = df_all[split_colname].unique()

    fg = sns.FacetGrid(
        df_all,
        col = split_colname,
        col_order=col_order,
        height=5,
    )

    fg.map_dataframe(
        sns.swarmplot,
        x=category_colname,
        y=value_colname,
        hue="TreatmentNumber",
        size=3,

    )
    
    fg.map_dataframe(
        sns.violinplot,
        x=category_colname,
        y=value_colname,
        inner=None,
        alpha=.4,
    )
    
    fg.map_dataframe(
        sns.pointplot,
        x=category_colname,
        y=value_colname,
        color='C3', 
        errorbar='sd',
        alpha=.5,
        linestyles="none",
        zorder=3,
    )

    grouped = df_all.groupby(split_colname)

    fig = fg.figure
    fig.suptitle(figure_super_title)
    
    axs = fig.get_axes()
    
    for ax, hemi in zip(axs, col_order):
        baseline_mean = df_all.query(f"({category_colname} == 'dbs_off') & ({split_colname} == '{hemi}')").loc[:, value_colname].mean()
        ax.hlines(baseline_mean, -.5, 2.5, colors='green')
    
        data_dict = grouped.get_group(hemi).groupby(category_colname)[value_colname].apply(list).to_dict()

        # Wilcoxon
        result = get_stat_test_string(
            data_dict,
            wilcoxon_ind,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.2,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
        # t-test
        result = get_stat_test_string(
            data_dict,
            ttest_independent,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.4,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
    
    fig.set_layout_engine('constrained')
    return fig

def plot_all_hemi_type_inter(df_all, freq_range):
    """Plot power-mean percentage-change normalized to inter-treatment baseline, and split by treatment-type for each hemisphere.

    This plot looks at the average power-mean percentage-change for each of the 
    treatment type regardless whether they were administered as the first or
    second treatment.
    
    It is normalized by the inter-treatment baseline, which is defined as the
    average of the 4th, 5th, and 6th, recording session of the dbs-off stage.
    
    TODO: Check if the definition of the inter-treatment baseline
    """

    category_colname ="TreatmentBranch"
    split_colname = "IpsiContra"
    value_colname =f"PowerMean_PercentageChange_InterTreatment_{freq_range}"
    figure_super_title = f"Percentage Change of Power Mean for freq_range={freq_range} Split by Hemisphere and Treatment type"
    
    col_order = df_all[split_colname].unique()

    fg = sns.FacetGrid(
        df_all,
        col = split_colname,
        col_order=col_order,
        height=5,
    )

    fg.map_dataframe(
        sns.swarmplot,
        x=category_colname,
        y=value_colname,
        hue="TreatmentNumber",
        size=3,

    )
    
    fg.map_dataframe(
        sns.violinplot,
        x=category_colname,
        y=value_colname,
        inner=None,
        alpha=.4,
    )
    
    fg.map_dataframe(
        sns.pointplot,
        x=category_colname,
        y=value_colname,
        color='C3', 
        errorbar='sd',
        alpha=.5,
        linestyles="none",
        zorder=3,
    )

    grouped = df_all.groupby(split_colname)

    fig = fg.figure
    fig.suptitle(figure_super_title)
    
    axs = fig.get_axes()
    
    for ax, hemi in zip(axs, col_order):
        baseline_mean = df_all.query(f"({category_colname} == 'dbs_off') & ({split_colname} == '{hemi}')").loc[:, value_colname].mean()
        ax.hlines(baseline_mean, -.5, 2.5, colors='green')
    
        data_dict = grouped.get_group(hemi).groupby(category_colname)[value_colname].apply(list).to_dict()
        print(data_dict)

        # Wilcoxon
        result = get_stat_test_string(
            data_dict,
            wilcoxon_ind,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.2,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
        # t-test
        result = get_stat_test_string(
            data_dict,
            ttest_independent,
            left_width=50, 
            right_width=30,
        )
        ax.text(
            x=0, y=-.4,
            s=result,
            ha='left', va='top',
            transform=ax.transAxes,
            fontsize=8,
        )
    
    fig.set_layout_engine('constrained')
    return fig