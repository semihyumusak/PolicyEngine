from pyDatalog import pyDatalog.parser

# Define the Datalog statements
statement1 = "Permission(Pe1) :- hasTarget(Pe1, x0), covid19Stats(x0), hasActor(Pe1, x1), Recipient(x1), hasAction(Pe1, x2), DerivativeWorks(x2), hasPurpose(Pe1, x3), ResearchAndDevelopment(x3)"
statement2 = "Permission(Pe1) :- hasTarget(Pe1, x0), hasActor(Pe1, x1), Recipient(x1), hasAction(Pe1, x2), DerivativeWorks(x2), hasPurpose(Pe1, x3), ResearchAndDevelopment(x3)"

# Parse the Datalog statements
query1 = parse_query(statement1)
query2 = parse_query(statement2)

# Check for conflicting points
conflicts = []
for atom1 in query1.body:
    if atom1 not in query2.body:
        conflicts.append(atom1)

for atom2 in query2.body:
    if atom2 not in query1.body:
        conflicts.append(atom2)

if conflicts:
    print("Conflicting points:")
    for conflict in conflicts:
        print(conflict)
else:
    print("No conflicting points found.")
