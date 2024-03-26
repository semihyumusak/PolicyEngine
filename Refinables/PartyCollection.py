"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the party collection class which implements refinable interface.

Contributors:

"""
from typing import List

from Constraint import Constraint
from Interfaces.Refinable import RefinableInterface

class PartyCollection(RefinableInterface):
    def __init__(self, source: str, refinements: List[Constraint] = None):
        """
        Initializes a PartyCollection instance.

        :param source: The source reference of the PartyCollection.
        :param refinements: Optional list of Constraint objects that refine the conditions of the PartyCollection.
        """
        self.source = source
        self.refinements = refinements if refinements is not None else []

    def add_refinement(self, constraint: Constraint):
        """
        Adds a refinement to the PartyCollection.

        :param constraint: Constraint object to be added as a refinement.
        """
        self.refinements.append(constraint)

    def remove_refinement(self, constraint: Constraint):
        """
        Removes a refinement from the PartyCollection.

        :param constraint: Constraint object to be removed from refinements.
        """
        if constraint in self.refinements:
            self.refinements.remove(constraint)
