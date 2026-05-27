import scipy as scp
from scipy.signal import firwin, filtfilt, ShortTimeFFT, get_window
import numpy.typing as npt
import typing
import warnings
import numpy as np

def filter_Medtronic_Percept_ECG_artifacts():
    """
    Medtronic Percept whitepaper states that there are two main types of
    artifacts, ECG and motion artifacts, and the clinician application will
    display a message of artifact detected if one of the two types of artifacts
    is detected.

    Characteristic of an ECG artifact is a large amplitude signal observed at
    ~1-2 Hz.

    Medtronic. (2022, September). Percept™ (PC and RC) Neurostimulators with 
    BrainSense ™ Technology—DBS Sensing White Paper. 
    https://www.medtronicacademy.com/en-us/document/brainsense--whitepaper-update-for-a610-v3-0
    """
    print(filter_Medtronic_Percept_ECG_artifacts.__doc__)

def filter_Medtronic_Percept_motion_artifacts():
    """
    Motion artifacts are not LFP induced by motion but motion that causes the
    sensing apparatus to move in a manner that produces an artifact.

    Motion artifacts are best observed when plotting the raw data and a aperiodic
    large amplitude is observed in the raw signal.

    Medtronic. (2022, September). Percept™ (PC and RC) Neurostimulators with 
    BrainSense ™ Technology—DBS Sensing White Paper. 
    https://www.medtronicacademy.com/en-us/document/brainsense--whitepaper-update-for-a610-v3-0
    """
    print(filter_Medtronic_Percept_motion_artifacts.__doc__)

def FIR_filter(data:npt.NDArray, freq_range:tuple=(1, 100)) -> npt.NDArray:
    """
    Intuitive FIR filter design.

    Can be improved by consulting the SciPy Cookbook:
    https://scipy-cookbook.readthedocs.io/items/FIRFilter.html
    """
    sampling_freq = 250  # Medtronic Summit RC+S & Medtronic Percept PC+RC
    numtaps = int(sampling_freq / 2)  # Nyquist Freq.

    if (not isinstance(freq_range, tuple)) | (len(freq_range)!=2):
        raise ValueError(f"freq_range expected to be a tuple of length 2, got {freq_range} of type {type(freq_range)}")

    # Create FIR filter
    FIR_filter = firwin(
        numtaps=numtaps,
        cutoff=freq_range,
        width=None,  # Default - arg for Kaiser FIR filter design
        window="hamming", # MATLAB fir1 states that the window needs to be n+1 in length
        pass_zero="bandpass",
        scale=True, # MATLAB fir1 filter `scaleopt` defaults to scale
        fs=sampling_freq
    )

    # Zero phase-shift filtering - Convolve forward and backward
    filtered_signal = filtfilt(
        b=FIR_filter,
        a=[1.0],  # SciPy Cookbook - Set the denominator to [1.0] for FIR filter
        x=data,
    )
    return filtered_signal

def FIR_filter_gilron_2021(data:npt.NDArray, freq_range:typing.Tuple=(1, 100)) -> npt.NDArray:
    """FIR zero phase-shift filtering using parameters from (Gilron, 2021). 

    Warning
    ------- 
    The author may meant an IIR filter instead of the FIR filter because a 3rd 
    order FIR filter is very weak in filtering anything.

    Notes
    -----
    - Two-way 3rd order FIR filter (eegfilt from eeglab toolbox with fir1 parameters)
    - Most home streaming used a lower sampling rate of 250 Hz even though the device
      allows for greater sampling freq (Supplemental Information).
    - Bandpassed in freq between 1-200 Hz for movement related tasks which are
      sampling at 1000 Hz.
    - For data acquisition using lower sampling freq of 250 Hz, a low-pass 100 Hz
      is used. This aligns with the issue of transition bands at the spectral ends.
      
    Reference
    ---------
    Gilron, R., Little, S., Perrone, R., Wilt, R., De Hemptinne, 
    C., Yaroshinsky, M. S., Racine, C. A., Wang, S. S., Ostrem, J. L., Larson, 
    P. S., Wang, D. D., Galifianakis, N. B., Bledsoe, I. O., San Luciano, M., 
    Dawes, H. E., Worrell, G. A., Kremen, V., Borton, D. A., Denison, T., 
    & Starr, P. A. (2021). Long-term wireless streaming of neural recordings 
    for circuit discovery and adaptive stimulation in individuals with 
    Parkinson’s disease. Nature Biotechnology, 39(9), 1078–1085. 
    https://doi.org/10.1038/s41587-021-00897-5
    """

    warnings.warn(f"The 3rd order FIR filter only has 4 taps and does not have enough filtering ability. Perhaps the author meant an IIR filter?", UserWarning)

    sampling_freq = 250  # Medtronic Summit RC+S & Medtronic Percept PC+RC
    order = 3  # 3rd order

    if (not isinstance(freq_range, tuple)) | (len(freq_range)!=2):
        raise ValueError(f"freq_range expected to be a tuple of length 2, got {freq_range} of type {type(freq_range)}")

    # Create FIR filter
    FIR_filter = firwin(
        numtaps=order + 1,  # SciPy documentation
        cutoff=freq_range,
        width=None,  # Default - arg for Kaiser FIR filter design
        window="hamming", # MATLAB fir1 states that the window needs to be n+1 in length
        # pass_zero="bandpass",
        pass_zero=False,
        scale=True, # MATLAB fir1 filter `scaleopt` defaults to scale
        fs=sampling_freq
    )

    # Zero phase-shift filtering - Convolve forward and backward
    filtered_signal = filtfilt(
        b=FIR_filter,
        a=[1.0],  # SciPy Cookbook - Set the denominator to [1.0] for FIR filter
        x=data,
    )

    return filtered_signal

