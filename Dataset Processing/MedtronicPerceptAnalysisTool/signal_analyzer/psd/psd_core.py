import logging
from ...data_wrapper.base import Patient_Dataset_Base as BasePatientObject
from ..base import BaseSignalAnalyzer
import pandas as pd
from ...signal_processor.filter import BandpassFilterProcessor
from ...signal_processor.psd import PowerSpectralDensityProcessor, PowerSpectralDensity
import numpy as np
import typing
from ...signal_processor.psd import PowerSpectralDensityProcessor
from ...signal_processor.filter import BandpassFilterProcessor
from ...signal_processor.filter import BandpassFilterProcessor
from ...signal_processor.psd import PowerSpectralDensityProcessor

logger = logging.getLogger(__name__)


def get_sampling_freq(patient_df: pd.DataFrame) -> int:
    """Convenience function"""
    sampling_rates = patient_df.SampleRateInHz
    assert (
        len(sampling_rates.unique()) == 1
    ), f"More than one sampling rate detected, should only have one sample rate but got the following unique rates: {sampling_rates.unique()}"

    result = int(sampling_rates.iloc[0])
    return result


class FrequencyRangePSDAnalyzer(BaseSignalAnalyzer):
    def __init__(self, freq_range: tuple, last_n_sessions:int = None, dest_colname: str = None):
        """Process signals into a PowerSpectralDensity object"""

        self.__freq_range = self.__validate_freq_range(freq_range)
        if dest_colname is None:
            dest_colname = f"PSD_{self.freq_range}"
        self.__dest_colname = self.__validate_dest_colname(dest_colname)
        self.__last_n_sessions = self.__validate_last_n_sessions(last_n_sessions)

    def __call__(self, patient_obj: BasePatientObject):
        patient_obj = self.__validate_input_type(patient_obj=patient_obj)
        df = patient_obj.get_dataframe()

        bandpass_filter_processor = BandpassFilterProcessor(freq_range=self.freq_range, sampling_freq=get_sampling_freq(df))
        psd_processor: PowerSpectralDensity = PowerSpectralDensityProcessor(sampling_freq=get_sampling_freq(df))

        def processing_pipeline(signal: typing.Iterable) -> PowerSpectralDensity:
            """Convenience lambda function."""

            signal = np.array(signal)
            signal = bandpass_filter_processor(signal)
            psd_obj: PowerSpectralDensity = psd_processor(signal)
            result = psd_obj.filter_freq_range(self.freq_range)
            return result

        data_colname = "TimeDomainData"
        sort_colname = "FirstPacketDateTime"
        filter_colname = "TreatmentBranch"
        dest_colname = self.__dest_colname

        result = (
            df.pivot(
                index=[
                    "PatientNumber",
                    "Channel",
                    "RecordingHemisphere",
                    "StimGloveHand",
                    "IpsiContra",
                    sort_colname,
                ],
                columns=filter_colname,
                values=data_colname,
            )
            .map(lambda signal_data: processing_pipeline(signal_data), na_action="ignore")
            .stack()
            .to_frame(name=dest_colname)
            .sort_values(sort_colname)
            .reset_index(drop=False)
        )

        # Return all sessions
        if self.last_n_sessions is None:
            return result
        # Return only the last n sessions
        else: 
            result = (result
                .sort_values(by=sort_colname)
                .groupby(
                    by = [
                        "PatientNumber",
                        "Channel",
                        "TreatmentBranch"
                    ]
                )
                .tail(self.last_n_sessions)
            )
            return result
            

    def __validate_input_type(self, patient_obj: BasePatientObject):
        if not isinstance(patient_obj, BasePatientObject):
            raise TypeError
        return patient_obj

    def __validate_dest_colname(self, dest_colname: str) -> str:
        if not isinstance(dest_colname, str):
            raise TypeError
        return dest_colname
    
    def __validate_freq_range(self, freq_range:tuple):
        if not isinstance(freq_range, tuple):
            raise TypeError
        if len(freq_range) != 2:
            raise TypeError
        return freq_range

    def __validate_last_n_sessions(self, last_n_sessions: int|None):
        if last_n_sessions is None:
            return
        if not isinstance(last_n_sessions, int):
            raise TypeError
        if last_n_sessions < 0: 
            raise ValueError
        if last_n_sessions > 6:
            raise ValueError
        return last_n_sessions

    @property
    def last_n_sessions(self):
        return self.__last_n_sessions
    @property
    def freq_range(self):
        return self.__freq_range


