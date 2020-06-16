from abc import ABC, abstractmethod

class Blockchain(ABC):

    @abstractmethod
    def __str__(self):
        pass
