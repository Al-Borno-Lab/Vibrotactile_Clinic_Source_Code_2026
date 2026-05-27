from datetime import datetime
from pathlib import Path

class PlotterRegistry:
    __registry = {}
    
    @classmethod
    @property
    def registry(cls, ):
        return cls.__registry

    def __init__(self,):
        self.__plotter_list = self.__registry.values()
        return self
    
    @classmethod
    def register(cls, key:str):
        
        key = str(key)
        
        if key in cls.registry:
            raise KeyError(f"{key} already registered.")

        def inner_wrapper(plotter):
            cls.__registry[key] = plotter
            return plotter

        return inner_wrapper
        
    
    def __getitem__(self, key:str):
        return self.__registry[str(key)]
    
    def __iter__(self, ):
        return self
    
    def __next__(self, ):
        if self.__plotter_list:
            return self.__plotter_list.pop()
        else:
            raise StopIteration

    @classmethod 
    def all(cls, ):

        timestamp = datetime.now().strftime("%Y%m%d")
        storage_dir = (Path() / Path(f"Figure_{timestamp}")).resolve()
        storage_dir.mkdir(exist_ok=True)
        
        for plotter_name, plotter in cls.registry.items():
            fig = plotter()
            fig.savefig(storage_dir / Path(f"{plotter_name}.svg"))
        
        return