class FrequencyRangePSDBaselineAnalyzer(BaseSignalAnalyzer):
    def __init__(self, freq_range: tuple, dest_colname: str = None):
        self.__last_n_sessions = 3
        self.__freq_range = self.__validate_freq_range(freq_range)
        if dest_colname is None:
            dest_colname = f"PSDBaseline_{self.freq_range}"
        self.__dest_colname = self.__validate_dest_colname(dest_colname)

    def __call__(self, patient_obj: BasePatientObject):
        patient_obj = self.__validate_input_type(patient_obj=patient_obj)
        groupby_colnames = [
            "PatientNumber",
            "Channel",
            "RecordingHemisphere",
            "StimGloveHand",
            "IpsiContra",
        ]

        analyzer = FrequencyRangePSDAnalyzer(
            freq_range=self.freq_range,
            dest_colname=self.__dest_colname,
        )

        df = (
            analyzer(patient_obj=patient_obj)
            .query("TreatmentBranch == 'dbs_off'")
            .sort_values("FirstPacketDateTime", ascending=True)
            # .groupby(by=["PatientNumber", "Channel", "IpsiContra"])
            .groupby(by=groupby_colnames)
            .tail(self.last_n_sessions)
            # .groupby(by=["PatientNumber", "Channel", "IpsiContra"])[[self.__dest_colname]]
            .groupby(by=groupby_colnames)[[self.__dest_colname]]
            .agg(lambda series: np.mean(series.to_numpy()))
            .reset_index(drop=False)
        )
        return df

    def __validate_input_type(self, patient_obj: BasePatientObject) -> BasePatientObject:
        assert isinstance(patient_obj, BasePatientObject)
        return patient_obj

    def __validate_freq_range(self, freq_range: tuple) -> tuple:
        assert isinstance(freq_range, tuple)
        assert len(freq_range) == 2
        return freq_range

    def __validate_dest_colname(self, dest_colname: str) -> str:
        assert isinstance(dest_colname, str)
        return dest_colname

    @property
    def last_n_sessions(self):
        return self.__last_n_sessions

    @property
    def freq_range(self):
        return self.__freq_range

class FrequencyRangeNormalizedPSDAnalyzer(BaseSignalAnalyzer):

    def __init__(self, freq_range: tuple, last_n_sessions:int=3, dest_colname: str = None,):
        self.__freq_range = freq_range
        if dest_colname is None:
            dest_colname = f"PSDNormalized_{self.freq_range}"
        self.__dest_colname = dest_colname
        self.__last_n_sessions = last_n_sessions

        self.__validate__()

    def __validate__(self):
        self.__validate_last_n_sessions(self.last_n_sessions)
        self.__validate_dest_colname(self.__dest_colname)
        self.__validate_freq_range(self.freq_range)
        

    def __call__(self, patient_obj: BasePatientObject):
        patient_obj = self.__validate_input_type(patient_obj)
        psd_colname = f"PSD_{self.freq_range}"
        psd_baseline_colname = f"PSDBaseline_{self.freq_range}"
        psd_analyzer = FrequencyRangePSDAnalyzer(
            freq_range=self.freq_range,
            last_n_sessions=self.last_n_sessions,
            dest_colname=psd_colname,
        )
        baseline_analyzer = FrequencyRangePSDBaselineAnalyzer(
            freq_range=self.freq_range,
            dest_colname=psd_baseline_colname,
        )

        df_psd = psd_analyzer(patient_obj=patient_obj)
        df_baseline = baseline_analyzer(patient_obj=patient_obj)
        
        common_colnames = [colname for colname in df_psd if colname in df_baseline.columns]
        result = (pd
                  .merge(df_psd, df_baseline, how="left",
                         on=common_colnames,
                         validate="many_to_one")
                  .sort_values(by="FirstPacketDateTime")
                  )
        
        result[self.__dest_colname] = result[psd_colname] / result[psd_baseline_colname]
        return result


    def __validate_freq_range(self, freq_range: tuple):
        assert isinstance(freq_range, tuple)
        assert len(freq_range) == 2
        return freq_range

    def __validate_input_type(self, input: BasePatientObject):
        assert isinstance(input, BasePatientObject)
        return input

    def __validate_dest_colname(self, dest_colname: str = None) -> str:
        assert isinstance(dest_colname, str)
        return dest_colname

    def __validate_last_n_sessions(self, last_n_sessions: int|None):
        if last_n_sessions is None:
            return
        if not isinstance(last_n_sessions, int):
            raise TypeError
        if last_n_sessions < 0: 
            raise ValueError
        if last_n_sessions > 6:
            raise ValueError
        return last_n_sessions
    
    @property
    def last_n_sessions(self):
        return self.__last_n_sessions

    @property
    def freq_range(self):
        return self.__freq_range
