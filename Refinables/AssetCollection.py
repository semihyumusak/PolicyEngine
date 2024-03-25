"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the asset collection class which implements refinable interface.

Contributors:

"""


from Constraint import Constraint
from Interfaces.Refinable import RefinableInterface


class AssetCollection(RefinableInterface):

    def remove_constraint(self, constraint: Constraint):
        self.refinements.remove(constraint)

    def add_constraint(self, constraint: Constraint):
        self.refinements.append(constraint)

    def __init__(self, identifier, refinement=None):
        """
        Initializes an AssetCollection instance.

        :param identifier: A string or an object representing the collection. If an object, it should have a 'source' attribute.
        :param refinement: Optional; a list of Constraint objects that refine the conditions of the asset collection.
        """
        self.identifier = identifier
        self.refinements = refinement if refinement is not None else []

