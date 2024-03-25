"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is file containing Policy and rule classes.

Contributors:

"""


from Refinables.Action import Action
from Refinables.AssetCollection import AssetCollection
from Constraint import Constraint
from Refinables.PartyCollection import PartyCollection

class Rule:
    def __init__(self, target:AssetCollection, action: Action, assigner, assignee: PartyCollection):
        self.target = target
        self.action = action
        self.assigner = assigner
        self.assignee = assignee
        self.state = "Inactive"  # Default state is Inactive

    def activate(self):
        self.state = "Active"

    def deactivate(self):
        self.state = "Inactive"

    def is_active(self):
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
        pass




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
        """
        self.actions.append(action)

    def add_constraint(self, constraint):
        """
        Adds a constraint to the duty.
        """
        self.constraints.append(constraint)

    def set_consequence(self, consequence):
        """
        Sets the consequence of the duty.
        """
        self.consequence = consequence
    def is_fulfilled(self):
        pass

