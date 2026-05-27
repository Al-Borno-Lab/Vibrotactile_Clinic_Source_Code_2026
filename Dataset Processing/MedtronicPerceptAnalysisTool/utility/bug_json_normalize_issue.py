import MedtronicPerceptAnalysisTool as mpat
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from pprint import pprint
from typing import Dict
from pathlib import Path
import MedtronicPerceptAnalysisTool as mpat

## Setting up some variables
base_dir_path = Path("./data/Patient_3_Data")
json_paths = ["Report_Json_Session_Report_20240528T174157.json", "Report_Json_Session_Report_20240528T174146.json",]
json_paths = [base_dir_path/Path(json_path) for json_path in json_paths]

##### treatment_mapping = {
#####     "dbs_off": range(0, 14), 
#####     "rvs": range(14, 38),
#####     "all_on": range(38, 44),
##### }
##### 
##### treatment_order = ['dbs_off', 'rvs', 'all_on']

## Read in the json path
for json_path in json_paths: 
    with open(json_path, "r") as file: 
        json_dict = json.load(file)
        print(json_dict.keys())
        print()

################################################################################
## INVESTIGATE THIS BUG, WHEN HAVING META DATA WILL THROW ERROR ##
## Resolution: 
## This bug exist in v1.5.3, however it was addressed in v2.1.0 in August 30,
## 2023 in reference to GH issue #37782.
##
## [v2.1.0 Change notes](https://pandas.pydata.org/docs/whatsnew/v2.1.0.html#bug-fixes)
## [GH 37782](https://github.com/pandas-dev/pandas/issues/37782)
################################################################################

json_path = json_paths[1]

with open(json_path, "r") as file: 
    json_dict = json.load(file)

    ## Pop "SenseChannelTests" and "CalibrationTests" from the first json dictionary
    # json_dict.pop("SenseChannelTests")
    # json_dict.pop("CalibrationTests")

    # pprint(json_dict["BrainSenseTimeDomain"])
    # mpat.parser.extract_BrainSenseTimeDomain_from_unserialized(json_dict)

    output_df = pd.json_normalize(
        json_dict, 
        record_path=["BrainSenseTimeDomain"], 
        meta=[
            "ProgrammerUtcOffset", 
            "ProgrammerVersion", 
            "BatteryInformation", 
            "LeadConfiguration", 
            "Impedance"
        ], 
        meta_prefix="Metadata.")
    
    print(output_df)

    # print( json_dict["ProgrammerUtcOffset"] )