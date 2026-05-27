# 2025-01-21 Anthony Lee
from .constants import *
from . import constants
from . import json_support
from . import stats
from . import util
from . import template_subtraction




def get_full_beta_freq_range():
    result = (
        constants.BIOMARKER_BANDS_FASANO_2024["low-beta"][0],
        constants.BIOMARKER_BANDS_FASANO_2024["high-beta"][1],
    )
    return result

def get_low_beta_freq_range():
    return constants.BIOMARKER_BANDS_FASANO_2024["low-beta"]

def get_high_beta_freq_range():
    return constants.BIOMARKER_BANDS_FASANO_2024["high-beta"]

def get_sampling_rate(df):
    """Get sampling rate and check rate consistency."""
    assert len(df.SampleRateInHz.unique()) == 1, "More than one sampling rate detected."
    return df.SampleRateInHz[0]