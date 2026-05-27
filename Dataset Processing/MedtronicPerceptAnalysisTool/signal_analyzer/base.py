import abc

class BaseSignalAnalyzer(abc.ABC):
    
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def __call__(self):
        pass