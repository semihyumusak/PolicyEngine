"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the action class which implements refinable interface.

Contributors:

"""

from typing import List

from Constraint import Constraint
from Interfaces import RefinableInterface


class Action(RefinableInterface):
    def __init__(self, value: str, refinements: List[Constraint] = None, included_in: 'Action' = None,
                 implies: List['Action'] = None):
        """
        Initializes an Action instance.

        :param value: The main action, can be a string or an object representing the action.
        :param refinements: Optional list of Constraint objects that refine the conditions of the action.
        :param included_in: The encompassing Action.
        :param implies: Optional list of Actions that are implied by this Action.
        """
        self.value = value
        self.refinements = refinements if refinements is not None else []
        self.included_in = included_in
        self.implies = implies if implies is not None else []

    def add_refinement(self, constraint: Constraint):
        """
        Adds a refinement to the action.

        :param constraint: Constraint object to be added as a refinement.
        """
        self.refinements.append(constraint)

    def remove_refinement(self, constraint: Constraint):
        """
        Removes a refinement from the action.

        :param constraint: Constraint object to be removed from refinements.
        """
        if constraint in self.refinements:
            self.refinements.remove(constraint)

    """
    #TODO Check semantics of imply property, if this is valid or not"""

    def add_implied_action(self, action: 'Action'):
        """
        Adds an implied action.

        :param action: Action object to be added as an implied action.
        """
        self.implies.append(action)


class AssetCollection(RefinableInterface):
    def __init__(self, source: str, refinements: List[Constraint] = None):
        """
        Initializes an AssetCollection instance.

        :param source: The source reference of the AssetCollection.
        :param refinements: Optional list of Constraint objects that refine the conditions of the AssetCollection.
        """
        self.source = source
        self.refinements = refinements if refinements is not None else []

    def add_refinement(self, constraint: Constraint):
        """
        Adds a refinement to the AssetCollection.

        :param constraint: Constraint object to be added as a refinement.
        """
        self.refinements.append(constraint)

    def remove_refinement(self, constraint: Constraint):
        """
        Removes a refinement from the AssetCollection.

        :param constraint: Constraint object to be removed from refinements.
        """
        if constraint in self.refinements:
            self.refinements.remove(constraint)


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
