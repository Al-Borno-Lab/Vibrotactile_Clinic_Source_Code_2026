from .base import BaseSignalProcessor
from .psd_support import psd_welch_contaldi_2023
import logging
import dataclasses
import numpy as np
import collections
import numbers
import typing

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class PowerSpectralDensity:
    frequency: np.ndarray
    PSD: np.ndarray

    def filter_freq_range(self, freq_range: tuple) -> typing.Self:

        self.__validate_freq_range(freq_range)

        lower_limit, upper_limit = freq_range
        mask = (self.frequency >= lower_limit) & (self.frequency <= upper_limit)

        return PowerSpectralDensity(self.frequency[mask], self.PSD[mask])

    def __post_init__(self) -> None:
        self.__validate_frequency(self.frequency)
        self.__validate_PSD(self.PSD)
        self.__validate_components_euqal_lengths(self.frequency, self.PSD)
        return

    def __iter__(self) -> typing.Generator[np.ndarray, None, None]:
        yield from dataclasses.asdict(self).values()
        
    def __eq__(self, other: typing.Self) -> bool:
        return ( np.array_equal(self.frequency, other.frequency) & np.array_equal(self.PSD, other.PSD))

    def __add__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            return PowerSpectralDensity(self.frequency, self.PSD + other)
        elif isinstance(other, PowerSpectralDensity):
            self.__validate_PowerSpectralDensity_obj(other)
            return PowerSpectralDensity(self.frequency, np.add(self.PSD, other.PSD))

    def __sub__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            return PowerSpectralDensity(self.frequency, self.PSD - other)
        elif isinstance(other, PowerSpectralDensity):
            self.__validate_PowerSpectralDensity_obj(other)
            return PowerSpectralDensity(self.frequency, np.subtract(self.PSD, other.PSD))

    def __mul__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            return PowerSpectralDensity(self.frequency, self.PSD * other)
        elif isinstance(other, PowerSpectralDensity):
            self.__validate_PowerSpectralDensity_obj(other)
            return PowerSpectralDensity(self.frequency, np.multiply(self.PSD, other.PSD))

    def __truediv__(self, other: typing.Self) -> typing.Self:
        if isinstance(other, numbers.Number):
            return PowerSpectralDensity(self.frequency, self.PSD / other)
        elif isinstance(other, PowerSpectralDensity):
            self.__validate_PowerSpectralDensity_obj(other)
            return PowerSpectralDensity(self.frequency, np.divide(self.PSD, other.PSD))

    def mean(self, axis=None, dtype=None, out=None, **kwargs) -> float:
        # TODO: Implement dtype, out, and kwargs conforming to Numpy's API guidance
        if axis is None: 
            axis = 0
            
        if axis == 0:
            return self.PSD.mean()
        if axis == 1: 
            return self.PSD
    
    def __array__(self, dtype=None, copy=None) -> np.ndarray:
        # TODO: Further understand the array protocol and conform to it - https://numpy.org/doc/stable/user/basics.interoperability.html#the-array-method
        return self.PSD

    def __validate_PowerSpectralDensity_obj(self, other: typing.Self) -> None:
        if not np.array_equal(self.frequency, other.frequency):
            raise ValueError(f"`frequency` attribute mismatch, got {self.frequency}, {other.frequency}")
        if not (self.PSD.shape == other.PSD.shape):
            raise ValueError(f"`PSD` attribute length mismatch, {self.PSD.shape}, {other.PSD.shape}")
        return
    
    def __validate_freq_range(self, freq_range: tuple) -> None:
        if not isinstance(freq_range, tuple):
            raise TypeError(f"`freq_range` is expected to be a tuple, got {type(freq_range)}")
        if len(freq_range) != 2:
            raise ValueError(f"`freq_range` length expected to be 2, got {len(freq_range)}")


    def __validate_frequency(self, frequency: np.ndarray):
        if not isinstance(frequency, np.ndarray):
            raise TypeError(f"`frequency` expected to be an ndarray, got {type(frequency)}")
        if (frequency < 0).any():
            raise ValueError(f"`frequency` have to all be non-negative, got {frequency}")

    def __validate_PSD(self, PSD: np.ndarray):
        if not isinstance(PSD, np.ndarray):
            raise TypeError(f"`PSD` expected to be an ndarray, got {type(PSD)}")

    def __validate_components_euqal_lengths(self, frequency: np.ndarray, PSD: np.ndarray):
        if not (frequency.shape == PSD.shape):
            raise ValueError(f"Expected same lengths, got {frequency.shape}, {PSD.shape}")


class PowerSpectralDensityProcessor(BaseSignalProcessor):
    def __init__(self, sampling_freq: int) -> typing.Self:
        self.__sampling_freq = sampling_freq
        self.__validate__()

    def __call__(self, data: np.ndarray) -> PowerSpectralDensity:
        data = self.__validate_data(data)
        freq, psd = psd_welch_contaldi_2023(
            data=data,
            fs=self.sampling_freq,
        )
        # return PowerSpectralDensity(freq, psd).filter_freq_range((1, int(max(freq))))
        return PowerSpectralDensity(freq, psd)

    @property
    def sampling_freq(self):
        return self.__sampling_freq

    def __validate__(self) -> None:
        self.__validate_sampling_freq(self.sampling_freq)

    def __validate_sampling_freq(self, sampling_freq:int) -> int:
        if not isinstance(sampling_freq, int):
            raise TypeError(f"`sampling_freq` is expected to be an integer, got {type(sampling_freq)}")
        if sampling_freq <= 0:
            raise ValueError(f"`sampling_freq` has to be non-negative, got {sampling_freq}")
        
        return sampling_freq

    def __validate_data(self, data: np.ndarray) -> np.ndarray:
        if not isinstance(data, np.ndarray):
            raise TypeError(f"`data` expected to be type ndarray, got {type(data)}")
        return data

