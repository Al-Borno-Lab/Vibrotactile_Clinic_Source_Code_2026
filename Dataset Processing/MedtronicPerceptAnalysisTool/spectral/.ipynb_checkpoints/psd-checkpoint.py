# 2025-01-17 Anthony Lee

from typing import Iterable, Tuple
import numpy as np
from scipy.signal import welch, get_window
import numpy.typing as npt
import warnings

__PREFERRED_FUNCTION__ = "psd_welch_contaldi_2023()"

def psd_welch_contaldi_2023(data:npt.NDArray, fs:float) -> Tuple[npt.NDArray, npt.NDArray]:
    """Welch method PSD calculation based on (Contaldi, 2023)

    "Welch’s method (1sec Hamming window, 60% overlap, 250 points)"

    Contaldi, E., Leogrande, G., Fornaro, R., Comi, C., & Magistrelli, L. 
    (2023). Menstrual‐Related Fluctuations in a Juvenile‐Onset Parkinson’s 
    Disease Patient Treated with STN‐DBS: Correlation with Local Field 
    Potentials. Movement Disorders Clinical Practice, 11(1), 101. 
    https://doi.org/10.1002/mdc3.13931
    """
    nperseg = fs
    window_length_sec = 1  # 1-second
    overlap_ratio = 0.6  # 60%

    hamming_window_ndarray = get_window(
        window = "hamming",
        Nx = window_length_sec*fs,
        fftbins = False
    )

    freq, psd = welch(
        x = data, 
        fs = fs, 
        window = hamming_window_ndarray,  # 1 sec Hamming window
        nperseg = nperseg, 
        noverlap = int(nperseg * overlap_ratio),
        detrend=False, # https://github.com/scipy/scipy/issues/8045 - Also the original paper doesn't seem to have detrending
        return_onesided=True,
        scaling="density", 
        axis=-1,
        average="mean"
    )

    return (freq, psd)


def psd_welch_gilron_2021(data:npt.NDArray, fs:float=250) -> Tuple[npt.NDArray, npt.NDArray]:
    """PSD Welch method from (Gilron, 2021)

    - Welch method in MATLAB (pwelch, 500 ms window, 250 ms overlap)

    Gilron, R., Little, S., Perrone, R., Wilt, R., De Hemptinne, 
    C., Yaroshinsky, M. S., Racine, C. A., Wang, S. S., Ostrem, J. L., Larson, 
    P. S., Wang, D. D., Galifianakis, N. B., Bledsoe, I. O., San Luciano, M., 
    Dawes, H. E., Worrell, G. A., Kremen, V., Borton, D. A., Denison, T., 
    & Starr, P. A. (2021). Long-term wireless streaming of neural recordings 
    for circuit discovery and adaptive stimulation in individuals with 
    Parkinson’s disease. Nature Biotechnology, 39(9), 1078–1085. 
    https://doi.org/10.1038/s41587-021-00897-5
    """
    warnings.warn(f"Use the preferred function instead >>> {__PREFERRED_FUNCTION__}", UserWarning)
    window_size_time = 500  # ms
    overlap_time = 250  # ms
    nperseg = int(window_size_time * (fs/1000))  # Count
    noverlap = int(overlap_time * (fs/1000))  # Count

    hamming_window_ndarray = get_window(
        window = "hamming",
        Nx = nperseg,
        fftbins = False
    )

    freq, psd = welch(
        x = data, 
        fs = fs, 
        # window = hamming_window_ndarray, 
        window = "hamm",
        nperseg = nperseg, 
        noverlap = noverlap,
        detrend=False, # https://github.com/scipy/scipy/issues/8045 - Also the original paper doesn't seem to have detrending
        return_onesided=True,
        scaling="density", 
        axis=-1,
        average="mean"
    )

    return (freq, psd)

def psd_calculation_deHemptinne_2015():
    """
    - Welch periodogram method (Matlab pwelch) using FFT
    - 512 points (freq resolution of 1.95Hz)
    - 50% overlap
    - Hanning window
    - Supplemental Information mentioned 257 points (freq resolution of 1.95Hz) --> WHICH IS RIGHT?

    de Hemptinne, C., Swann, N. C., Ostrem, J. L., Ryapolova-Webb, E. S., 
    San Luciano, M., Galifianakis, N. B., & Starr, P. A. (2015). 
    Therapeutic deep brain stimulation reduces cortical phase-amplitude coupling
    in Parkinson’s disease. Nature Neuroscience, 18(5), 779–786. 
    https://doi.org/10.1038/nn.3997
    """
    warnings.warn(f"Use the preferred function instead >>> {__PREFERRED_FUNCTION__}", UserWarning)
    pass

def calculate_psd(data: npt.NDArray, fs: float, nperseg: int = None) -> Tuple[npt.NDArray, npt.NDArray]:
    """Calculate the power spectral density (PSD), and return a tuple of frequency and PSD.

    Calculates using the Welch method with uniform weighting and boxcar window.
    Defaults to PSD frequency bin sizes of 1/4 Hz.

    When the PSD freq bin size is too small (nperseg too large), then the PSD
    figure would be very noisy.
    """
    warnings.warn(f"Use the preferred function instead >>> {__PREFERRED_FUNCTION__}", UserWarning)
    if nperseg is None:
        # A segment is the duration of 1 sec or 1 Hz. Thus the number per segment
        # determines the resolution of the PSD calculation.
        bins_per_hertz = 4
        nperseg = int(fs * bins_per_hertz)

    if len(data) < nperseg: 
        # Some recordings are too short and thus do not have enogh data points
        # for the analysis.
        raise ValueError(f"Input data needs to have length at least {nperseg}, got {len(data)}.")

    percentage_of_overlap = 0.9  # 90% overlap

    freq, psd = welch(
        x=data,
        fs=fs,
        nperseg=nperseg,
        noverlap=int(nperseg * percentage_of_overlap),
        window="boxcar",
    )

    return (freq, psd)