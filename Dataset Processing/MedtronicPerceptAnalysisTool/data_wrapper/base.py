# Wrappers for the patient datasets
# Anthony Lee 2024-12-27
#
# The reason for wrapping the patient dataset is that each of them require unique transformation
# and this method documents how each of the dataset is uniquely transformed.

import logging
import json
from typing import Union
from pathlib import Path
import abc
import pandas as pd
import numpy as np
from .base_support import (
    add_column_PSD,
    convert_firstpacketdatetime_to_datetime_obj,
    add_treatment_branch_column,
    remove_non_standard_sessions_based_on_treatment_branch,
    add_recordinghemisphere_column_based_on_channel,
    add_treatmentorder_column,
    add_column_treatment_number,
    add_ipsicontra_column,
    add_column_of_xarray_lfp_data,
    add_column_PSD_Baseline_InterTreatment,
    add_column_PSD_Baseline_IntraTreatment,
    add_column_PowerMean,
    add_column_PowerMean_Baseline_InterTreatment,
    add_column_PowerMean_Baseline_IntraTreatment,
    add_column_PowerMean_PercentageChange_InterTreatment,
    add_column_PowerMean_PercentageChange_IntraTreatment,
    reorder_columns,
    add_column_burst_detection_array_and_stats,
)
from ..utility.constants import (
    ColumnNames_Main,
    FrequencyRange,
)

logger = logging.getLogger(__name__)


