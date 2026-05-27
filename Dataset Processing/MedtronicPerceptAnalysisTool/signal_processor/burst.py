import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import ShortTimeFFT, get_window

from ..signal_processor.filter import BandpassFilterProcessor
# from neurodsp.burst import detect_bursts_dual_threshold
# from neurodsp.burst import compute_burst_stats
# from neurodsp.plts.time_series import plot_bursts
# from .base import BaseSignalProcessor


    
# class DualThresholdBurstProcessor(BaseSignalProcessor):
    
#     def __init__(self, dual_threshold: tuple, freq_range: tuple, 
#                  sampling_freq: int, magnitude_type: str="power",
#                  avg_type: str="mean",):
        
#         self._dual_threshold = dual_threshold
#         self._freq_range = freq_range
#         self._magnitude_type = magnitude_type
#         self._avg_type = avg_type
#         self._sampling_freq = sampling_freq
        

#     def __call__(self, signal: typing.Iterable, burst_or_stat:str="stat"):
#         match burst_or_stat:
#             case "burst":
#                 return self.__calculate_burst(signal=signal)
#             case "stat":
#                 return self.__calculate_burst_stat(self.__calculate_burst(signal=signal))

#     def __calculate_burst(self, signal: typing.Iterable):
#         return detect_bursts_dual_threshold(
#             sig=np.array(signal),
#             fs=self.sampling_freq, 
#             dual_thresh=self.dual_threshold,
#             f_range=self.freq_range, 
#             magnitude_type=self.magnitude_type,
#             avg_type=self.avg_type,
#         )
    
#     def __calculate_burst_stat(self, bursting) -> dict:
#         return compute_burst_stats(bursting=bursting, fs=self._sampling_freq)

#     @property
#     def dual_threshold(self):
#         return self._dual_threshold

#     @property
#     def freq_range(self):
#         return self._freq_range
        
#     @property
#     def magnitude_type(self):
#         return self._magnitude_type

#     @property
#     def avg_type(self):
#         return self._avg_type

#     @property
#     def sampling_freq(self):
#         return self._sampling_freq
    
# def plot(self, ax_title: str=None) -> Figure:
#     plt.ioff()
#     plt.close()

#     if ax_title is None:
#         ax_title = "    ".join([f"dual-threshold:{self.dual_threshold}", 
#                     f"freq-range:{self.freq_range}", 
#                     f"fs:{self.sampling_freq}Hz", 
#                     f"magnitude-type:{self.magnitude_type}",
#                     f"average-type:{self.avg_type}"]
#         )

#     nrows, ncols, inches, xyratio = 1, 1, 3, 5
#     fig, ax = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))

#     times = np.arange(0, len(self.signal)) * 1/self.sampling_freq
#     plot_bursts(times, self.signal, self.burst, ax=ax, labels=["LFP", "Detected Burst"])

#     ax.set_title(ax_title)
#     fig.suptitle("Dual Threshold Burst Detection")
#     fig.set_layout_engine("constrained")

#     return fig

import numpy as np
from scipy import sparse
from collections import namedtuple

BurstStatistics_Duration_ms = namedtuple(
    "BurstStatistics_Duration_ms", 
    (
        "histogram", 
        "mean", 
        "std", 
        "count",
    )
)
BurstDurationHist_ms = namedtuple(
    "BurstDurationHist_ms", 
    ("bin_counts", "bin_edges_ms")
)
    
BurstDetectionStartsAndEnds = namedtuple(
    "BurstDetectionStartsAndEnds",
    (
        "start_indices", 
        "end_indices", 
        "segment_lengths",
        "datapoint_counts",
    )
)


def burst_detection_starts_ends(burst_detection_array):
    """Find the starting-/ending-indices of burst detection.
    
    Finding the starting and ending indices help with filtering for bursts of certain minimum length.
    Both the indices for starts and ends are INCLUSIVE!
    """
    
    edges = np.diff(burst_detection_array, prepend=0)
    starts = np.where(edges==1)[0]
    
    edges = np.diff(np.flip(burst_detection_array, axis=0), prepend=0)
    edges = np.flip(edges, axis=0)
    ends = np.where(edges==1)[0]  # Ending indices are inclusive!
    
    lengths = ends - starts
    counts = ends - starts + 1

    return BurstDetectionStartsAndEnds(
        start_indices=starts, 
        end_indices=ends, 
        segment_lengths=lengths,
        datapoint_counts=counts
    )

