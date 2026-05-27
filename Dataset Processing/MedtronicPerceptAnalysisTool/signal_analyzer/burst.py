from ..data_wrapper.base import Patient_Dataset_Base
import pandas as pd
from .base import BaseSignalAnalyzer
from ..utility import get_full_beta_freq_range, get_sampling_rate
    

    
class DualThresholdFullBetaBurstAnalyzer(BaseSignalAnalyzer):
    def __init__(self):#, dual_threshold:tuple, freq_range:tuple, sampling_freq:int, magnitude_type:str, avg_type:str):
        self._dual_threshold = (1, 1.3)
        self._freq_range = get_full_beta_freq_range()
        pass

    def __call__(self, pt_obj:Patient_Dataset_Base):
        from ..signal_processor.burst import DualThresholdBurstProcessor

        df = pt_obj.get_dataframe()

        full_beta_processor = DualThresholdBurstProcessor(
            dual_threshold=self._dual_threshold,
            freq_range=self._freq_range,
            sampling_freq=get_sampling_rate(df),
            magnitude_type="power",
            avg_type="mean"
        )

        df_stats = df.apply(
            lambda x: full_beta_processor(x["TimeDomainData"], "stat"), 
            axis=1, 
            result_type="expand"
        )

        df_combined = pd.concat([df, df_stats], axis=1)
        
        result = (df_combined
            .pivot(
                index=["PatientNumber", "TreatmentBranch", "FirstPacketDateTime"],
                columns="IpsiContra",
                values=df_stats.columns,)
            .sort_values(by="FirstPacketDateTime")
        )

        return result

    @property
    def dual_threshold(self):
        return self._dual_threshold

    @property
    def freq_range(self):
        return self._freq_range