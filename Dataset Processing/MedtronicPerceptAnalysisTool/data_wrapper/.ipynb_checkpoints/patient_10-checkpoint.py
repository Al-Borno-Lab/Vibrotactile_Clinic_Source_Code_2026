from typing import Union
from pathlib import Path
from .base import Patient_Dataset_Base
from ..utility import PROTOCOL_STAGES

class Patient_10_Dataset(Patient_Dataset_Base):
    def __init__(self, data_dir: Union[str, Path]):
        super().__init__(data_dir=data_dir)
        self.stage_mapping = {
            "dbs_off": range(0, 14), 
            "rvs": range(14, 38),
            "all_on": range(38, 62),
        }
        self.glove_hand = "right"
        self.json_filenames = ["Report_Json_Session_Report_20250429T123558.json"]
        self.updrs_filename = "UPDRS_Patient_10.xlsx"