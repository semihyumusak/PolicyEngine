from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Assuming 'policy.odrl' is the file path
file_path = 'policy.odrl'
policy = ""
# Read the file
with open(file_path, 'r') as file:
    policy = json.load(file)


# Utility function to check if a constraint is satisfied
def is_constraint_satisfied(constraint, context):
    if constraint["operator"] == "lt" and context[constraint["leftOperand"]] < constraint["rightOperand"]:
        return True
    elif constraint["operator"] == "gte" and context[constraint["leftOperand"]] >= constraint["rightOperand"]:
        return True
    return False

# Function to check if a duty is met
def is_duty_met(duty, context):
    if "constraint" in duty and not is_constraint_satisfied(duty["constraint"], context):
        return False
    return True

# Endpoint to evaluate an action against the policy
@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    target = data['target']
    action = data['action']
    context = data['context']
    allow = {"allowed": True}
    permission_found = False
    # Check permissions
    for permission in policy.get("permission", []):
        if permission["target"] == target and permission["action"] == action:
            # Check constraints
            permission_found = True
            if "constraint" in permission and not is_constraint_satisfied(permission["constraint"], context):
                allow = {"allowed": False, "reason": "Constraint not satisfied for permission"}
            # Check duties
            for duty in permission.get("duty", []):
                if not is_duty_met(duty, context) and allow["allowed"]:
                    allow = {"allowed": False, "reason": "Duty not met"}

    if allow["allowed"]:
        # Check prohibitions
        for prohibition in policy.get("prohibition", []):
            if prohibition["target"] == target and prohibition["action"] == action:
                # Check constraints
                if "constraint" in prohibition and not is_constraint_satisfied(prohibition["constraint"], context):
                    allow = {"allowed": True}  # If constraint not met, prohibition does not apply
                else:
                    return {"allowed": False, "reason": "Prohibition applies"}

    if not permission_found:
        return {"allowed": False, "reason": "No applicable permission found"}
    else:
        return jsonify(allow)

if __name__ == '__main__':
    app.run(debug=True)
