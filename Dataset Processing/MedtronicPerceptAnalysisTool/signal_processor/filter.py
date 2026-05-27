import logging
import numpy as np
from .base import BaseSignalProcessor
from .filter_support import IIR_butterworth_filter_hammer_2022

logger = logging.getLogger(__name__)

class BandpassFilterProcessor(BaseSignalProcessor):
    def __init__(self, freq_range:tuple, sampling_freq:int):
        """Constructs a bandpass filter processor

        Args:
            freq_range (tuple): The frequency range to bandpass with.
            sampling_freq (int): Sampling frequency of the signal.
        """
        
        self.__freq_range = freq_range
        self.__sampling_freq = sampling_freq

        self.__validate__()
    
    def __validate__(self) -> None:
        self.__validate_sampling_freq(self.sampling_freq)
        self.__validate_freq_range(self.freq_range)
        

    def __call__(self, data:np.ndarray) -> np.ndarray:
        """Bandpass filter the signal data

        Args:
            data (np.ndarray): Raw signal data.

        Returns:
            np.ndarray: Bandpass filtered signal data.
        """
        data = self.__validate_data_dtype(data)
        result = IIR_butterworth_filter_hammer_2022(
            data=data, 
            freqRange=self.freq_range,
            fs=self.sampling_freq,
        )
        return result

    @property
    def freq_range(self) -> tuple:
        return self.__freq_range

    @property
    def sampling_freq(self) -> int:
        return self.__sampling_freq

    def __validate_freq_range(self, freq_range:tuple) -> tuple:
        if not isinstance(freq_range, tuple):
            raise TypeError(f"`freq_range` is expected to be a tuple, got {type(freq_range)}")
        if not len(freq_range) == 2:
            raise ValueError(f"`freq_range` is expected to be a length two tuple, got length {len(freq_range)}")
        if not ((freq_range[0] >= 0) & (freq_range[1] >= 0)):
            raise ValueError(f"`freq_range` bounds have to be non-negative, got {freq_range}")
        if not ((freq_range[0] <= self.sampling_freq) & (freq_range[1] <= self.sampling_freq)):
            raise ValueError(f"`freq_range` has to be no greater than the `sampling_freq`, got {freq_range}")

        return freq_range 

    def __validate_sampling_freq(self, sampling_freq:int) -> int:
        if not isinstance(sampling_freq, int):
            raise TypeError(f"`sampling_freq` is expected to be an integer, got {type(sampling_freq)}")
        if sampling_freq <= 0:
            raise ValueError(f"`sampling_freq` has to be non-negative, got {sampling_freq}")
        
        return sampling_freq

    def __validate_data_dtype(self, data:np.ndarray) -> np.ndarray:
        if not isinstance(data, np.ndarray): 
            raise TypeError(f"`data` is expected to be of numpy ndarray type, got type {type(data)}")

        return data