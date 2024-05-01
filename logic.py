import re
from .Parsers import ODRLParser
from .PolicyEnforcement import PolicyEnforcement
from .ontology import *

odrl = ODRLParser()

conjunction = "∧"
disjunction = "∨"
actionTypes = get_actions_from_odrl()
actorTypes = get_actors_from_dpv()
purposeTypes = get_purposes_from_dpv()
def check(i,list):
    for a in list:
        if a["label"].lower() == i.lower() or a["uri"].lower() == i.lower():
            return True
def get(i, list):
    for a in list:
        if a["label"].lower() == i.lower() or a["uri"].lower() == i.lower():
            return a["label"].replace(" ","")

def extract_logic_expressions_from_file(file = "./Examples/consent.odrl"):
    policies = odrl.parse_file(file)
    return extract_logic(policies)
def extract_logic(policies):
    logic_expression = ""
    logic_op = conjunction
    y = 0
    for p in policies:
        results = []
        i = 1
        for proh in p.prohibition:
            id = f"P{i}"
            i += 1
#            id = f"\"{p.uid.split(':')[2]}\""
            query = proh.target
            query_parts = query.split("<--")
            target = query_parts[0].split("(")[1].replace(")","")

            pattern = r'Table\d+\([^)]+\)'
            tables = re.findall(pattern,  query_parts[1])

            logic_expression += f"hasTarget({id}, {target})  {logic_op} "
            for table in tables:
                logic_expression += f"{table.strip()}  {logic_op} "
            if check(proh.assignee, actorTypes):
                function_name = get(proh.assignee, actorTypes)
                logic_expression += f"hasActor ({id},y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                y += 1
            if check(proh.action, actionTypes):
                function_name = get(proh.action, actionTypes)
                logic_expression += f"hasAction ({id},y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                y += 1
            for c in proh.constraint:
                if check(c.rightOperand, purposeTypes):
                    function_name = get(c.rightOperand, purposeTypes)
                    logic_expression += f"hasPurpose ({id},y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                    y += 1
            logic_expression = logic_expression [:-2] + "\n\n"
            results.append({"uid":id,"rule":logic_expression})

    return logic_expression
