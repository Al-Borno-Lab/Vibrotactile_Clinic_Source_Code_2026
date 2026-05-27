import logging
from ...data_wrapper.base import Patient_Dataset_Base as BasePatientObject
from ..base import BaseSignalAnalyzer
import numpy as np
from . import FrequencyRangePSDAnalyzer, FrequencyRangeNormalizedPSDAnalyzer

logger = logging.getLogger(__name__)


class FrequencyRangePSDMeanAnalyzer(BaseSignalAnalyzer):

    def __init__(self, freq_range: tuple, dest_colname: str = None):
        self.__freq_range = self.__validate_freq_range(freq_range)
        if dest_colname is None:
            dest_colname = f"PSDMean_{self.freq_range}"
        self.__dest_colname = self.__validate_dest_colname(dest_colname)

    def __call__(self, patient_obj: BasePatientObject):
        patient_obj = self.__validate_input_type(patient_obj)
        analyzer = FrequencyRangePSDAnalyzer(
            freq_range=self.freq_range,
            dest_colname=self.__dest_colname,
        )

        df = analyzer(patient_obj=patient_obj)
        df.loc[:, self.__dest_colname] = df.loc[:, self.__dest_colname].apply(lambda cell: np.mean(cell))

        return df

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

    @property
    def freq_range(self):
        return self.__freq_range


class FrequencyRangeNormalizedPSDMeanAnalyzer(BaseSignalAnalyzer):

    def __init__(self, freq_range: tuple, last_n_sessions:int=None, dest_colname: str = None,):
        self.__freq_range = self.__validate_freq_range(freq_range)
        if dest_colname is None:
            dest_colname = f"NormalizedPSDMean_{self.freq_range}"
        self.__dest_colname = self.__validate_dest_colname(dest_colname)
        if last_n_sessions is None:
            last_n_sessions = 3
        self.__last_n_sessions = self.__validate_last_n_sessions(last_n_sessions)

    def __call__(self, patient_obj: BasePatientObject):
        patient_obj = self.__validate_input_type(patient_obj)
        analyzer = FrequencyRangeNormalizedPSDAnalyzer(
            freq_range=self.freq_range,
            last_n_sessions=self.last_n_sessions,
            dest_colname=self.__dest_colname,
        )
        
        result = analyzer(patient_obj)
        result[self.__dest_colname] = result[self.__dest_colname].apply(lambda cell: np.mean(cell))
        return result
        
    @property
    def last_n_sessions(self):
        return self.__last_n_sessions

    @property
    def freq_range(self):
        return self.__freq_range

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

    def __validate_last_n_sessions(self, last_n_sessions:int) -> int:
        assert last_n_sessions in range(1, 7)
        assert isinstance(last_n_sessions, int)
        return last_n_sessions