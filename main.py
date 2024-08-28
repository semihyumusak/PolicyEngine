"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is a reference implementation of the engine. Logical pipeline is implemented here.

Contributors:

"""
import json

from flask import Flask, request, jsonify, render_template
from Constraint import Constraint
from Parsers import ODRLParser
from PolicyEnforcement import PolicyEnforcement
from ontology import *
from logic import extract_logic_expressions as logic_expr
app = Flask(__name__)

# Assuming 'policy.odrl' is the file path
file_path = "./examples/policy.odrl"

odrl = ODRLParser()
policies = odrl.parse_file(file_path)

@app.route('/', methods=['GET'])
def index():
    # Read the content of the HTML file
    with open('html/logic.html', 'r') as file:
        html_content = file.read()
    return html_content
@app.route('/evaluate_odrl', methods=['POST'])
def evaluate_odrl():
    data = request.json
    incoming_request = odrl.parse(data)

    for p in policies:
        pe = PolicyEnforcement(p)
        return pe.enforce_policy(incoming_request)

    pe = PolicyEnforcement(policies)
    for r in incoming_request:
        for perm in r.permission:
            print(pe.check_permission(perm))

conjunction = "∧"
disjunction = "∨"
@app.route('/extract_logic_expressions', methods=['POST'])
def extract_logic_expressions():

    incoming_request = odrl.parse_list(request.json)
    print (incoming_request)
    result = logic_expr(incoming_request)
    return result


@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    target = data['target']
    action = data['action']
    context = data['context']
    permission_found = False
    allowed = True
    reason = ""

    for permission in policy.permission:
        if permission.target == target and permission.action == action:
            permission_found = True
            if len(permission.constraint)>0:
                constraints = permission.constraint if isinstance(permission.constraint, list) else [permission.constraint]
                if not Constraint.evaluate(constraints, context):
                    allowed = False
                    reason = "Constraint not satisfied for permission"
            if allowed:
                for duty in permission.duty:
                    if not duty.is_fulfilled(duty, context):
                        allowed = False
                        reason = "Duty not met"
                        break

    if allowed:
        for prohibition in policy.prohibition:
            if prohibition.target == target and prohibition.action == action:
                if len(prohibition.constraint)>0:
                    constraints = prohibition.constraint if isinstance(prohibition.constraint, list) else [prohibition.constraint]
                    # TODO: check constraints
                    if Constraint.evaluate(constraints, context, "or"):  # Assuming OR logic for prohibition constraints
                        allowed = False
                        reason = "Prohibition applies"
                        break

    if not permission_found:
        allowed = False
        reason = "No applicable permission found"

    return jsonify({"allowed": allowed, "reason": reason})

@app.route('/get_properties_from_properties_file', methods=['GET'])
def get_properties_from_properties_file(request):
    try:
        uri = request.GET["uri"]
        fields = get_properties_of_a_class(uri,"./media/default_ontology/AdditionalProperties.ttl")
        res = 200
        # res = _fetch_valid_status(odrl)
        return jsonify({"fields":fields})
    except BaseException as b:
            return b

@app.route('/convert_to_odrl', methods=['GET'])
def convert_to_odrl(request):
    if request.method == "POST":
        try:
            response = json.loads(request.body)
            odrl = convert_list_to_odrl_jsonld_no_user(response)
            res = 200
            # res = _fetch_valid_status(odrl)
            return jsonify(odrl)
            #return JsonResponse({"Policy": odrl, "response": res})
        except BaseException as b:
            return jsonify({})
            #return b
@app.route('/create_rule', methods=['GET'])
def create_rule_dataset_no_user():
    rules = get_rules_from_odrl("./media/default_ontology/ODRL22.rdf")
    actors = get_actors_from_dpv("./media/default_ontology/dpv.rdf")
    actions = get_actions_from_odrl("./media/default_ontology/ODRL22.rdf")
    targets = get_dataset_titles_and_uris("./media/default_ontology/Datasets.ttl")
    constraints = get_constraints_types_from_odrl("./media/default_ontology/ODRL22.rdf")
    purposes = get_purposes_from_dpv("./media/default_ontology/dpv.rdf")
    operators = get_operators_from_odrl("./media/default_ontology/ODRL22.rdf")

    rules.append({"label": "Obligation", "uri": "http://www.w3.org/ns/odrl/2/Obligation"})

    context = {
        "rules": rules,
        "actors": actors,
        "actions": actions,
        "targets": targets,
        "constraints": constraints,
        "operators": operators,
        "purposes": purposes,
    }
    return render_template("./html/policy.html", **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port="8080")
