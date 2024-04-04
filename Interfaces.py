"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the refinable interface.

Contributors:

"""

from abc import abstractmethod, ABC

from Constraint import Constraint


class RefinableInterface(ABC):
    @abstractmethod
    def add_refinement(self, constraint: Constraint):
        pass
    @abstractmethod
    def remove_refinement(self, constraint: Constraint):
        pass
