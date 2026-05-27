import abc

class BaseSignalProcessor(abc.ABC):
    """Defines the SignalProcessor interface."""
    
    @abc.abstractmethod
    def __init__(self):
        """Creates a signal processor."""
        pass
    
    @abc.abstractmethod
    def __call__(self):
        """Processes the signal."""
        pass