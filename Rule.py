from Action import Action
from AssetCollection import AssetCollection
from Constraint import Constraint
from PartyCollection import PartyCollection


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

    def __str__(self):
        return (f"Rule(Target: {self.target}, Action: {self.action}, "
                f"Assigner: {self.assigner}, Assignee: {self.assignee}, "
                f"State: {self.state})")

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

    def __str__(self):
        base_str = super().__str__()
        duty_str = f", Duty: {str(self.duty)}" if self.duty else ""
        return f"{base_str}{duty_str}"


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
    def __str__(self):
        base_str = super().__str__()
        remedy_str = f", Remedy: {str(self.remedy)}" if self.remedy else ""
        return f"{base_str}{remedy_str}"


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

    def __str__(self):
        base_str = super().__str__()
        actions_str = ", ".join(str(action) for action in self.actions)
        constraints_str = ", ".join(str(constraint) for constraint in self.constraints)
        consequence_str = f"Consequence: [{str(self.consequence)}]" if self.consequence else "No consequence"
        return f"{base_str}, Additional Actions: [{actions_str}], Constraints: [{constraints_str}], {consequence_str}"


if __name__ == '__main__':
    # Example usage:
    rule1 = Rule(target="Document Approval", action="Approve", assigner="Manager", assignee="Employee")
    print(rule1)

    rule1.activate()
    print("Is rule1 active?", rule1.is_active())

    rule1.deactivate()
    print("Is rule1 active?", rule1.is_active())

    # Example usage:
    # Assuming Action and Constraint classes are defined as previously discussed

    # Simple duty example
    simple_duty = Action("Notify")

    # Complex duty example with refinements
    constraint1 = Constraint('eq', leftOperand='day', reference="Friday")
    complex_duty = Action("Report", refinements=[constraint1])

    # Creating Permission instances
    simple_permission = Permission(target="Document", action="Edit", assigner="Manager", assignee="Employee",
                                   duty=simple_duty)
    print(simple_permission)

    complex_permission = Permission(target="System", action="Access", assigner="Admin", assignee="User",
                                    duty=complex_duty)
    print(complex_permission)


    # Example usage:
    # Assuming the Action, Constraint, and Rule classes are defined as previously discussed

    # Define a primary duty
    primary_duty = Duty(target="Report Submission", action="Submit", assigner="Manager", assignee="Employee")

    # Define a consequence duty for failing to fulfill the primary duty
    consequence_duty = Duty(target="Late Report", action="Notify", assigner="System", assignee="Manager")

    # Add actions and constraints to the primary duty
    action1 = Action("Write")
    constraint1 = Constraint('lt', leftOperand='deadline', reference=24)
    primary_duty.add_action(action1)
    primary_duty.add_constraint(constraint1)

    # Set the consequence of the primary duty
    primary_duty.set_consequence(consequence_duty)

    print(primary_duty)

