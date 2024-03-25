"""
Author: Semih Yumuşak
Date: March 25, 2024
Description: This is a reference implementation of the engine. Logical pipeline is implemented here.

Contributors:

"""


from flask import Flask, request, jsonify
import json
from Constraint import Constraint

app = Flask(__name__)

# Assuming 'policy.odrl' is the file path
file_path = 'policy.odrl'
policy = ""
with open(file_path, 'r') as file:
    policy = json.load(file)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    target = data['target']
    action = data['action']
    context = data['context']
    permission_found = False
    allowed = True
    reason = ""

    for permission in policy.get("permission", []):
        if permission["target"] == target and permission["action"] == action:
            permission_found = True
            if "constraint" in permission:
                constraints = permission["constraint"] if isinstance(permission["constraint"], list) else [permission["constraint"]]
                if not Constraint.evaluate(constraints, context):
                    allowed = False
                    reason = "Constraint not satisfied for permission"
            if allowed:
                for duty in permission.get("duty", []):
                    if not duty.is_fulfilled(duty, context):
                        allowed = False
                        reason = "Duty not met"
                        break

    if allowed:
        for prohibition in policy.get("prohibition", []):
            if prohibition["target"] == target and prohibition["action"] == action:
                if "constraint" in prohibition:
                    constraints = prohibition["constraint"] if isinstance(prohibition["constraint"], list) else [prohibition["constraint"]]
                    if Constraint.evaluate(constraints, context, "or"):  # Assuming OR logic for prohibition constraints
                        allowed = False
                        reason = "Prohibition applies"
                        break

    if not permission_found:
        allowed = False
        reason = "No applicable permission found"

    return jsonify({"allowed": allowed, "reason": reason})

if __name__ == '__main__':
    app.run(debug=True)
