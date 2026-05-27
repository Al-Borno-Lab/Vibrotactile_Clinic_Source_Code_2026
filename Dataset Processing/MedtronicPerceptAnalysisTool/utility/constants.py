# 2025-01-21 Anthony Lee
import enum
import warnings
import logging
from .constants_support import BIOMARKER_BANDS_FASANO_2024

logger = logging.getLogger(__name__)

class FrequencyRange(enum.Enum):
    MedtronicPerceptRange = (1, 100)
    LowBeta = BIOMARKER_BANDS_FASANO_2024["low-beta"]
    HighBeta = BIOMARKER_BANDS_FASANO_2024["high-beta"]
    Beta = (BIOMARKER_BANDS_FASANO_2024["low-beta"][0], BIOMARKER_BANDS_FASANO_2024["high-beta"][1])

class TreatmentStage(enum.StrEnum):
    DBS_OFF = "dbs_off"
    ALL_ON = "all_on"
    RVS = "rvs"

class LateralSide(enum.StrEnum):
    IPSILATERAL = "ipsi"
    CONTRALATERAL = "contra"

class StimGloveHand(enum.StrEnum):
    RIGHT = "right"
    LEFT = "left"

class Hemisphere(enum.StrEnum):
    RIGHT = "right"
    LEFT = "left"
    
class TreatmentStageOrder(enum.StrEnum):
    ALLON_THEN_RVS = ",".join(
        (
            str(TreatmentStage.DBS_OFF), 
            str(TreatmentStage.ALL_ON), 
            str(TreatmentStage.RVS),
        )
    )
    RVS_THEN_ALLON = ",".join(
        (
            str(TreatmentStage.DBS_OFF), 
            str(TreatmentStage.RVS), 
            str(TreatmentStage.ALL_ON),
        )
    )

class PlotColorHemisphere(enum.StrEnum):
    LEFT = "Blue"
    RIGHT = "Red"
    
class ColumnNames_Main(enum.StrEnum):
    patient_num = "PatientNumber"
    treatment_branch = "TreatmentBranch"
    treatment_num = "TreatmentNumber"
    treatment_order = "TreatmentOrder"
    channel = "Channel"
    recording_hemisphere = "RecordingHemisphere"
    filename = "Filename"
    lateral_side = "IpsiContra"
    psd = "PSD"
    stimglovehand = "StimGloveHand"
    datetime_first_packet = "FirstPacketDateTime"


class ColumnNames_PSD(enum.StrEnum):
    PSD_medtronic = "PSD"
    PSD_Baseline_InterTreatment = "PSD_Baseline_InterTreatment"
    PSD_Baseline_IntraTreatment = "PSD_Baseline_IntraTreatment"

PlotColorStage = enum.StrEnum(
    "PlotColorStage", 
   [(treatment_stage._name_, color) for (treatment_stage, color) in zip(
       TreatmentStage, 
       ["lightslategray", "steelblue", "salmon"]
       )
    ]
)

### Re-exporting, but will remove in the future
# warnings.warn(
#     message=f"The constants are re-exported into module '{__name__}', but will be removed in the future.",
# )
# from .constants_support import *