# 2025-01-20 Anthony Lee

from typing import Union
from pathlib import Path
from .base import PatientObjAbstractBase
from ..utility import constants
from .utility import get_data_dir_path
from .patient_registry import PatientDatasetRegistry

patient_num_from_module = int(Path(__file__).stem.split("_")[-1])

@PatientDatasetRegistry.register(patient_num_from_module)
class Patient_7(PatientObjAbstractBase):
    def __init__(self, data_dir: Union[str, Path] = None):

        if data_dir is None:
            data_dir = (get_data_dir_path() / Path(f"Patient_{patient_num_from_module}_Data")).resolve()

        super().__init__(data_dir=data_dir)

        self.stage_mapping = {
            str(constants.TreatmentStage.DBS_OFF): list(range(0, 5)) + list(range(7, 8)),        # Ignore session 10, 11, 12, 13 as they are connection tests
            "test_connection1": range(5, 7),                         # Ignore sessions because they are test connections
            str(constants.TreatmentStage.ALL_ON): range(8, 16),                                  # 8x all-on sessions because fire-alarm in building and this had to be shortened
            "test_connection2": range(16, 17),                       # Jesse testing connections of IPG
            str(constants.TreatmentStage.RVS): range(17, 27),                                    # Only has 27 recrodings for each hemisphere (with 3 being connection tests)
        }
        self.treatment_order = str(constants.TreatmentStageOrder.ALLON_THEN_RVS)
        self.glove_hand = str(constants.StimGloveHand.RIGHT)
        self.json_filenames = ["Report_Json_Session_Report_20240910T125232.json"]
        self.updrs_filename = f"UPDRS_Patient_{patient_num_from_module}.xlsx"
