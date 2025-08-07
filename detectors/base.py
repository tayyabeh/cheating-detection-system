# abstract class
from abc import ABC, abstractmethod

class BaseDetector(ABC):
    @abstractmethod
    def detect (self , frame) -> dict:
        pass 