class PatientObjAbstractBase(abc.ABC):
    @abc.abstractmethod
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir: Path = Path(data_dir)
        self.stage_mapping: dict = None
        self.glove_hand: str = None
        self.json_filenames: list = None
        self.updrs_filename: str = None

    def get_dataframe_json(self) -> pd.DataFrame:
        """Get a dataframe of all the JSON output for the patient.

        This method normalize all the JSON files of the patient into one
        dataframe to make it convenient to parse through the highest level JSON
        keys. To reduce dataframe fragmentation, the normalization only
        normalize to the first level of the nested JSON.
        """

        json_parse_max_depth = 0
        json_paths = list(
            self.data_dir.glob(
                "Report_Json_Session_Report_*.json", case_sensitive=False
            )
        )
        datetime_colnames = ["SessionDate", "SessionEndDate"]
        sort_colname = datetime_colnames[0]
        holder_df = []
        filenames = [filename.name for filename in json_paths]

        for json_path in json_paths:
            with open(json_path, "r") as fp:
                df = pd.json_normalize(json.load(fp), max_level=json_parse_max_depth)
                holder_df.append(df)

        result = pd.concat(holder_df, axis=0)

        for datetime_colname in datetime_colnames:
            result.loc[:, datetime_colname] = pd.to_datetime(
                result.loc[:, datetime_colname]
            )

        result.insert(0, "PatientNumber", self.patient_num)
        result.insert(1, "Filename", filenames)

        result = result.sort_values(by=sort_colname).reset_index(drop=True)
        return result

    def get_dataframe_groups(
        self,
    ) -> pd.DataFrame:
        """Convert all 'Groups' information into a dataframe

        In Medtronic Percept, all the settings are stored in groups A, B, C, D
        and when the study is conducted, one of the unused groups is used for
        the study and thus the BrainSense setup data is stored within the group
        that was used.
        """

        df = self.get_dataframe_json()
        colname_groups_from_json = "Groups"
        colname_patient_number = "PatientNumber"
        colname_filename = "Filename"
        colname_initial_final = "InitialOrFinalState"
        colname_groups = "GroupData"
        holder_patient_number = []
        holder_filename = []
        holder_initial_final = []
        holder_df = []

        for named_tuple in df.itertuples():
            # The initial and final are dict keys thus unable to use explode and keep the values
            result = pd.json_normalize(getattr(named_tuple, colname_groups_from_json))
            result = pd.melt(
                result, var_name=colname_initial_final, value_name=colname_groups
            )
            result = result.explode(column=colname_groups)

            holder_patient_number.extend(
                np.repeat(getattr(named_tuple, colname_patient_number), result.shape[0])
            )
            holder_filename.extend(
                np.repeat(getattr(named_tuple, colname_filename), result.shape[0])
            )
            holder_initial_final.extend(result.loc[:, colname_initial_final])

            for group_row in result.loc[:, colname_groups]:
                holder_df.append(pd.json_normalize(group_row))

        result_combined = pd.concat(holder_df, axis=0)
        result_combined.insert(0, colname_patient_number, holder_patient_number)
        result_combined.insert(1, colname_filename, holder_filename)
        result_combined.insert(2, colname_initial_final, holder_initial_final)

        return result_combined

    def get_dataframe_brainSenseSetup_psd(self) -> pd.DataFrame:
        """Get the BrainSense setup result for ALL electrode-pair from "MostRecentInSessionSignalCheck" (PSD).

        BrainSense setup result is stored in "MostRecentInSessionSignalCheck",
        "SenseChannelTests", and in "Groups". The differences are:

        - "MostRecentInSessionSignalCheck": Stores ALL electrode-pair LFP PSD results.
        - "SenseChannelTests": Stores ALL electrode-pair time-domain data.
        - "Groups": Stores ONLY the electrode-pair used's LFP PSD result.

        The easiest way to find them is to search for "SignalPsdValues" in the
        JSON files.

        For Medtronic Percept in-built artifact detection result, see the
        "ArtifactStatus" column.

        Patient 1 does not have 'MostRecentInSessionSignalCheck' thus use the
        data stored under 'Groups' instead by using `get_dataframe_brainSenseSetup_groups`.
        """

        colname_signal_check_psd = "MostRecentInSessionSignalCheck"
        colname_to_keep = ["PatientNumber", "Filename"]
        patient_number_list_missing_data = [
            1,
        ]

        if self.patient_num in patient_number_list_missing_data:
            raise NotImplementedError(
                f"Patient {self.patient_num}'s JSON files do not have data for {colname_signal_check_psd}, use 'get_dataframe_brainSenseSetup_groups' instead."
            )

        df = self.get_dataframe_json()

        if colname_signal_check_psd not in df.columns:
            raise KeyError(f"{colname_signal_check_psd} mising from the dataframe.")

        result = df.explode(colname_signal_check_psd)
        mask_notna_row = result.loc[:, colname_signal_check_psd].notna()
        if sum(mask_notna_row) == 0:
            raise ValueError(
                f"The dataframe has no data in the {colname_signal_check_psd} column."
            )
        result = result.loc[
            mask_notna_row,
            colname_to_keep
            + [
                colname_signal_check_psd,
            ],
        ]
        result = result.reset_index(drop=True)

        result = pd.concat(
            [
                result.loc[:, colname_to_keep],
                pd.concat(
                    [
                        pd.json_normalize(row)
                        for row in result.loc[:, colname_signal_check_psd]
                    ],
                    axis=0,
                    ignore_index=True,
                ),
            ],
            axis=1,
            # ignore_index=True
        )

        result["ArtifactStatus"] = result["ArtifactStatus"].apply(
            lambda cell: cell.split(".")[1]
        )
        result["Channel"] = result["Channel"].apply(lambda cell: cell.split(".")[1])
        return result

    def get_dataframe_brainSenseSetup_timeDomain(self) -> pd.DataFrame:
        """Get the BrainSense setup result for ALL electrode-pair from "SenseChannelTests" (time domain data).

        BrainSense setup result is stored in "MostRecentInSessionSignalCheck",
        "SenseChannelTests", and in "Groups". The differences are:

        - "MostRecentInSessionSignalCheck": Stores ALL electrode-pair LFP PSD results.
        - "SenseChannelTests": Stores ALL electrode-pair time-domain data.
        - "Groups": Stores ONLY the electrode-pair used's LFP PSD result.

        The easiest way to find them is to search for "SignalPsdValues" in the
        JSON files.

        Patient 1 does not have 'MostRecentInSessionSignalCheck' thus use the
        data stored under 'Groups' instead by using `get_dataframe_brainSenseSetup_groups`.
        """
        colname_signal_check_timeDomain = "SenseChannelTests"
        colname_to_keep = ["PatientNumber", "Filename"]
        patient_number_list_missing_data = [
            1,
        ]

        if self.patient_num in patient_number_list_missing_data:
            raise NotImplementedError(
                f"Patient {self.patient_num}'s JSON files do not have data for {colname_signal_check_timeDomain}, use 'get_dataframe_brainSenseSetup_groups' instead."
            )

        df = self.get_dataframe_json()

        if colname_signal_check_timeDomain not in df.columns:
            raise KeyError(
                f"{colname_signal_check_timeDomain} mising from the dataframe."
            )

        result = df.explode(colname_signal_check_timeDomain)
        mask_notna_row = result.loc[:, colname_signal_check_timeDomain].notna()
        if sum(mask_notna_row) == 0:
            raise ValueError(
                f"The dataframe has no data in the {colname_signal_check_timeDomain} column."
            )
        result = result.loc[
            mask_notna_row,
            colname_to_keep
            + [
                colname_signal_check_timeDomain,
            ],
        ]
        result = result.reset_index(drop=True)
        result = pd.concat(
            [
                result.loc[:, colname_to_keep],
                pd.concat(
                    [
                        pd.json_normalize(row)
                        for row in result.loc[:, colname_signal_check_timeDomain]
                    ],
                    axis=0,
                    ignore_index=True,
                ),
            ],
            axis=1,
            # ignore_index=True
        )

        result["FirstPacketDateTime"] = pd.to_datetime(result["FirstPacketDateTime"])
        return result

    def get_dataframe_brainSenseSetup_groups(self) -> pd.DataFrame:
        """Get the BrainSense setup result for the electrode-pair used from the 'Groups' record


        BrainSense setup tests all pairs of electrodes for each probe, thus for
        a three-electrode probe, there will be three electrode pairs (AB, BC,
        and AC). Even though all pairs are tested during the BrainSense setup,
        only the one pair that is used for each group thus only one pair will be
        saved in the 'Groups' records.

        - "MostRecentInSessionSignalCheck": Stores ALL electrode-pair LFP PSD results.
        - "SenseChannelTests": Stores ALL electrode-pair time-domain data.
        - "Groups": Stores ONLY the electrode-pair used's LFP PSD result.

        For lead configuration details such as built-in high-pass filter, this
        function parses the data from the 'Groups' section.

        Patient 9 and 10 data files do not have the BrainSense setup results
        under the 'Groups' key, thus use the 'get_dataframe_brainSenseSetup_psd'
        instead (or use `get_dataframe_brainSenseSetup_timeDomain` for the
        time-domain raw data.)

        """
        colname_sensing_setup = "ProgramSettings.SensingChannel"
        colname_sort = ["Filename", "GroupId", "InitialOrFinalState"]
        df = self.get_dataframe_groups()

        patient_number_list_missing_data = [9, 10]

        if self.patient_num in patient_number_list_missing_data:
            raise NotImplementedError(
                f"Patient {self.patient_num}'s JSON files do not have data for {colname_sensing_setup}, use 'get_dataframe_brainSenseSetup_psd' or 'get_dataframe_brainSenseSetup_timeDomain' instead."
            )

        if colname_sensing_setup not in df.columns:
            raise KeyError(
                f"Column not found - {colname_sensing_setup} not found in dataframe columns."
            )

        df = df.explode(column=colname_sensing_setup)
        df = df.loc[df[colname_sensing_setup].notna(), :]

        holder_df = [pd.json_normalize(row) for row in df.loc[:, colname_sensing_setup]]
        holder_df = pd.concat(holder_df, axis=0, ignore_index=False)

        df = df.drop(colname_sensing_setup, axis=1)

        result = pd.concat([df, holder_df], axis=1, ignore_index=False)
        result = result.sort_values(colname_sort)
        result = result.reset_index(drop=True)
        return result

    def get_dataframe_brainSenseTimeDomain(self) -> pd.DataFrame:
        """Return a dataframe of the "BrainSenseTimeDomain" data sessions with additional metadata

        This function extracts the "BrainSenseTimeDomain" data from the JSON
        files, do various data cleaning and add metadata columns.
        """

        colname_data = "BrainSenseTimeDomain"
        holder_df = []
        df_all_jsons = self.get_dataframe_json()
        series_timedomain = df_all_jsons.loc[:, colname_data]
        series_timedomain_notna = series_timedomain[series_timedomain.notna()]

        for timedomain_to_parse in series_timedomain_notna:
            holder_df.append(pd.json_normalize(timedomain_to_parse))

        df = pd.concat(holder_df, axis="index")
        df = convert_firstpacketdatetime_to_datetime_obj(df)
        df = add_treatment_branch_column(df, self.stage_mapping)
        df = remove_non_standard_sessions_based_on_treatment_branch(df)
        # df = add_patient_number_column(df, self.__class__.__name__)
        df.insert(0, "PatientNumber", self.patient_num)

        # Preserve the session number per patient by creating a new column
        # df = df.reset_index(drop=False, names="SessionNumber")
        # reordered_colnames = [df.columns[-1]] + df.columns[:-1].to_list()
        # df = df.loc[:, reordered_colnames]

        df[ColumnNames_Main.stimglovehand] = self.glove_hand
        df = add_recordinghemisphere_column_based_on_channel(df)
        df = add_treatmentorder_column(df, self.treatment_order)
        df = add_column_treatment_number(df)
        df = add_ipsicontra_column(df)
        df = df.sort_values(["FirstPacketDateTime", "Channel"]).reset_index(drop=True)

        df = add_column_of_xarray_lfp_data(df)

        # warnings.warn("TEMP MODIFICATION OF TIMEDOMAINDATA SIGNAL - 2025-12-07")
        # ecg_artifact_removed_series = df.TimeDomainData.apply(lambda cell: remove_ECG_artifacts(np.array(cell), sampling_rate=250))
        # # df["ECG_artifact_filtered"] = ecg_artifact_removed_series
        # df["TimeDomainData"] = ecg_artifact_removed_series

        return df

    def get_dataframe_lfp(self) -> pd.DataFrame:
        freq_ranges = [
            FrequencyRange.Beta.value,
            FrequencyRange.LowBeta.value,
            FrequencyRange.HighBeta.value,
        ]

        df = self.get_dataframe_brainSenseTimeDomain()

        # Add PSD columns - Medtronic range
        freq_range = FrequencyRange.MedtronicPerceptRange.value
        df = add_column_PSD(df, freq_range)

        df = add_column_PSD_Baseline_InterTreatment(df)
        df = add_column_PSD_Baseline_IntraTreatment(df)

        # Add Power mean columns
        for freq_range in freq_ranges:
            df = add_column_PowerMean(df, freq_range)

            df = add_column_PowerMean_Baseline_InterTreatment(df, freq_range=freq_range)
            df = add_column_PowerMean_Baseline_IntraTreatment(df, freq_range=freq_range)

            df = add_column_PowerMean_PercentageChange_InterTreatment(
                df, freq_range=freq_range
            )
            df = add_column_PowerMean_PercentageChange_IntraTreatment(
                df, freq_range=freq_range
            )

        df = reorder_columns(df)

        return df

    def get_dataframe_burst(self) -> pd.DataFrame:
        freq_ranges = [
            FrequencyRange.Beta.value,
            FrequencyRange.LowBeta.value,
            FrequencyRange.HighBeta.value,
        ]

        df = self.get_dataframe_brainSenseTimeDomain()

        for freq_range in freq_ranges:
            df = add_column_burst_detection_array_and_stats(df, freq_range=freq_range)

        return df

    def get_dataframe_pac(self) -> pd.DataFrame:
        raise NotImplementedError

    def get_dataframe_updrs(self, summary=False) -> pd.DataFrame:
        treatment_order = tuple(self.treatment_order.split(","))
        assert len(treatment_order) == 3
        mapper = {
            "Baseline": treatment_order[0],
            "Treatment 1": treatment_order[1],
            "Treatment 2": treatment_order[2],
        }

        def process_sub_category_2(input: str) -> str:
            assert isinstance(input, str), "Input has to be a string"

            input = input.split(".")

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

        df["Category"] = df["Item Number"].apply(lambda x: str(x).split(".")[0])
        df["Sub-category-1"] = df["Item Number"].apply(lambda x: str(x).split(".")[1])
        df["Sub-category-2"] = df["Item Number"].apply(
            lambda x: process_sub_category_2(str(x))
        )
        df.loc[df["Sub-category-2"].isna(), "Sub-category-2"] = "Body"

        if summary:
            pivoted = df.pivot_table(
                index=["Sub-category-2"],
                columns="Stage",
                values="Score",
                aggfunc="mean",
                dropna=False,
            )
            # new_col_order = [treatment for treatment in treatment_order if treatment in pivoted.columns.to_list()]
            # pivoted = pivoted.loc[:, new_col_order]
            pivoted = pivoted.loc[:, treatment_order]
            pivoted.columns = pd.MultiIndex.from_product(
                (["UPDRS mean"], pivoted.columns.to_list())
            )
            # pivoted = pivoted.loc[new_index_order, :]
        else:
            pivoted = df.pivot(
                index=[
                    "Category",
                    "Sub-category-1",
                    "Sub-category-2",
                    "Item Number",
                    "Item Description",
                ],
                columns="Stage",
                values=["Score"],
            ).sort_index(level=[0, 1], ascending=True)

            new_col_order = pd.MultiIndex.from_arrays(
                [["Score"] * len(treatment_order), treatment_order]
            )
            pivoted = pivoted.loc[:, new_col_order]

        return pivoted

    def get_dataframe_signalcheck(self) -> pd.DataFrame:
        raise NotImplementedError

    @property
    def patient_num(
        self,
    ):
        classname = self.__class__.__name__
        if "abstract" in classname.lower():
            raise RuntimeError("Should not be called from the abstract base class.")

        return int(classname.split("_")[1])
