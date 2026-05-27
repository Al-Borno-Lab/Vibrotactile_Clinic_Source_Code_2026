# 2025-01-20 Anthony Lee

from typing import Union
from pathlib import Path
from .base import PatientObjAbstractBase
from ..utility import constants
from .patient_registry import PatientDatasetRegistry
from .utility import get_data_dir_path

# print("Module level resolve: ", Path().cwd().resolve())  # Resolves to where the initiating script is located

patient_num_from_module = int(Path(__file__).stem.split("_")[-1])

@PatientDatasetRegistry.register(patient_num_from_module)
class Patient_1(PatientObjAbstractBase):
    
    def __init__(self, data_dir: Union[str, Path] = None):

        if data_dir is None:
            data_dir = (get_data_dir_path() / Path(f"Patient_{patient_num_from_module}_Data")).resolve()

        super().__init__(data_dir=data_dir)

        self.stage_mapping = {
            "marker_1": range(0, 1),  # 1x session each hemisphere
            str(constants.TreatmentStage.DBS_OFF): range(1, 7),  # 6x sessions each hemisphere
            "marker_2": range(7, 8),  # 1x session each hemisphere
            str(constants.TreatmentStage.ALL_ON): range(8, 20),  # 12x sessions each hemisphere
            str(constants.TreatmentStage.RVS): range(20, 32),  # 12x sessions each hemisphere
        }
        self.treatment_order = str(constants.TreatmentStageOrder.ALLON_THEN_RVS)
        self.glove_hand = str(constants.StimGloveHand.RIGHT)
        self.json_filenames = [
            "Report_Json_Session_Report_20240126T133016.json",
            "Report_Json_Session_Report_20240126T133039.json",
        ]
        self.updrs_filename = f"UPDRS_Patient_{patient_num_from_module}.xlsx"
