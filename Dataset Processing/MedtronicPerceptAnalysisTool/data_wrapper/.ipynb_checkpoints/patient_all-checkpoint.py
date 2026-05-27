# 2025-01-20 Anthony Lee

from typing import Iterable
from .base import Patient_Dataset_Base
import pandas as pd

class Patient_All_Dataset():
    def __init__(self, patient_datasets:Iterable[Patient_Dataset_Base]):
        """Takes all the patient data objects and return a combined dataframe (with some processing)."""
        self.__list_of_patient_datasets = patient_datasets

    def __iter__(self, ):
        return (patientObject for patientObject in self.__list_of_patient_datasets)

    def get_dataframe(self) -> pd.DataFrame:
        holder_df = []
        for dataset in self:
            df = dataset.get_dataframe()
            holder_df.append(df)
        df = pd.concat(holder_df).reset_index(drop=True)
        return df