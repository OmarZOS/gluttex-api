from abc import ABC, abstractmethod

class StorageService(ABC):
    
    @abstractmethod
    def test_connection(api):
        pass
    @abstractmethod
    def saveData(data):
        pass
    @abstractmethod
    def queryData(*args):
        pass