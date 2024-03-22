from Constraint import Constraint


class Action:
    def __init__(self, value, refinements=None):
        """
        Initializes an Action instance.

        :param value: The main action, can be a string or an object representing the action.
        :param refinements: Optional list of Constraint objects that refine the conditions of the action.
        """
        self.value = value
        self.refinements = refinements if refinements is not None else []

    def add_refinement(self, refinement):
        """
        Adds a refinement (constraint) to the action.

        :param refinement: A Constraint object to be added as a refinement.
        """
        self.refinements.append(refinement)

    def __str__(self):
        value_str = str(self.value)
        refinements_str = ", ".join(str(refinement) for refinement in self.refinements)
        return f"Action(Value: {value_str}, Refinements: [{refinements_str}])"

if __name__ == '__main__':
    # Example usage:
    # Assuming the Constraint class is defined as previously discussed

    # Simple action example
    simple_action = Action("Read")
    print(simple_action)

    # Complex action example with refinements
    constraint1 = Constraint('gt', leftOperand='time', reference=10)
    constraint2 = Constraint('lt', leftOperand='time', reference=20)
    complex_action = Action("Play", refinements=[constraint1, constraint2])
    print(complex_action)

    # Adding a new refinement to the complex action
    constraint3 = Constraint('eq', leftOperand='location', reference="Park")
    complex_action.add_refinement(constraint3)
    print(complex_action)
