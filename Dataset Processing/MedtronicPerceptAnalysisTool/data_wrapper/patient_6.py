# 2025-01-20 Anthony Lee

from typing import Union
from pathlib import Path
from .base import PatientObjAbstractBase
from .patient_registry import PatientDatasetRegistry

# patient_num_from_module = int(Path(__file__).stem.split("_")[-1])

# @PatientDatasetRegistry.register(patient_num_from_module)
class Patient_6(PatientObjAbstractBase):
    def __init__(self, data_dir: Union[str, Path] = None):
        raise NotImplementedError(f"Patient 6 withdrew from the study prior to any data collection.")
