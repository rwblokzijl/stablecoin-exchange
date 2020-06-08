from abc import ABC, abstractmethod

class Persistence(ABC):

    @abstractmethod
    def __str__(self):
        pass