def FIR_filter_deHeptinne_2015():
    """
    Note
    ----
    - FIR1 filter (egglab)

    Reference
    ---------
    de Hemptinne, C., Swann, N. C., Ostrem, J. L., Ryapolova-Webb, E. S., 
    San Luciano, M., Galifianakis, N. B., & Starr, P. A. (2015). 
    Therapeutic deep brain stimulation reduces cortical phase-amplitude coupling
    in Parkinson’s disease. Nature Neuroscience, 18(5), 779–786. 
    https://doi.org/10.1038/nn.3997
    """
    pass

def FIR_filter_ince_2010(): 
    """
    - LFP recroded using percutaneous extension cable indicating recroding device
      other than the Medtronic Percept IPG.
    - Specified lead model 3389 is compatible with Medtronic Percept PC.
    - Low-pass FIR filter at 220 Hz cutoff indicates that the recording device
      sampling rate is greater than 440 Hz.

    “The LFP data from all contacts were low-pass filtered using an FIR filter 
    with 220 Hz cutoff frequency, and then down-sampled to 512 Hz.”    

    Reference:
    Ince, N. F., Gupte, A., Wichmann, T., Ashe, J., Henry, T., Bebler, M., 
    Eberly, L., & Abosch, A. (2010). Selection of Optimal Programming Contacts 
    Based on Local Field Potential Recordings From Subthalamic Nucleus in 
    Patients With Parkinson’s Disease. Neurosurgery, 67(2), 390. 
    https://doi.org/10.1227/01.NEU.0000372091.64824.63
    """
    pass


def IIR_butterworth_filter_hammer_2022(data: npt.NDArray, freqRange:tuple[float|int, float|int]=(1, 100), fs:float|int = 250) -> npt.NDArray:
    """Butterworth filter implemented in (Hammer, 2022).

    All data was analyzed using MathWorks MATLAB r2021a. Time series data 
    were first low-pass filtered using forward-backward filtering with a 
    seventh-order Butterworth filter with a cutoff frequency of 100 Hz. Three 
    methods of ECG removal were assessed: a new template subtraction pipeline, 
    singular value decomposition (SVD), and QRS interpolation. The template 
    subtraction technique was also implemented to remove non-ECG repetitive 
    artifacts.

    Reference:
    Hammer, L. H., Kochanski, R. B., Starr, P. A., & Little, S. (2022). 
    Artifact characterization and a multipurpose template-based offline 
    removal solution for a sensing-enabled deep brain stimulation device. 
    Stereotactic and Functional Neurosurgery, 100(3), 168. 
    https://doi.org/10.1159/000521431
    """

    order = 7

    # Butterworth filter design
    numerator, denominator = scp.signal.butter(
        N = order, 
        Wn = freqRange, 
        btype = "bandpass", 
        analog = False, 
        fs = fs,
    )
    
    # Filter
    pad_length = 3*max(len(numerator), len(denominator))-1 # Match Matlab filtfilt default - https://mail.python.org/pipermail/scipy-user/2014-April/035648.html
    filtered_signal = scp.signal.filtfilt(
        b=numerator, 
        a=denominator,
        x=data, 
        padlen = pad_length,
    )
    return filtered_signal


def IIR_butterworth_filter_connolly_2015(data: npt.NDArray, freqRange: tuple[float|int, float|int]=(1, 100), fs:float|int=250) -> npt.NDArray:
    """Butterworth filter implemented in (Connolly, 2015).
    
    “The data was filtered into the beta band using a 4th order butterworth 
    filter, and the root mean squared (rms) power was calculated across time.”

    Reference:
    Connolly, A. T., Muralidharan, A., Hendrix, C., Johnson, L., Gupta, R., 
    Stanslaski, S., Denison, T., Baker, K. B., Vitek, J. L., & Johnson, M. D. 
    (2015). Local field potential recordings in a non-human primate model of 
    Parkinsons disease using the Activa PC + S neurostimulator. Journal of 
    Neural Engineering, 12(6), 066012. 
    https://doi.org/10.1088/1741-2560/12/6/066012
    """
    pass

def IIR_butterworth_filter_young_2018() -> npt.NDArray:
    """
    “Next, a noncausal Butterworth bandpass filter (8th order) between 250Hz 
    to 5000Hz was applied.” ([Young et al., 2018, p. 8])

    Reference: 
    Young, D., Willett, F., Memberg, W. D., Murphy, B., Walter, B., Sweet, J., 
    Miller, J., Hochberg, L. R., Kirsch, R. F., & Ajiboye, A. B. (2018). 
    Signal processing methods for reducing artifacts in microelectrode brain 
    recordings caused by functional electrical stimulation. Journal of Neural 
    Engineering, 15(2), 026014. https://doi.org/10.1088/1741-2552/aa9ee8
    """
    pass

def IIR_butterworth_filter_10_percent_pad(data: npt.NDArray, freqRange: tuple[float|int, float|int], fs: float|int) -> npt.NDArray:
    """Bandpass filter - 10% pad length, implemented with Butterworth filter and filtfilt digital filter."""

    if (not isinstance(freqRange, tuple)) | (len(freqRange) != 2):
        raise ValueError(f"freqRange has to be a tuple of length two, got {freqRange} instead.")

    low_freq = freqRange[0]
    high_freq = freqRange[1]

    pad_length = int(len(data) / 10)  # 10% of signal data as padding

    numerator, denominator = scp.signal.butter(
        N=2, Wn=[low_freq, high_freq], btype="bandpass", analog=False, fs=fs
    )
    filtered_signal_data = scp.signal.filtfilt(
        b=numerator, a=denominator, x=data, padlen=pad_length
    )

    return filtered_signal_data