import pandas as pd
import numpy as np
from ..data_wrapper.base import Patient_Dataset_Base

def calculate_mean_psd_of_freqRange(pt_data_obj: Patient_Dataset_Base, freqRange: tuple) -> pd.DataFrame:
    
    assert (isinstance(freqRange, tuple) & (len(freqRange)==2)), f"freqRange has to be a tuple of length 2, got {freqRange}"
    pt = pt_data_obj
    df: pd.DataFrame = pt.get_dataframe()
    
    # Construct nested function
    def func_to_apply(lfp_data):
        sampling_freq = 250
        freq_range = freqRange
        lfp_data = np.array(lfp_data)
        
        filtered_data = pt._bandpass_filter(data=lfp_data, freqRange=freq_range, fs=sampling_freq)
        freq, psd = pt._calculate_psd(data=filtered_data, fs=sampling_freq)
        mask = (freq >= freq_range[0]) & (freq <= freq_range[1])
        psd_subset = psd[mask]
        
        return psd_subset.mean()

    # Variables
    data_colname = "TimeDomainData"
    dest_colname = f"MeanPSD_{freqRange}"
    
    # Row-by-row calculation
    df[dest_colname] = df[data_colname].apply(lambda element: func_to_apply(element))
    
    # Pivot table
    temp = df.pivot(index=["Channel", "RecordingHemisphere", "StimGloveHand", "TreatmentOrder", "SessionNumber"], columns="TreatmentBranch", values=dest_colname)
    temp = temp.stack().to_frame(name=dest_colname).reset_index(drop=False)
    
    return temp

def calculate_psd_of_freqRange(pt_data_obj: Patient_Dataset_Base, freqRange: tuple) -> pd.DataFrame:
    
    assert (isinstance(freqRange, tuple) & (len(freqRange)==2)), f"freqRange has to be a tuple of length 2, got {freqRange}"
    pt = pt_data_obj
    df: pd.DataFrame = pt.get_dataframe()
    
    # Construct nested function
    def func_to_apply(lfp_data):
        sampling_freq = 250
        freq_range = freqRange
        lfp_data = np.array(lfp_data)
        
        filtered_data = pt._bandpass_filter(data=lfp_data, freqRange=freq_range, fs=sampling_freq)
        freq, psd = pt._calculate_psd(data=filtered_data, fs=sampling_freq)
        mask = (freq >= freq_range[0]) & (freq <= freq_range[1])
        psd_subset = psd[mask] 
        return psd_subset

    # Variables
    data_colname = "TimeDomainData"
    dest_colname = f"PSD_{freqRange}"
    
    # Row-by-row calculation
    df[dest_colname] = df[data_colname].apply(lambda element: func_to_apply(element))
    
    # Pivot table
    temp = df.pivot(index=["Channel", "RecordingHemisphere", "StimGloveHand", "TreatmentOrder", "SessionNumber"], columns="TreatmentBranch", values=dest_colname)
    temp = temp.stack().to_frame(name=dest_colname).reset_index(drop=False)
    
    return temp