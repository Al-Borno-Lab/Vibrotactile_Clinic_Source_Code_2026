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
            return self.__registry[self.__patient_list.pop()].get_dataframe()
        else:
            raise StopIteration

    @property
    def registry(self,):
        return self.__registry

    @classmethod
    def all(cls, ):
        holder_df = [pt_obj.get_dataframe() for pt_obj in cls.__registry.values()]
        result = pd.concat(holder_df, axis=0).reset_index(drop=True)
        return result