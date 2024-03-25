"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the refinable interface.

Contributors:

"""


from abc import abstractmethod, ABC

class RefinableInterface(ABC):

    @abstractmethod
    def add_constraint(self, constraint):
        pass
    @abstractmethod
    def remove_constraint(self, constraint):
        pass
