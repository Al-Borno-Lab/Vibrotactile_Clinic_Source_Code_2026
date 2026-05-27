# Template subtraction functionalities
#
# Anthony Lee 2025-12-07
# For ECG artifact removal from recorded signals.

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import neurokit2 as nk

def calculate_bpm(peak_idx, sampling_rate): 
    """Return estimated beats-per-minute (BPM)"""
    return (np.mean(np.diff(peak_idx)) * sampling_rate**(-1) / 60)**(-1)

def find_ecg_R_peaks(signal:np.ndarray, sampling_rate:int, method:str='emrich2023') -> np.ndarray:
    """Find the R-peak of the QRS-complex and return the indices as an ndarray.

    Emrich, J., Koka, T., Wirth, S., & Muma, M. (2023). Accelerated Sample-Accurate R-Peak Detectors Based on 
    Visibility Graphs. 2023 31st European Signal Processing Conference (EUSIPCO), 1090–1094. 
    https://doi.org/10.23919/EUSIPCO58844.2023.10290007

    Args:
        signal (np.ndarray): The signal to be analyzed
        sampling_rate (int): The sampling rate of the signal
        method (str, optional): The detection method, see NeuroKit2 documentation for other methods. Defaults to 'emrich2023'.

    Returns:
        np.ndarray: Indices of R-peak.
    """
    _, result_dict = nk.ecg_peaks(
       signal, 
       sampling_rate=sampling_rate,
       method=method,
       correct_artifacts=False,
    ) 
    return result_dict["ECG_R_Peaks"]

def compare_ecg_R_peak_finding_algo():
    pass

def get_QRS_complex_epochs(signal, peak_indices, samples_before: int = 50, samples_after: int = 50) -> np.ndarray:
    """Return a matrix given the original LFP signal and indicies of the detected peaks.
    
    This function slices the signal by capturing n_samples_before and n_samples after each peak. The result is a matrix
    that is n x (samples_before + samples_after + 1) where n is the length of the array `peak_indices`.
    
    The default tail lengths of 50 on each side is suggested by (Stam et al., 2023).
    
    Stam, M. J., Van Wijk, B. C. M., Sharma, P., Beudel, M., Piña-Fuentes, D. A., De Bie, R. M. A., Schuurman, P. R., 
    Neumann, W.-J., & Buijink, A. W. G. (2023). A comparison of methods to suppress electrocardiographic artifacts in 
    local field potential recordings. Clinical Neurophysiology, 146, 147–161. https://doi.org/10.1016/j.clinph.2022.11.011

    """
    
    peak_indices = np.array(peak_indices)

    n_samples_before = samples_before
    n_samples_after = samples_after

    n_rows = len(peak_indices)
    n_cols = (n_samples_before + n_samples_after + 1)

    result = np.full(
        shape=(n_rows, n_cols), 
        fill_value=0,
        dtype=np.float32,
    )

    for idx in range(n_rows):
        start_idx = peak_indices[idx] - n_samples_before
        end_idx = peak_indices[idx] + n_samples_after + 1

        # Check index - handle when clipping range extends outside the bounds of the signal length
        if start_idx < 0: 
            before_pad_length = np.abs(start_idx)
            start_idx = 0
            signal_slice = np.pad(signal[start_idx:end_idx], pad_width=(before_pad_length, 0))
            
        elif end_idx > len(signal):
            after_pad_length = np.abs(len(signal)-end_idx)
            end_idx = len(signal)
            signal_slice = np.pad(signal[start_idx:end_idx], pad_width=(0, after_pad_length))
        
        else:
            signal_slice = signal[start_idx:end_idx]

        # print(start_idx, end_idx, before_pad_length)
        # print(len(signal_slice))
        result[idx] = signal_slice
        
    return result


def get_avg_QRS_complex(qrs_complex_epochs) -> np.ndarray:
    """Return an average QRS complex given a 2D ndarray of QRS complex epochs.
    
    This function takes an ndarray matrix and averages across the index-axis to get the average QRS complex.

    Stam, M. J., Van Wijk, B. C. M., Sharma, P., Beudel, M., Piña-Fuentes, D. A., De Bie, R. M. A., Schuurman, P. R., 
    Neumann, W.-J., & Buijink, A. W. G. (2023). A comparison of methods to suppress electrocardiographic artifacts in 
    local field potential recordings. Clinical Neurophysiology, 146, 147–161. https://doi.org/10.1016/j.clinph.2022.11.011
    """
    
    assert isinstance(qrs_complex_epochs, np.ndarray)
    
    return np.mean(qrs_complex_epochs, axis=0)

