## 2025-01-20 Anthony Lee

## Wrappers for the patient datasets
## Anthony Lee 2024-12-27
##
## The reason for wrapping the patient dataset is that each of them require unique transformation
## and this method documents how each of the dataset is uniquely transformed.

# TODO: Write test function to throw errors when data only has single hemiphere data and plot_lfp_psd does not throw an error.
# TODO: Glob only files that has data (what is hardcoded) and ignore the rest (because the provided data dir may have other jsons.)

from typing import Protocol, Union, Iterable, Tuple, Dict, List
from collections.abc import Iterable
from pathlib import Path
from abc import abstractmethod
import pandas as pd
import numpy as np
import json
import numpy.typing as npt
from ..utility import PROTOCOL_STAGES
from ..filter.iir import IIR_butterworth_filter_hammer_2022
from ..spectral.psd import psd_welch_contaldi_2023, psd_welch_gilron_2021
from ..plot import plot_session_start_times
from ..plot import plot_both_hemisphere_lfp_psd
import warnings
import matplotlib.pyplot as plt

def parse_BrainSenseTimeDomain_from_path(json_path: Path) -> pd.DataFrame:

    with open(json_path, "r") as file:
        unserialized_dict = json.load(file)
        output_df = pd.json_normalize(
            data=unserialized_dict,
            record_path=["BrainSenseTimeDomain"],
            meta=[
                "ProgrammerUtcOffset",
                "ProgrammerVersion",
                "BatteryInformation",
                "LeadConfiguration",
                "Impedance",
            ],
            meta_prefix="Metadata.",
        )

    return output_df

def add_stage(df_lfp:pd.DataFrame, mapping_stage_to_range:Dict)->pd.DataFrame: 
    
    df = df_lfp
    mapping = {}

    for key, value in mapping_stage_to_range.items(): 
        for item in value: 
            mapping[ str(item) ] = key

    df.loc[:, "TreatmentBranch"] = [mapping[str(num)] for num in df.index.to_numpy()]
    
    return df

