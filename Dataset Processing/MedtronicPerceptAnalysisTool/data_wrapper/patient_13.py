from typing import Union
from pathlib import Path
from .base import PatientObjAbstractBase
from ..utility import constants
from .utility import get_data_dir_path
from .patient_registry import PatientDatasetRegistry

patient_num_from_module = int(Path(__file__).stem.split("_")[-1])

@PatientDatasetRegistry.register(patient_num_from_module)
class Patient_13(PatientObjAbstractBase):
    def __init__(self, data_dir: Union[str, Path] = None):

        if data_dir is None:
            data_dir = (get_data_dir_path() / Path(f"Patient_{patient_num_from_module}_Data")).resolve()

        super().__init__(data_dir=data_dir)
        
        self.stage_mapping = {
            str(constants.TreatmentStage.DBS_OFF): range(0, 7), # 0-6 inclusive
            str(constants.TreatmentStage.ALL_ON): range(7, 19), # 7-18 inclusive
            str(constants.TreatmentStage.RVS): range(19, 31), # 19-30 inclusive
        }
        self.treatment_order = str(constants.TreatmentStageOrder.ALLON_THEN_RVS)
        self.glove_hand = str(constants.StimGloveHand.LEFT)
        self.json_filenames = ["Report_Json_Session_Report_20250716T141544.json"]
        self.updrs_filename = f"UPDRS_Patient_{patient_num_from_module}.xlsx"