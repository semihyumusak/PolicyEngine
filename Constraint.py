class Constraint:
    def __init__(self, operator, leftOperand=None, reference=None, constraints=None):
        self.operator = operator
        self.leftOperand = leftOperand  # The specific operand that needs an exact match to proceed
        self.reference = reference
        self.constraints = constraints or []

    def check_constraint(self, leftOperandValue, value):
        # First, check if the leftOperand matches exactly
        if self.leftOperand is not None and self.leftOperand != leftOperandValue:
            return False  # The leftOperand does not match; constraint check does not proceed

        # Proceed with the constraint checks
        if self.operator == 'eq':
            return value == self.reference
        elif self.operator == 'gt':
            return value > self.reference
        elif self.operator == 'gteq':
            return value >= self.reference
        elif self.operator == 'lt':
            return value < self.reference
        elif self.operator == 'lteq':
            return value <= self.reference
        elif self.operator == 'neq':
            return value != self.reference
        elif self.operator in ['or', 'xone', 'and', 'andSequence']:
            results = [constraint.check_constraint(leftOperandValue, value) for constraint in self.constraints]
            if self.operator == 'or':
                return any(results)
            elif self.operator == 'xone':
                return sum(results) == 1
            elif self.operator == 'and':
                return all(results)
            elif self.operator == 'andSequence':
                return all(results) and results == sorted(results, reverse=True)
        else:
            return False

if __name__ == '__main__':
    # Example usage:
    # Define constraints with a specific leftOperand requirement
    constraint1 = Constraint('gt', leftOperand='temperature', reference=10)
    constraint2 = Constraint('lt', leftOperand='temperature', reference=20)
    logical_constraint = Constraint('and', constraints=[constraint1, constraint2])

    print(logical_constraint.check_constraint('temperature', 15))  # Should return True
    print(logical_constraint.check_constraint('humidity', 15))     # Should return False due to leftOperand mismatch