def trim_avg_QRS_complex_outer_tails(avg_qrs_complex) -> np.ndarray:
    """Return a trimmed avg QRS complex given an untrimmed QRS complex.

    The trimming algorithm selects the two samples with the least differences from the outer sides of the Q- and S-peaks
    with a maximum of 30 samples from each side (Stam et al., 2023).
    
    The minimum length of a trimmed QRS complex is determined by the suggested parameters in (Stam et al., 2023). The
    paper suggests 50 samples before and after the R-peak and to compare 30 samples from each outer tail of the average
    of QRS complex epochs. (50*2 + 1) - (30*2) = 41

    Instead of trimming the two ends off, the function set the tails to an additive identity (zero), such that the two
    tails will be be part of the template-subtraction from the original signal.

    Stam, M. J., Van Wijk, B. C. M., Sharma, P., Beudel, M., Piña-Fuentes, D. A., De Bie, R. M. A., Schuurman, P. R., 
    Neumann, W.-J., & Buijink, A. W. G. (2023). A comparison of methods to suppress electrocardiographic artifacts in 
    local field potential recordings. Clinical Neurophysiology, 146, 147–161. https://doi.org/10.1016/j.clinph.2022.11.011
    """    

    max_n_sample_trim = 30  # Max 30 samples can be trimmed from each outer edge
    min_trimmed_qrs = (50*2 + 1) - (max_n_sample_trim*2)
    assert (len(avg_qrs_complex) - 2 * max_n_sample_trim) >= min_trimmed_qrs, (
        f"The QRS complex needs to be at least {int(2*max_n_sample_trim+min_trimmed_qrs)}, "
        f"current QRS complex has a length of {len(avg_qrs_complex)}"
    )
    
    q_tail = avg_qrs_complex[:max_n_sample_trim].reshape((-1, 1))
    s_tail = avg_qrs_complex[-max_n_sample_trim:].reshape((1, -1))
    
    diff = np.abs(q_tail - s_tail)
    q_idx, s_idx = np.unravel_index(np.argmin(diff), shape=diff.shape)
    
    result = avg_qrs_complex

    ## Direction 1 - Setting the two wings to zero
    result[ :q_idx+1] = 0 # Offset to include the ending index item
    result[s_idx-max_n_sample_trim: ] = 0

    ## Direction 2 - Setting the two wings to the first and last value respectively
    # result[:q_idx] = q_tail.reshape(-1)[q_idx]
    # result[s_idx-max_n_sample_trim:] = s_tail.reshape(-1)[s_idx]
    
    return result

def get_ECG_artifact_removal_offset(signal, sampling_rate) -> np.ndarray:
    
    peak_idx = find_ecg_R_peaks(signal, sampling_rate)
    qrs_template = trim_avg_QRS_complex_outer_tails(
        get_avg_QRS_complex(
            get_QRS_complex_epochs(signal, peak_idx)
            )
        )
    mask = np.zeros_like(signal)
    mask[peak_idx] = 1
    
    return np.convolve(mask, qrs_template, mode="same")

def remove_ECG_artifacts(signal, sampling_rate) -> np.ndarray:
    """Remove the ECG artifacts"""

    offset = get_ECG_artifact_removal_offset(signal, sampling_rate)
    result = signal - offset
    return result


################################################################################
## Plotting tools
################################################################################

def plot_signal_and_detected_peaks(signal, peaks):
    # Create a mask
    mask = np.full(shape=signal.shape, fill_value=False, dtype=bool)
    mask[peaks] = True

    # Plot
    nrows, ncols, inches, xyratio = 1, 1, 8, 3
    fig, ax = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))
    ax.plot(signal)
    ax.scatter( np.arange(len(signal))[mask], signal[mask], color='red', marker="x")

    # Added artists
    ax.set_title("Signal and detected R-peaks")
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    return fig

def plot_qrs_epochs_template_and_trimmed_template(signal, sampling_rate):
    """Convenience function to plot the results for development."""

    nrows, ncols, inches, xyratio = 1, 1, 5, 1.2
    fig, ax = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches))

    peaks = find_ecg_R_peaks(signal, sampling_rate)
    qrs_complex_epochs = get_QRS_complex_epochs(signal, peaks)

    for qrs_epoch in qrs_complex_epochs: 
        line1, = ax.plot(qrs_epoch, color='grey', alpha=.2, label="QRS Epoch(s)")

    qrs_template = get_avg_QRS_complex(qrs_complex_epochs)
    line2, = ax.plot(qrs_template, color='red', label="QRS template")    

    qrs_template_trimmed = trim_avg_QRS_complex_outer_tails(qrs_template)
    qrs_template_trimmed

    line3, = ax.plot(qrs_template_trimmed, color='green', label="Trimmed QRS template")
    ax.legend(handles=[line1, line2, line3])

    # Add artists
    ax.set_title("QRS Epochs and Template")
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    return fig

def plot_ECG_artifact_correction_offset(signal, sampling_rate):
    """Convenience function to plot the array used to offset the QRS complexes via template subtraction."""

    nrows, ncols, inches, xyratio = 4, 1, 5, 10
    fig, axs = plt.subplots(nrows, ncols, figsize=(ncols*inches*xyratio, nrows*inches), sharex=True, sharey=True)
    fig.suptitle("Raw signal, template to subtract, and ECG artifact filtered signal")

    sampling_rate = 250
    y_max_amplitude = signal.max()

    offset = get_ECG_artifact_removal_offset(signal, sampling_rate)
    r_peaks = find_ecg_R_peaks(signal, sampling_rate)
    filtered_signal = remove_ECG_artifacts(signal, sampling_rate)

    ## Raw signal
    ax = axs[0]
    ax.set_title("Raw Signal")
    line0, = ax.plot(signal, label='Raw signal')
    ax.legend(handles=[line0])
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    ## Offset axes
    ax = axs[1]
    ax.set_title("Template subtraction offset")
    line1 = ax.scatter(r_peaks, np.zeros_like(r_peaks), marker='x', c='red', label='Detected R-peak')
    line2 = ax.vlines(r_peaks, ymin=-y_max_amplitude, ymax=y_max_amplitude, color='green', label='Detected R-peak')
    line3, = ax.plot(offset, label="offset")
    ax.legend(handles=[line1, line2, line3])
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    ## Filtered signal
    ax = axs[2]
    ax.set_title("After template subtraction")
    line4, = ax.plot(filtered_signal, label="Filtered signal")
    ax.legend(handles=[line4])
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    ## Overlay the two signals
    ax = axs[3]
    ax.set_title("Before and after")
    line5, = ax.plot(signal, alpha=0.5, label="Before filtered")
    line6, = ax.plot(filtered_signal, alpha=0.5, label="After filtered signal")
    ax.legend(handles=[line5, line6])
    ax.set_ylabel("Amplitude")
    ax.set_xlabel("n-th sample")

    fig.set_layout_engine('constrained')

    return fig