def reconstruct_burst_detection(starts, ends, data_length):
    """Reconstruct the original bool array of the burst detection using arrays of starting-/ending-indices.

    This func reconstructs the burst array of boolean that indicates whether each data point in the original signal is
    being detected as burst by some burst algorithm.
    
    args:
    =====
    starts (ndarray): array of indices of the burst detection starting point.
    ends (ndarray): array of indices of the burst detection ending point.
    data_length (int): length of the original burst detection array.
    
    returns:
    ========
    (ndarray): ndarray of boolean indicating whether each data point is "burst"
    """
    
    burst_counts = ends - starts + 1
    
    data = np.ones( burst_counts.sum(), dtype=int)
    indices = np.concat( tuple(np.arange(start, end+1, dtype=int) for start, end in np.column_stack((starts, ends))) )
    indptr = np.array( [0, len(data)], dtype=int )

    sparse_array = sparse.csr_array(
        (
            data, 
            indices,
            indptr
        )
    )
    
    result = np.append( sparse_array.todense(), np.zeros(data_length - sparse_array.shape[1])).astype(bool)
    return result

def filter_burst_detection(burst_detection_array, sampling_freq, min_duration_ms=100):

    # Translate the min_duration_ms from ms to min_segments
    min_segment_count = (min_duration_ms / (1e3 / sampling_freq))
    min_segment_count = np.ceil(min_segment_count)
    
    # Get start and end arrays and filter by the detection counts
    starts, ends, segment_lengths, datapoint_counts = burst_detection_starts_ends(
        burst_detection_array=burst_detection_array
    )
    
    mask = segment_lengths >= min_segment_count
    filtered_starts = starts[mask]
    filtered_ends = ends[mask]
    
    # Reconstruct the burst detection array
    result = reconstruct_burst_detection(filtered_starts, filtered_ends, len(burst_detection_array))
    return result

def detect_burst_tinkhauser_2017(signal, freq_range, sampling_freq, burst_threshold_percentile=None, min_burst_duration_ms=None):
    """Burst detection algorithm from Tinkhauser 2017.
    
    Gerd Tinkhauser, Alek Pogosyan, Huiling Tan, Damian M Herz, Andrea A Kühn, Peter Brown, Beta burst dynamics in Parkinson’s disease OFF and ON dopaminergic medication, Brain, Volume 140, Issue 11, November 2017, Pages 2968–2981, https://doi.org/10.1093/brain/awx252
    """
    if burst_threshold_percentile is None:
        burst_threshold_percentile = 75
        
    if min_burst_duration_ms is None:
        min_burst_duration_ms = 100 
    
    if sampling_freq % 2 == 0:
        padding = int( (250-1)//2 )
    else:
        padding = int( 250/2 )
    
    bandpass_filter = BandpassFilterProcessor(
        freq_range=freq_range, 
        sampling_freq=sampling_freq,
    )

    STFT_analyzer = ShortTimeFFT(
        win = get_window("hann", sampling_freq, False), 
        hop = 1,
        fs = sampling_freq, 
        scale_to= 'magnitude',
    )

    freq_mask = (STFT_analyzer.f >= freq_range[0]) & (STFT_analyzer.f <= freq_range[1])
    
    signal = np.array(signal)
    signal = bandpass_filter(signal)
    tf_spectral = STFT_analyzer.stft(signal)
    tf_spectral = abs(tf_spectral)  # Remove the complex component
    tf_spectral = tf_spectral[freq_mask, padding:-padding]  # Remove the extras from zero padding signal
    freq_band_magnitude_time_series = tf_spectral.mean(axis=0)
    
    # Get the burst threshold
    burst_threshold_magnitude = np.percentile(freq_band_magnitude_time_series, q=burst_threshold_percentile)
    
    # Get the burst detection array using the magnitude threshold
    burst_detection = freq_band_magnitude_time_series > burst_threshold_magnitude
    
    # Filter the burst detection array by the min_burst_duration
    filtered_burst_detection = filter_burst_detection(
        burst_detection_array=burst_detection,
        sampling_freq=sampling_freq,
        min_duration_ms=min_burst_duration_ms,
    )
    
    return filtered_burst_detection 

def calculate_burst_statistics(burst_detection_array, sampling_freq):
    # Get the starts and ends, then calculate the duration
    starts, ends, segment_lengths, datapoint_counts = burst_detection_starts_ends(burst_detection_array=burst_detection_array)
    segment_lengths_ms = segment_lengths * (1e3/sampling_freq)
    
    # Get histogram
    burst_duration_hist = BurstDurationHist_ms(
        *np.histogram(
            segment_lengths_ms,
            bins = np.arange(0, 1e4 + 1, 1e2)
        )
    )

    return BurstStatistics_Duration_ms(
        histogram = burst_duration_hist,
        mean = np.mean(segment_lengths_ms),
        std = np.std(segment_lengths_ms),
        count = len(segment_lengths_ms),
    )