# 2025-01-21 Anthony Lee

import os
import json
from datetime import datetime, tzinfo, timezone, timedelta, time
from typing import Union, List, Iterable, Dict
from pathlib import Path
import pandas as pd

def get_sampling_freq(patient_df: pd.DataFrame) -> int:
    """Convenience function"""
    sampling_rates = patient_df.SampleRateInHz
    assert (
        len(sampling_rates.unique()) == 1
    ), f"More than one sampling rate detected, should only have one sample rate but got the following unique rates: {sampling_rates.unique()}"

    result = int(sampling_rates.iloc[0])
    return result

def get_data_dir_path() -> Path:
    
    root_package = __package__.split(".").pop(0)
    data_path = (Path(root_package).parent / Path("data")).resolve()
    
    return data_path

## TODOs: 
## - chained parser - Create a chained parser
## - plotter class - The plotter is responsible for plotting and returning axes 
##   - Add the feature to mark the events (Events are the things that occured 
##     during the recording)
## - privacy - Add function to remove patient information

## Notes: 
## - The goal is to always return a pandas dataframe, which is a well documented
##   type and have various utility functions such as saving to CSV.


def save_json(dict_to_save:dict, file_name:str, dir_path:Path=None): 
    """Save the dictionary as a JSON file.
    
    Arg
    ===
    dict_to_save (dict): Dictionary to be saved.
    file_name (str): File name for the dictionary to be saved as.
    dir_path (Path): [optional] The directory for the JSON to be saved at.
    """
    if dir_path is None: 
        dir_path = Path.cwd()

    ## Remove extension from name
    file_name = file_name.replace(".json", "")
    
    ## Create the saving path
    dir_path = Path(dir_path, f"{file_name}.json")

    with open(dir_path, "w") as file: 
        json.dump(dict_to_save, file, indent=4)

    return

def parse_naive_utc_time_str(time_str: str, format: str = None) -> datetime:
    """Parse a time string in UTC to a timeaware datetime object.

    The data are default logged in UTC and of type string. This utility function
    parses the string literal and returns the datetime object to make further
    time offset manipulation much easier. 

    Args:
      time_str (str) : The string is assumed to be in UTC.
    """

    if format == None:
        format = "%Y-%m-%dT%H:%M:%S.%fZ"

    str_parsed_time = datetime.strptime(time_str, format)      # TZ naive time
    aware_time = str_parsed_time.replace(tzinfo=timezone.utc)  # TZ aware time (by adding tzinfo)

    return aware_time

# def convertIntStringList(str_literal: str, sep=',', dtype=np.int64) -> np.ndarray:
#     """Convert comma separated integer literals to List[int].
    
#     Converts a string like `'1,2,3,4,5,6,` to `[1, 2, 3, 4, 5, 6]`.
#     This is mostly used as a utility function for the parseing or extracting
#     process, especially for data such as the `GlobalSequence`, `GlobalPacketSizes`, 
#     and `TicksInMses`. These data are supposed to be a sequence of element, but
#     instead was recorded as a long continuous string.

#     Args: 
#         str_literal (str): A string delimited by `sep` to be splitted
#         sep (str): The delimiter. Default = ','
#         dtype (type): The data type each element to be converted to. Default = np.int64
#     """
#     return np.fromstring(str_literal, sep=sep, dtype=dtype)

def parseJsonSections(filePath: Union[Path, str]) -> pd.DataFrame: 
    """Parses a index-oriented JSON file and return a pd.DataFrame with appropriate column names.

    Args: 
        filePath (Path | str): A path object or string to the JSON file.
    Returns: 
        pd.DataFrame: A pandas DataFrame object with appropriate column names.
    """
    if isinstance(filePath, str): 
        filePath = Path(str)
    df = pd.read_json(filePath, orient="index")
    df = df.rename(mapper={0: "Data"}, axis=1)
    df = df.reset_index(drop=False, names="SectionName")
    df = df.set_index("SectionName")

    return df

def parseRecordLists(records: List[dict]) -> pd.DataFrame:
    """Parses records formatted as a list of dictionary to a pandas DataFrame.
    
    Certain time series data is recorded as a list of dictionary where each 
    dictionary may be a snapshot of a recording event.

    Args: 
        records (list): List of dictionary, where each dictionary is a record.
    Returns: 
        (pandas.DataFrame): DataFrame where each row is an entry in the list.
    """
    assert isinstance(records, list), "`records` need to be a list of dictionaries."
    df = pd.json_normalize(records)
    return df

def parseRecordDict(record: dict) -> pd.DataFrame: 
    """Parses record as a dict format to a pandas DataFrame."""
    assert isinstance(record, dict), "`record` has to be a dict."
    df = pd.DataFrame.from_dict(record, orient="index")
    return df

def determineTypesOfRecords(data) -> str: 
    """Determien the record type so to be able to leverage the proper parsing function.
    
    (WORK IN PROGRESS!!!)
    """
    if isinstance(data, pd.Series):
        #print("Of type pd.Series and needs a little more work.")
        data = data.to_numpy()[0]  # Convert to numpy and take the 1st element

    if isinstance(data, list):
        return 'list_of_records'

    if isinstance(data, dict):
        first_key = list( data.keys() )[0]
        ## Check if just a dictionary
        if isinstance(data[first_key], dict): 
            return 'dict_of_dict'
        ## Check if first value of dict is a record list
        if isinstance(data[first_key], list): 
            return 'dict_of_list'
        ## Last case
        else: 
            return 'dict'
    return str( type(data) )


# def add_treatment_branch(df_lfp:pd.DataFrame, dbs_off_session_num:Iterable, all_on_session_num:Iterable, rvs_session_num:Iterable)->pd.DataFrame: 
    
#     df = df_lfp
#     simple_mapping = {
#         "dbs_off": dbs_off_session_num, 
#         "all_on": all_on_session_num, 
#         "rvs": rvs_session_num,
#     }
#     mapping = {}

#     for key, value in simple_mapping.items(): 
#         for item in value: 
#             mapping[ str(item) ] = key

#     df.loc[:, "TreatmentBranch"] = [mapping[str(num)] for num in df.index.to_numpy()]
    
#     return df