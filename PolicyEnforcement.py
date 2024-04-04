from typing import List, Union
from datetime import datetime

from Policy import Policy, Permission, Prohibition, Obligation, Duty


class PolicyEnforcement:
    def __init__(self, policies: List[Policy]):
        self.policies = policies

    def check_permission(self, action: str, target: str, assigner: str, assignee: str = None) -> bool:
        """
        Checks if the given action is permitted according to any of the policies.

        :param action: The action to be checked.
        :param target: The target of the action.
        :param assigner: The entity attempting the action.
        :param assignee: Optional; the entity to whom the action is assigned.
        :return: True if the action is permitted, False otherwise.
        """
        for policy in self.policies:
            for permission in policy.permission:
                if permission.target == target and permission.assigner == assigner:
                    if assignee is None or permission.assignee == assignee:
                        if any(act.name == action for act in permission.action):
                            return True
        return False

    def check_prohibition(self, action: str, target: str, assigner: str, assignee: str = None) -> bool:
        """
        Checks if the given action is prohibited according to any of the policies.

        :param action: The action to be checked.
        :param target: The target of the action.
        :param assigner: The entity attempting the action.
        :param assignee: Optional; the entity to whom the action is assigned.
        :return: True if the action is prohibited, False otherwise.
        """

        for policy in self.policies:
            for prohibition in policy.prohibition:
                if prohibition.target == target and prohibition.assigner == assigner:
                    if assignee is None or prohibition.assignee == assignee:
                        if any(act.name == action for act in prohibition.action):
                            return True
        return False

    def enforce_policy(self, action: str, target: str, assigner: str, assignee: str = None) -> Union[str, None]:
        """
        Enforces the policies by checking if the given action is permitted, prohibited, or neither.

        :param action: The action to be checked.
        :param target: The target of the action.
        :param assigner: The entity attempting the action.
        :param assignee: Optional; the entity to whom the action is assigned.
        :return: "Permitted" if the action is permitted, "Prohibited" if the action is prohibited, None otherwise.
        """
        if self.check_permission(action, target, assigner, assignee):
            return "Permitted"
        elif self.check_prohibition(action, target, assigner, assignee):
            return "Prohibited"
        else:
            return None


# Example usage:
if __name__ == "__main__":
    # Example policies
    policy1 = Policy(uid="1", type="Example", permission=[Permission(target="resource", action=[Action(name="read")],
                                                                     assigner="user", assignee="admin")])
    policy2 = Policy(uid="2", type="Example", prohibition=[Prohibition(target="resource", action=[Action(name="delete")],
                                                                        assigner="user", assignee="admin")])
    policies = [policy1, policy2]

    # Creating an instance of PolicyEnforcement
    policy_enforcement = PolicyEnforcement(policies)

    # Checking permissions
    print(policy_enforcement.enforce_policy("read", "resource", "user", "admin"))  # Output: Permitted
    print(policy_enforcement.enforce_policy("write", "resource", "user", "admin"))  # Output: None

    # Checking prohibitions
    print(policy_enforcement.enforce_policy("delete", "resource", "user", "admin"))  # Output: Prohibited
    print(policy_enforcement.enforce_policy("update", "resource", "user", "admin"))  # Output: None
