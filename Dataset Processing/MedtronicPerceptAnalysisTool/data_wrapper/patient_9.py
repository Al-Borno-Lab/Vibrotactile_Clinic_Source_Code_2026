# 2025-01-20 Anthony Lee

from typing import Union
from pathlib import Path
from .base import PatientObjAbstractBase
from ..utility import constants
from .utility import get_data_dir_path
from .patient_registry import PatientDatasetRegistry

patient_num_from_module = int(Path(__file__).stem.split("_")[-1])

@PatientDatasetRegistry.register(patient_num_from_module)
class Patient_9(PatientObjAbstractBase):
    def __init__(self, data_dir: Union[str, Path] = None):

        if data_dir is None:
            data_dir = (get_data_dir_path() / Path(f"Patient_{patient_num_from_module}_Data")).resolve()

        super().__init__(data_dir=data_dir)
        
        # self.stage_mapping = {
        #     "dbs_off": range(0, 12), 
        #     "all_on": range(12, 36),
        #     "test_connection": range(36, 38),  # Jesse testing connections of IPG
        #     "rvs": range(38, 62),
        # }
        self.stage_mapping = {
            str(constants.TreatmentStage.DBS_OFF): range(0, 6), 
            str(constants.TreatmentStage.ALL_ON): range(6, 18),
            "test_connection": range(18, 19),  # Jesse testing connections of IPG
            str(constants.TreatmentStage.RVS): range(19, 31),
        }
        self.treatment_order = str(constants.TreatmentStageOrder.ALLON_THEN_RVS)
        self.glove_hand = str(constants.StimGloveHand.LEFT)
        self.json_filenames = ["Report_Json_Session_Report_20250114T134835.json"]
        self.updrs_filename = f"UPDRS_Patient_{patient_num_from_module}.xlsx"