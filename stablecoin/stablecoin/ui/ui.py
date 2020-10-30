from abc import ABC, abstractmethod

class UI(ABC):

    @abstractmethod
    def __str__(self):
        pass
