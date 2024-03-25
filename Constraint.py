"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is the constraint package which has logical and arithmetic constraint implementations.

Contributors:

"""

class Constraint:
    def __init__(self):
        pass
    def evaluate(self):
        pass

class ArithmeticConstraint(Constraint):
    def __init__(self, operator, leftOperand=None, reference=None):
        self.operator = operator
        self.leftOperand = leftOperand  # The specific operand that needs an exact match to proceed
        self.reference = reference

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
        else:
            return False

class LogicalConstraint(Constraint):
    def __init__(self, operator):
        self.operator = operator

    def check_constraint(self, value):
        if self.operator == 'or':
            return any(constraint.check_constraint(None, value) for constraint in self.constraints)
        elif self.operator == 'xone':
            return sum(constraint.check_constraint(None, value) for constraint in self.constraints) == 1
        elif self.operator == 'and':
            return all(constraint.check_constraint(None, value) for constraint in self.constraints)
        elif self.operator == 'andSequence':
            results = [constraint.check_constraint(None, value) for constraint in self.constraints]
            return all(results) and results == sorted(results, reverse=True)
        else:
            return False