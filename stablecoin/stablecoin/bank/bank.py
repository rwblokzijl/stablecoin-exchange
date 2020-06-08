from abc import ABC, abstractmethod

class Bank(ABC):

    @abstractmethod
    def __str__(self):
        pass
