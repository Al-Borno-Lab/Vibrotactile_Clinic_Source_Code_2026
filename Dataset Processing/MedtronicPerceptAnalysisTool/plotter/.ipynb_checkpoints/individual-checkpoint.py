import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from ..utility.constants import FrequencyRange
from ..utility.stats import get_stat_test_string, wilcoxon_ind, ttest_ind, anova_test
from scipy.stats import f_oneway
import inspect


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
