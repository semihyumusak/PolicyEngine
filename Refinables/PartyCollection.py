"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the party collection class which implements refinable interface.

Contributors:

"""

from Constraint import Constraint
from Interfaces.Refinable import RefinableInterface

class PartyCollection(RefinableInterface):
    def remove_constraint(self, constraint: Constraint):
        self.refinement.remove(constraint)

    def add_constraint(self, constraint: Constraint):
        self.refinement.append(constraint)

    def __init__(self, identifier, refinement=None):
        """
        Initializes a PartyCollection instance.

        :param identifier: A string or an object representing the collection of parties. If an object, it should have a 'source' attribute.
        :param refinement: Optional; a list of Constraint objects that refine the conditions of the party collection.
        """
        self.identifier = identifier
        self.refinement = refinement if refinement is not None else []
