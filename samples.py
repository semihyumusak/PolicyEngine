from Constraint import ArithmeticConstraint
from Policy import Rule, Permission, Prohibition, Duty, Policy
from Refinables import Action, AssetCollection, PartyCollection

# Creating an Action instance
action1 = Action("read")
constraint1 = ArithmeticConstraint("gteq", leftOperand=10, reference=5)
action1.add_refinement(constraint1)

# Creating AssetCollection instances
assets1 = AssetCollection("Library")
constraint2 = ArithmeticConstraint("eq", reference="book")
assets1.add_refinement(constraint2)

# Creating PartyCollection instances
party1 = PartyCollection("Staff")
constraint3 = ArithmeticConstraint("eq", reference="librarian")
party1.add_refinement(constraint3)

# Creating Rule instances
rule1 = Rule(action=action1, target=assets1, assigner=party1)

# Creating a Permission instance
permission1 = Permission(target=assets1, action=action1, assigner=party1, assignee=party1)

# Creating a Prohibition instance
prohibition1 = Prohibition(target=assets1, action=action1, assigner=party1, assignee=party1)

# Creating a Duty instance
duty1 = Duty(target=assets1, action=action1, assigner=party1, assignee=party1)

# Creating a Policy instance
policy1 = Policy(uid="policy1")
policy1.addRule(rule1)

# Adding a constraint to the Duty instance
constraint4 = ArithmeticConstraint("lt", reference=100)
duty1.add_constraint(constraint4)

# Removing a constraint from the Duty instance
duty1.remove_constraint(constraint4)

# Activating a Rule
rule1.activate()

# Deactivating a Rule
rule1.deactivate()

# Checking if a Rule is active
is_active = rule1.is_active()

# Setting duty for Permission
duty_action = Action("notify")
permission1.set_duty(duty_action)

# Clearing duty for Permission
permission1.clear_duty()

# Checking if a Prohibition is violated
is_violated = prohibition1.is_violated()

# Setting remedy for Prohibition
remedy_action = Action("warn")
prohibition1.set_remedy(remedy_action)

# Clearing remedy for Prohibition
prohibition1.clear_remedy()

# Adding an implied action to an Action
implied_action = Action("log")
action1.add_implied_action(implied_action)
