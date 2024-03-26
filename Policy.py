"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is file containing Policy and rule classes.

Contributors:

"""

from typing import Union

from Refinables import Action
from Refinables import AssetCollection
from Refinables import PartyCollection
from Constraint import Constraint

class Rule:
    def __init__(self, action: Action, target: AssetCollection = None, assigner: Union[PartyCollection, None] = None, assignee: Union[PartyCollection, None] = None, constraints: list[Union[Constraint, 'LogicalConstraint']] = None, uid: str = None):
        """
        Initializes a Rule instance.

        :param action: The action associated with the Rule.
        :param target: Optional; the target AssetCollection associated with the Rule.
        :param assigner: Optional; the assigner PartyCollection associated with the Rule.
        :param assignee: Optional; the assignee PartyCollection associated with the Rule.
        :param constraints: Optional list of Constraint or LogicalConstraint objects associated with the Rule.
        :param uid: Optional; the unique identifier of the Rule.
        """
        self.action = action
        self.target = target
        self.assigner = assigner
        self.assignee = assignee
        self.constraints = constraints if constraints is not None else []
        self.uid = uid
        self.state = "Inactive"  # Default state is Inactive

    def add_constraint(self, constraint: Union[Constraint, 'LogicalConstraint']):
        """
        Adds a constraint to the Rule.

        :param constraint: Constraint or LogicalConstraint object to be added.
        """
        self.constraints.append(constraint)

    def remove_constraint(self, constraint: Union[Constraint, 'LogicalConstraint']):
        """
        Removes a constraint from the Rule.

        :param constraint: Constraint or LogicalConstraint object to be removed.
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)

    def clear_constraints(self):
        """
        Clears all constraints associated with the Rule.
        """
        self.constraints = []

    def activate(self):
        """
        Activates the Rule.
        """
        self.state = "Active"

    def deactivate(self):
        """
        Deactivates the Rule.
        """
        self.state = "Inactive"

    def is_active(self) -> bool:
        """
        Checks if the Rule is active.

        :return: True if the Rule is active, False otherwise.
        """
        return self.state == "Active"


class Policy:
    def __init__(self, uid, profiles=None, inherit_from=None, conflict=None):
        self.uid = uid
        self.rules = []
        self.profiles = profiles if profiles else []
        self.inherit_from = inherit_from if inherit_from else []
        self.conflict = conflict
    def addRule(self, rule:Rule):
        self.rules.append(rule)
    def removeRule(self, rule:Rule):
        self.rules.remove(rule)

class Permission(Rule):
    def __init__(self, target, action, assigner, assignee, duty=None):
        """
        Initializes a Permission instance, extending the Rule class with an additional 'duty' property.

        :param target: The object or entity the permission applies to.
        :param action: The action permitted by the permission.
        :param assigner: The entity that grants the permission.
        :param assignee: The entity to whom the permission is granted.
        :param duty: Optional; an Action instance representing the duty associated with the permission.
        """
        super().__init__(target, action, assigner, assignee)
        self.duty = duty

    def set_duty(self, duty):
        """
        Sets or updates the duty associated with the permission.

        :param duty: Action instance representing the duty.
        """
        self.duty = duty

    def clear_duty(self):
        """
        Removes the duty associated with the permission.
        """
        self.duty = None

    def is_used(self):
        pass


class Prohibition(Rule):
    def __init__(self, target, action, assigner, assignee, remedy:Duty):
        """
        Initializes a Prohibition instance, extending the Rule class with an additional 'remedy' property.

        :param target: The object or entity the prohibition applies to.
        :param action: The action permitted by the prohibition.
        :param assigner: The entity that grants the prohibition.
        :param assignee: The entity to whom the prohibition is granted.
        :param remedy: Optional; an Action instance representing the remedy associated with the prohibition.
        """
        super().__init__(target, action, assigner, assignee)
        self.remedy = remedy


    def is_violated(self):
        """
        Checks if the prohibition has been violated.

        :return: True if the prohibition has been violated, False otherwise.
        """
        # # TODO: Implement your logic to check if the prohibition is violated here
        # For example, if the remedy is not None, consider it as violated
        return self.remedy is not None

    def set_remedy(self, remedy):
        """
        Sets or updates the remedy associated with the prohibition.

        :param remedy: Action instance representing the remedy.
        """
        self.remedy = remedy

    def clear_remedy(self):
        """
        Removes the remedy associated with the prohibition.
        """
        self.remedy = None



class Duty(Rule):
    def __init__(self, target, action, assigner, assignee, consequence=None, actions=None, constraints=None):
        """
        Initializes a Duty instance, extending the Rule class with additional properties
        for actions, constraints, and a potential consequence.

        :param target: The object or entity the duty applies to.
        :param action: The primary action associated with the duty.
        :param assigner: The entity that imposes the duty.
        :param assignee: The entity obligated to fulfill the duty.
        :param consequence: Optional; another Duty (or Rule) instance representing the consequence of not fulfilling the duty.
        :param actions: Optional; a list of additional Action objects associated with the duty.
        :param constraints: Optional; a list of Constraint objects specifying conditions under which the duty applies.
        """
        super().__init__(target, action, assigner, assignee)
        self.actions = actions if actions is not None else []
        self.constraints = constraints if constraints is not None else []
        self.consequence = consequence


    def add_action(self, action):
        """
        Adds an additional action to the duty.

        :param action: Action object to be added.
        """
        self.actions.append(action)
    def remove_action(self, action):
        """
        Remove action from the duty.

        :param action: Action object to be removed.
        """
        if action in self.actions:
            self.actions.remove(action)

    def add_constraint(self, constraint):
        """
        Adds a constraint to the duty.

        :param constraint: Constraint object to be added.
        """
        self.constraints.append(constraint)

    def set_consequence(self, consequence):
        """
        Sets the consequence of the duty.

        :param consequence: Duty object representing the consequence.
        """
        self.consequence = consequence

    def is_fulfilled(self):
        """
        Checks if the duty is fulfilled.

        :return: True if the duty is fulfilled, False otherwise.
        """
        # Implement your logic to check if the duty is fulfilled here
        # For example, if all constraints are satisfied, consider it as fulfilled
        return all(constraint.is_satisfied() for constraint in self.constraints)

    def clear_actions(self):
        """
        Clears all additional actions associated with the duty.
        """
        self.actions = []

    def clear_constraints(self):
        """
        Clears all constraints associated with the duty.
        """
        self.constraints = []

    def clear_consequence(self):
        """
        Clears the consequence associated with the duty.
        """
        self.consequence = None

