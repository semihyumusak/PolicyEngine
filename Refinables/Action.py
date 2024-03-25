"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the action class which implements refinable interface.

Contributors:

"""

from Constraint import Constraint
from Interfaces.Refinable import RefinableInterface

class Action(RefinableInterface):
    def remove_constraint(self, constraint: Constraint):
        self.refinements.remove(constraint)

    def add_constraint(self, constraint: Constraint):
        self.refinements.append(constraint)

    def __init__(self, value, refinements=None):
        """
        Initializes an Action instance.

        :param value: The main action, can be a string or an object representing the action.
        :param refinements: Optional list of Constraint objects that refine the conditions of the action.
        """
        self.value = value
        self.refinements = refinements if refinements is not None else []

