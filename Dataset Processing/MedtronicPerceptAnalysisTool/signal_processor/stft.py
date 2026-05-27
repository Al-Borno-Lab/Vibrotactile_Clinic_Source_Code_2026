from scipy.signal import ShortTimeFFT, get_window
import numpy as np


def stft_method(signal):
    sampling_freq = 250
    overlap_ratio = 0.5

    signal = np.array(signal)

    STFT_analyzer = ShortTimeFFT(
        win = get_window("hann", sampling_freq, False), 
        # hop = int(sampling_freq* (1-overlap_ratio)), 
        hop = 1,
        fs = sampling_freq, 
        # scale_to= "magnitude",
        scale_to= "psd",
    )
    tf_spectral = STFT_analyzer.stft(signal)
    tf_spectral = abs(tf_spectral)
    # print(tf_spectral.shape)
    return tf_spectral