class Patient_Dataset_Base:
    
    @abstractmethod
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir: Path = Path(data_dir)
        self.stage_mapping: dict = None
        self.glove_hand: str = None
        self.json_filenames: list = None
        self.updrs_filename: str = None

    def get_dataframe(self) -> pd.DataFrame:
        json_filepaths = self._convert_filenames_to_filepaths(
            data_dir=self.data_dir, 
            json_filenames=self.json_filenames,
        )
        return self._process_lfp(json_filepaths)
    
    def get_dataframe_updrs(self, summary=None) -> pd.DataFrame:
        """
        
        Args
        ====
        summary (bool): Indicate whether to return a summarized dataframe.
        
        """

        if summary is None: 
            summary=False

        # TODO: Find another way to get treatment order such that not repeatedly calling get_dataframe.
        treatment_order = self.get_dataframe().loc[0, "TreatmentOrder"].split(',')
        assert len(treatment_order) == 3
        mapper = {
            "Baseline": treatment_order[0],
            "Treatment 1": treatment_order[1], 
            "Treatment 2": treatment_order[2],
        }

        def process_sub_category_2(input:str) -> str:
            assert isinstance(input, str), "Input has to be a string"
            
            input = input.split('.')
            
            match len(input):
                case 3:
                    return input[2]
                case 2:
                    return
                case _:
                    raise ValueError
        
        data_path = self.data_dir / Path(self.updrs_filename)
        df = pd.read_excel(data_path)
        df["Stage"] = df["Stage"].map(mapper)

        df["Category"] = df["Item Number"].apply(lambda x: str(x).split('.')[0])
        df["Sub-category-1"] = df["Item Number"].apply(lambda x: str(x).split('.')[1])
        df["Sub-category-2"] =  df["Item Number"].apply(lambda x: process_sub_category_2(str(x)))
        df.loc[df["Sub-category-2"].isna(), "Sub-category-2"] = "Body"
        
        if summary:
            pivoted = df.pivot_table(index=["Sub-category-2"], columns="Stage", values="Score", aggfunc="mean", dropna=False)
            # new_col_order = [treatment for treatment in treatment_order if treatment in pivoted.columns.to_list()]
            # pivoted = pivoted.loc[:, new_col_order]
            pivoted = pivoted.loc[:, treatment_order]
            pivoted.columns = pd.MultiIndex.from_product((["UPDRS mean"], pivoted.columns.to_list()))
            # pivoted = pivoted.loc[new_index_order, :]
        else:
            pivoted = df.pivot(
                index=["Category", "Sub-category-1", "Sub-category-2", "Item Number", "Item Description"],
                columns="Stage", 
                values=["Score"]
            ).sort_index(level=[0, 1], ascending=True)
            
            new_col_order = pd.MultiIndex.from_arrays([["Score"]*len(treatment_order), treatment_order])
            pivoted = pivoted.loc[:, new_col_order]

        return pivoted

    def __len__(self) -> int:
        raise NotImplementedError

    def _getitem__(self, index:int) -> pd.Series:
        raise NotImplementedError
    
    @staticmethod
    def _bandpass_filter(data:npt.NDArray, freqRange:tuple[float|int, float|int], fs:float|int ) -> Tuple[npt.NDArray, npt.NDArray]:
        """Delegates the calculation to IIR filter with param specified by (Hammer, 2022)."""

        if not isinstance(data, np.ndarray):
            raise TypeError(f"'data' is required to be ndarray, got {type(data)}")
        if (not isinstance(freqRange, tuple)) | (len(freqRange) != 2):
            raise ValueError(f"'freqRange' is required to be of type Tuple and have length of two, got {type(freqRange)} and length {len(freqRange)}")

        filteredSigData = IIR_butterworth_filter_hammer_2022(data=data, freqRange=freqRange, fs=fs)
        return filteredSigData
    
    @staticmethod
    def _calculate_psd(data:npt.NDArray, fs:float|int) -> tuple[npt.NDArray, npt.NDArray]:
        """Delegates the calculation to Welch periodogram with parameters specified by (Contaldi, 2023)."""

        if not isinstance(data, np.ndarray):
            raise TypeError(f"'data' is required to be ndarray, got {type(data)}")

        freq, psd = psd_welch_contaldi_2023(data=data, fs=fs)
        return (freq, psd)


    # TODO: Fix this internal method call of creating paths when subclassing this class. Prevent the case when users forget to call this internal method.
    def _convert_filenames_to_filepaths(self, data_dir:str|Path, json_filenames:Iterable[str|Path]) -> Iterable[Path]:
       return [( Path(data_dir) / Path(json_path)).resolve() for json_path in json_filenames]


    def get_initial_dict(self, freqRange:tuple[float|int, float|int]=(1, 100), fs:float|int=250, nFirstSessions:int=1) -> Dict[str, Tuple[npt.NDArray, npt.NDArray]]:
        df = self.get_dataframe()

        # Filter for just dbs_off sessions
        df = df.loc[(df["TreatmentBranch"] == "dbs_off"), :]
        grouped = df.groupby(by=["TreatmentBranch", "Channel"])  # groupby with single element raises warning when using get_group()

        holder_channel = {}

        # Go through each group, which is each channel for the DBS-off stage.
        # Channel is synonymous for the hemisphere of the DBS.
        for group in grouped.groups:
            treatment_branch, channel_name = group
            last_n_dbs_off = grouped.get_group(group).head(nFirstSessions)
            lfps = last_n_dbs_off["TimeDomainData"]

            holder_last_n_sessions = []
            for lfp in lfps:
                lfp = np.array(lfp)
                # Bandpass
                lfp  = self._bandpass_filter(data=lfp, freqRange=freqRange, fs=fs)
                # PSD calculation
                freq, psd = self._calculate_psd(data=lfp, fs=fs)
                holder_last_n_sessions.append(psd)

            holder_last_n_sessions = np.array(holder_last_n_sessions)
            baseline_psd = holder_last_n_sessions.mean(axis=0)  # Averaged across the nLastSessions 

            holder_channel[channel_name] = (freq, baseline_psd)
        
        return holder_channel
        
    def get_baseline_dict(self, freqRange:tuple[float|int, float|int]=(1, 100), fs:float|int=250, nLastSessions:int=1) -> Dict[str, Tuple[npt.NDArray, npt.NDArray]]:
        """Return a dictionary of the baseline PSD for each recording channel.
        
        Baseline is defined as the last three sessiosn of the DBS_off period. The
        LFP signal is bandpassed at freq range of (1, 100) instead of (1, 125) to
        prevent band transition effect towards the end of the useable spectrum.

        PSD is calculated and then averaged across the three sessions for each
        channel.

        Args
        ----
        df: DataFrame of a single patient
        freqRange: The freq range for the bandpass (inclusive).
        fs: Sampling frequency of the signal data.
        """
        df = self.get_dataframe()

        # Filter for just dbs_off sessions
        df = df.loc[(df["TreatmentBranch"] == "dbs_off"), :]
        grouped = df.groupby(by=["TreatmentBranch", "Channel"])  # groupby with single element raises warning when using get_group()

        holder_channel = {}

        # Go through each group, which is each channel for the DBS-off stage.
        # Channel is synonymous for the hemisphere of the DBS.
        for group in grouped.groups:
            treatment_branch, channel_name = group
            last_n_dbs_off = grouped.get_group(group).head(nLastSessions)
            lfps = last_n_dbs_off["TimeDomainData"]

            holder_last_n_sessions = []
            for lfp in lfps:
                lfp = np.array(lfp)
                # Bandpass
                lfp  = self._bandpass_filter(data=lfp, freqRange=freqRange, fs=fs)
                # PSD calculation
                freq, psd = self._calculate_psd(data=lfp, fs=fs)
                holder_last_n_sessions.append(psd)

            holder_last_n_sessions = np.array(holder_last_n_sessions)
            baseline_psd = holder_last_n_sessions.mean(axis=0)  # Averaged across the nLastSessions 

            holder_channel[channel_name] = (freq, baseline_psd)
        
        return holder_channel



    def _get_dataframe_with_psd_norm(self, freqRanges=[(1, 50)], fs=250):
        """Convenience function - API could change!"""

        warnings.warn("This is a private API and is subject to change!", UserWarning)

        colname_channel = "Channel"
        colname_lfp_data = "TimeDomainData"
        
        colname_prefix = "BaselineNormalizedMeanPSD"
        holder_result_dict = {f"{colname_prefix}_{freqRange}":[] for freqRange in freqRanges}

        df = self.get_dataframe()

        for freqRange in freqRanges:
            baselines = self.get_initial_dict(freqRange=freqRange)
            for idx, data in df.loc[:, [colname_channel, colname_lfp_data]].iterrows():
                channel = data[colname_channel]
                lfp = np.array(data[colname_lfp_data])

                # Bandpass and PSD the LFP data
                filtered_lfp = self._bandpass_filter(data=lfp, freqRange=freqRange, fs=fs)
                sig_freq, sig_psd = self._calculate_psd(data=filtered_lfp, fs=fs)
                # Filter to the freqRange subset
                mask = (sig_freq >= freqRange[0]) & (sig_freq <= freqRange[1])
                sig_freq, sig_psd = sig_freq[mask], sig_psd[mask]

                # Baseline to compare against
                baseline_freq, baseline_psd = baselines[channel]
                # Filter to the freqRange subset
                mask = (baseline_freq >= freqRange[0]) & (baseline_freq <= freqRange[1])
                baseline_freq, baseline_psd = baseline_freq[mask], baseline_psd[mask]
                baseline_psd_mean = baseline_psd.mean()
                
                # Baselines should use the same filter and calculate_psd as specified by the delegators
                if (baseline_freq != sig_freq).any(): raise ValueError("The Spectral frequencies are not the same!")

                # Point div norm
                point_div_norm = sig_psd.mean() / baseline_psd_mean
                holder_result_dict[f"{colname_prefix}_{freqRange}"].append(point_div_norm)

        dfPsd = pd.DataFrame(holder_result_dict)

        combined = pd.concat([df, dfPsd], axis=1)
        return combined







    def _process_lfp(self, json_filepaths: Iterable[Path]) -> pd.DataFrame:
        
        # Process each of the json files        
        df_holder = []
        for json_filepath in json_filepaths:
            df = parse_BrainSenseTimeDomain_from_path(json_path=json_filepath)
            df_holder.append(df)
        # Merge the df
        df = pd.concat(df_holder, axis="index").reset_index(drop=True)  # New index

        # Add treatment branch info in a new column
        df = add_stage(df, self.stage_mapping)

        # Remove non-treatment sessions (such as marker, testing, or accidental recordings)
        mask_normal_treatmentbranches = df.TreatmentBranch.isin(PROTOCOL_STAGES)
        df = df.loc[mask_normal_treatmentbranches, :].reset_index(drop=False, names="OriginalSessionNumber")

        # Add patient number column
        patient_number = int(self.__class__.__name__.split("_")[1])
        df.loc[:, "PatientNumber"] = patient_number
        
        # Preserve the session number per patient by creating a new column
        df = df.reset_index(drop=False, names="SessionNumber")
        reordered_colnames = [df.columns[-1]] + df.columns[:-1].to_list()
        df = df.loc[:, reordered_colnames]

        # Add glove hand into the dataframe
        df["StimGloveHand"] = self.glove_hand

        # Add hemisphere column
        for hemisphere in ["left", "right"]:        
            mask = df["Channel"].str.lower().str.contains(hemisphere)
            df.loc[mask, "RecordingHemisphere"] = hemisphere

        # # Add Treatment Branch Order
        # first_treatment = df.TreatmentBranch.unique()[1]  # Does NOT sort, according to documentation
        # df.loc[:, "FirstTreatment"] = first_treatment

        # Add Treatment Branch Order
        treatment_order = df.TreatmentBranch.unique().tolist()  # Does NOT sort, according to documentation
        df.loc[:, "TreatmentOrder"] = ",".join(treatment_order)
        
        # Convert datetime column to datetime
        df.loc[:, "FirstPacketDateTime"] = pd.to_datetime(df.FirstPacketDateTime, format="ISO8601")

        # Add IpsiContra column
        ipsicontra_mask = df.StimGloveHand == df.RecordingHemisphere
        df.loc[:, "IpsiContra"] = ipsicontra_mask.replace({True: "ipsi", False: "contra"})

        return df
    
    # def _num_of_files_with_timedomaindata(self) -> int:
    #     """Checks the number of files that have time domain data."""
    #     warnings.warn("This method will be removed soon as it does not work when the data directory contains other jsons.", DeprecationWarning, stacklevel=2)
    #     list_of_jsons = self.data_dir.glob("**/*.json")
    #     num_of_files = 0

    #     for json_path in list_of_jsons:
    #         with open(json_path, "r") as file: 
    #             unserialized_dict = json.load(file)
    #             keys = unserialized_dict.keys()
    #         if "BrainSenseTimeDomain" in keys:
    #             num_of_files += 1
        
    #     return num_of_files

    def _plot_session_start_times(self):
        df_lfp = self.get_dataframe()
        ax = plot_session_start_times(df_lfp=df_lfp)
        fig = ax.get_figure()
        fig.set_layout_engine(layout="tight")
        return fig
    
    # def _check_filepaths_and_num_of_jsons_match(self):
    #     pass

    def _bandpass_and_calculate_psd(self, freqRange:Tuple[float, float]=(1, 100), fs:int=250):
        json_filepaths = self._convert_filenames_to_filepaths(
            data_dir=self.data_dir,
            json_filenames=self.json_filenames,
        )
        df_lfp = self._process_lfp(json_filepaths)

        df_lfp[f"PsdFrequencies_{freqRange}"] = df_lfp.loc[:, "TimeDomainData"].apply(
            lambda data: (self._calculate_psd(
                data=self._bandpass_filter(data=np.array(data), freqRange=freqRange, fs=fs),
                fs=fs,
                )[0]
            )
        )
        df_lfp[f"Psd_{freqRange}"] = df_lfp.loc[:, "TimeDomainData"].apply(
            lambda data: (self._calculate_psd(
                data=self._bandpass_filter(data=np.array(data), freqRange=freqRange, fs=fs),
                fs=fs,
                )[1]
            )
        )
        return df_lfp

        
    def _plot_all_plots(self):
        from .. import plotter
        from datetime import datetime as dt
        from datetime import timezone as tz
        from pathlib import Path
       
        now = dt.now(tz=tz.utc)
        folder = Path(now.strftime("%Y-%m-%d"))
        # sub_folder = Path(now.strftime("%H:%M:%S"))
        sub_folder = Path(self.__class__.__name__)
        cwd = Path().cwd()

        destination = cwd / folder / sub_folder
        destination.mkdir(parents=True, exist_ok=True)
        
        jobs = [
            plotter.plot_recording_sessions_seconds, 
            plotter.plot_mean_beta_time_series,
            plotter.plot_mean_beta_psd_normalized,
            plotter.plot_boxplot_with_mean_beta,
            plotter.plot_boxplot_with_mean_low_beta,
            plotter.plot_boxplot_with_mean_high_beta,
            plotter.plot_lfp_and_psd,
            plotter.plot_spectrogram,
            plotter.plot_baseline_psd_of_each_channel,
            plotter.plot_full_beta_ipsi_contra_mean_psd,
            
            plotter.plot_updrs_averages,  # Keep this at the end because pt 10 doesn't have UPDRS data yet
        ]
        
        for idx, job in enumerate(jobs):
            fig = job(self)
            fig.savefig(destination / Path(f"{job.__name__}.svg"))
            plt.close()
        
        return







   ################################################################################ 
   ################################################################################ 
   ################################################################################ 
   ################################################################################ 
    # TODO: Fix this function as this is too specific to just the beta-band.
    # def _calculate_psd_sums(self, fs:float=250):
    #     df_lfp = self._bandpass_and_calculate_psd(freqRange=(12, 30), fs=fs)

    #     ## Calculate PSD sum
    #     df_psd_sums = (
    #         df_lfp.pivot_table(
    #             values=["PsdFrequencies_beta", "Psd_beta"], index=["TreatmentBranch", "Channel", "SessionNumber"]
    #         )["Psd_beta"]
    #         .apply(lambda psd: np.sum(psd))
    #         .sort_index(level=2)
    #     )
    #     return df_psd_sums

    # TODO: Fix this function as this is too specific to just the beta-band.
    # def _calculate_psd_means(self, fs:float=250):
    #     df_lfp = self._bandpass_and_calculate_psd(freqRange=(12, 30), fs=fs)
    #     df_psd_means = (
    #         df_lfp.pivot_table(
    #             values=["PsdFrequencies_beta", "Psd_beta"], index=["TreatmentBranch", "Channel", "SessionNumber"]
    #         )["Psd_beta"]
    #         .apply(lambda psd: np.mean(psd))
    #         .sort_index(level=2)
    #     )
    #     return df_psd_means

    # TODO: Fix this function as it is too specific to just the beta-band.
    # def _plot_boxplot_and_trend(self):
    #     df = self._calculate_psd_means()
    #     glove_hand = self.glove_hand
    #     stage_mapping = self.stage_mapping
    #     treatment_stages_alphabetized = sorted(PROTOCOL_STAGES)

    #     fig_boxplot, axs_boxplot = plt.subplots(1, 2, figsize=(10, 4))
    #     fig_trend, ax_trend = plt.subplots(1, 1, figsize=(10, 5))

    #     for channel in df.index.get_level_values(level=1).unique():
    #         if "left" in channel.lower():
    #             hemisphere = "left"
    #             idx_channel = 0
    #         elif "right" in channel.lower():
    #             hemisphere = "right"
    #             idx_channel = 1

    #         stage_data = []
    #         stage_names = []

    #         for treatment in df.index.get_level_values(level=0).unique():
    #             data = df.loc[(treatment, channel),]
    #             stage_data.append(data)
    #             stage_names.append(treatment)

    #         ## Check that the stage names are in the same order as the stage mapping dict
    #         if stage_names != [
    #             stage_name for stage_name in stage_mapping.keys() if stage_name in treatment_stages_alphabetized
    #         ]:
    #             raise ValueError(
    #                 "The unique stage names' order does not match that of the stage_mapping order. Either the pandas unique() method is broken or the stage_mapping dictionary is in the wrong order."
    #             )

    #         plot_boxplot(
    #             stage_data,
    #             stage_names,
    #             hemisphere,
    #             ax_title=f"Glove on {glove_hand} - mean - beta bandpass",
    #             ax=axs_boxplot[idx_channel],
    #         )
    #         plot_trend(
    #             stage_data,
    #             stage_names,
    #             hemisphere,
    #             label=channel,
    #             ax_title=f"Time Series Trend (Glove on {glove_hand})- beta bandpass",
    #             ax=ax_trend,
    #         )

    #     return fig_boxplot, fig_trend

    # TODO: Fix this plotting method such that it can accomodate for different hemisphere count of recordings.
    # def _plot_lfp_psd(self):
    #     import tempfile

    #     df_lfp = self._beta_bandpass_and_calculate_psd()

    #     temp_dir = tempfile.mkdtemp()
    #     session_numbers = df_lfp.index

    #     for session_num in session_numbers:
    #         if session_num % 2 == 0:  # left
    #             # Get LFP data
    #             y = df_lfp.loc[session_num, "TimeDomainData"]
    #             x = (1 / df_lfp.loc[session_num, "SampleRateInHz"] * 1000) * np.arange(len(y))  # 4 ms intervals
    #             treatment = df_lfp.loc[session_num, "TreatmentBranch"]
    #             left_lfp_data = (x, y)

    #             # Get PSD data
    #             y = df_lfp.loc[session_num, "Psd_beta"]
    #             x = df_lfp.loc[session_num, "PsdFrequencies_beta"]
    #             left_psd_data = (x, y)

    #         else:  # right
    #             # Get LFP data
    #             y = df_lfp.loc[session_num, "TimeDomainData"]
    #             x = (1 / df_lfp.loc[session_num, "SampleRateInHz"] * 1000) * np.arange(len(y))  # 4 ms intervals
    #             treatment = df_lfp.loc[session_num, "TreatmentBranch"]
    #             right_lfp_data = (x, y)

    #             # Get PSD data
    #             y = df_lfp.loc[session_num, "Psd_beta"]
    #             x = df_lfp.loc[session_num, "PsdFrequencies_beta"]
    #             right_psd_data = (x, y)

    #             # Plot - now got both left and right data
    #             axs = plot_both_hemisphere_lfp_psd(left_lfp_data, right_lfp_data, left_psd_data, right_psd_data)
    #             fig = axs[0].get_figure()
    #             super_title = f"Session {session_num-1} and {session_num} - {treatment} - beta bandpass"
    #             fig.suptitle(super_title, fontsize=60)
    #             # plt.show()

    #             ## Temp save
    #             fig.set_layout_engine(layout="tight")
    #             # fig.savefig(Path(temp_dir)/Path(f"{super_title}.svg"))
    #             # plt.close("all")
    #             # print(f"Find files in {temp_dir}")
    #     return fig