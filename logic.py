from Parsers import ODRLParser
from PolicyEnforcement import PolicyEnforcement
from ontology import *

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
    return extract_logic_expressions(policies)
def extract_logic_expressions(policies):
    logic_expression = ""
    logic_op = conjunction
    y = 0
    for p in policies:
        for proh in p.prohibition:
            if check(proh.target, actorTypes):
                function_name = get(proh.target, actorTypes)
                logic_expression += f"hasActor (x,y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                y += 1
            if check(proh.action, actionTypes):
                function_name = get(proh.action, actionTypes)
                logic_expression += f"hasAction (x,y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                y += 1
            for c in proh.constraint:
                if check(c.rightOperand, purposeTypes):
                    function_name = get(c.rightOperand, purposeTypes)
                    logic_expression += f"hasPurpose (x,y{y}) {logic_op} {function_name} (y{y}) {logic_op} "
                    y += 1
    logic_expression = logic_expression [:-2]
    return logic_expression
