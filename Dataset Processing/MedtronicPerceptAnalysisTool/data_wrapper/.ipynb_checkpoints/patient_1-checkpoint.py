# 2025-01-20 Anthony Lee

from typing import Union
from pathlib import Path
from .base import Patient_Dataset_Base
from ..utility import PROTOCOL_STAGES

class Patient_1_Dataset(Patient_Dataset_Base):
    def __init__(self, data_dir: Union[str, Path]):
        super().__init__(data_dir=data_dir)
        self.stage_mapping = {
            "marker_1": range(0, 2),             # 0-1 inclusive - 1x session each hemisphere
            "dbs_off": range(2, 14),             # 2-13 inclusive - 6x sessions each hemisphere
            "marker_2": range(14, 16),           # 14-15 inclusive - 1x session each hemisphere
            "all_on": range(16, 40),             # 16-39 inclusive - 12x sessions each hemisphere
            "rvs": range(40, 64),                # 40-63 inclusive - 12x sessions each hemisphere
        }
        self.glove_hand = "right"
        self.json_filenames = [
            "Report_Json_Session_Report_20240126T133016.json",
            "Report_Json_Session_Report_20240126T133039.json",
        ]
        self.updrs_filename = "UPDRS_Patient_1.xlsx"