import pandas as pd

class PatientDatasetRegistry:
    __registry = {}
    
    def __init__(self,):
        self.__patient_list = list(self.__registry.keys())[::-1]
    
    @classmethod
    def register(cls, key:str|int):
        key = str(key)

        if key in cls.__registry:
        # if key in getattr(cls, 'registry'):
            raise KeyError(f"{key} already registered.")

        def inner_wrapper(patient_obj):
            cls.__registry[key] = patient_obj()
            return patient_obj

        return inner_wrapper
    
        
    def __getitem__(self, key:str|int):
        # return self.__registry[str(key)].get_dataframe()
        return self.__registry[str(key)]

    def __iter__(self,):
        return self
    
    def __next__(self,):
        if self.__patient_list:
            return self.__registry[self.__patient_list.pop()]
        else:
            raise StopIteration

    @property
    def registry(self,):
        return self.__registry

    
    @classmethod
    def all_dataframe_json(cls, ) -> pd.DataFrame:
        """Return a dataframe of normalized JSON files for all patients.
        
        Normalized all the JSON files for all patients. 
        Some patients have multiple JSON files, and the "BrainSenseTimeDomain"
        data could be split across multiple JSON files.
        
        This normalization makes comparing the metadata of each file convenient,
        such as "AbnormalEnd", "SessionDate", "SessionEndDate", "Stimulation"
        (stimulation on/off), "FeatureInformationCode", "ProgrammerVersion", etc.
        """
        
        holder_df = [pt_obj.get_dataframe_json() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            .sort_values(by=["PatientNumber", "SessionDate"])
            .reset_index(drop=True)
        )
        return result
    
    @classmethod
    def all_dataframe_brainsensetimedomain(cls, ) -> pd.DataFrame:
        """Return a datafame of all patients' "BrainSenseTimeDomain" data."""
        holder_df = [pt_obj.get_dataframe_brainsensetimedomain() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            .sort_values(by=["PatientNumber", "FirstPacketDateTime"])
            .reset_index(drop=True)
        )
        return result

    @classmethod
    def all_dataframe_lfp(cls, ) -> pd.DataFrame:
        """Return a datafame of all patients' LFP related calculated data."""
        holder_df = [pt_obj.get_dataframe_lfp() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            .sort_values(by=["PatientNumber", "FirstPacketDateTime"])
            .reset_index(drop=True)
        )
        return result

    @classmethod
    def all_dataframe_burst(cls, ) -> pd.DataFrame:
        """Return a datafame of all patients' beta burst calculated data."""
        holder_df = [pt_obj.get_dataframe_burst() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            .sort_values(by=["PatientNumber", "FirstPacketDateTime"])
            .reset_index(drop=True)
        )
        return result
    
    @classmethod
    def all_dataframe_pac(cls, ) -> pd.DataFrame:
        """Return a datafame of all patients' PAC calculated data."""
        holder_df = [pt_obj.get_dataframe_pac() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            .sort_values(by=["PatientNumber", "FirstPacketDateTime"])
            .reset_index(drop=True)
        )
        return result

    @classmethod
    def all_dataframe_updrs(cls, ) -> pd.DataFrame:
        """Return a datafame of all patients' UPDRS data."""
        holder_df = [pt_obj.get_dataframe_updrs() for pt_obj in cls.__registry.values()]
        result = (
            pd.concat(holder_df, axis=0)
            # .sort_values(by=["PatientNumber", "FirstPacketDateTime"])
            .reset_index(drop=True)
        )
        return result