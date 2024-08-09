import json

import rdflib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Union
from motor.motor_asyncio import AsyncIOMotorClient
from rdflib import Graph, BNode
from rdflib.namespace import Namespace
from rdflib.plugins.sparql import prepareQuery
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from typing import List, Dict, Any

from Parsers import ODRLParser
from Translators import LogicTranslator


class ODRLData(BaseModel):
    key: str
    value: Any  # Adjust according to the actual structure of your data


import data_helper

app = FastAPI()
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Define the namespaces
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")
DPV = Namespace("https://w3id.org/dpv/dpv-owl#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")


# MongoDB connection setup
user = "semih"
password = "a8Spt66DKqGh2V0T"
host = "cluster0.btnpvyy.mongodb.net"
MONGO_DETAILS = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client['policy_database']
collection_data = db['data_policies']
collection_script = db['script_policies']

# Define the SPARQL query to find matching nodes
sparql_query = """
PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?action ?assignee ?target_source ?purpose 
WHERE {
  ?node odrl:action ?action ;
        odrl:assignee ?assignee ;
        odrl:target ?target ;
        odrl:constraint ?constraint .
        ?constraint odrl:leftOperand odrl:purpose ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand ?purpose .
        ?target odrl:source ?target_source.
}
"""

example_permission_policy_2 = {
        "permission": [
            {
                "action": "http://www.w3.org/ns/odrl/2/appendTo",
                "assignee": "https://w3id.org/dpv/dpv-owl#Citizen",
                "target": {
                    "source": "http://example.org/datasets/climateChangeData",
                    "refinement": [
                        {
                            "leftOperand": "http://example.org/datasets/title",
                            "operator": "http://www.w3.org/ns/odrl/2/eq",
                            "rightOperand": "6"
                        }
                    ]
                },
                "constraint": [
                    {
                        "leftOperand": "http://www.w3.org/ns/odrl/2/purpose",
                        "operator": "http://www.w3.org/ns/odrl/2/eq",
                        "rightOperand": "https://w3id.org/dpv/dpv-owl#Personalisation"
                    }
                ]
            }
        ],
        "uid": "http://example.org/policy-79f7e6ba-daff-4919-940f-a1ad1344a97b",
        "@context": "http://www.w3.org/ns/odrl.jsonld",
        "@type": "http://www.w3.org/ns/odrl/2/Policy"
    }

example_permission_policy =  {
    "permission": [
        {
            "action": "http://www.w3.org/ns/odrl/2/appendTo",
            "assignee": "https://w3id.org/dpv/dpv-owl#Citizen",
            "target": {
                "source": "http://example.org/datasets/climateChangeData",
                "refinement": [
                    {
                        "leftOperand": "http://example.org/datasets/title",
                        "operator": "http://www.w3.org/ns/odrl/2/eq",
                        "rightOperand": "6"
                    }
                ]
            },
            "constraint": [
                {
                    "leftOperand": "purpose",
                    "operator": "http://www.w3.org/ns/odrl/2/eq",
                    "rightOperand": "https://w3id.org/dpv/dpv-owl#Personalisation"
                }
            ]
        }
    ],
    "uid": "http://example.org/policy-79f7e6ba-daff-4919-940f-a1ad1344a97b",
    "@context": "http://www.w3.org/ns/odrl.jsonld",
    "@type": "http://www.w3.org/ns/odrl/2/Policy"
}

example_prohibition_policy_2 = {
    "prohibition": [
        {
            "action": "http://www.w3.org/ns/odrl/2/appendTo",
            "assignee": "https://w3id.org/dpv/dpv-owl#LegalEntity",
            "target": {
                "source": "http://example.org/datasets/climateChangeData",
                "refinement": [
                    {
                        "leftOperand": "http://example.org/datasets/title",
                        "operator": "http://www.w3.org/ns/odrl/2/eq",
                        "rightOperand": "6"
                    }
                ]
            },
            "constraint": [
                {
                    "leftOperand": "purpose",
                    "operator": "http://www.w3.org/ns/odrl/2/eq",
                    "rightOperand": "https://w3id.org/dpv/dpv-owl#Personalisation"
                }
            ]
        }
    ],
    "uid": "http://example.org/policy-79f7e6ba-daff-4919-940f-a1ad1344a97a",
    "@context": "http://www.w3.org/ns/odrl.jsonld",
    "@type": "http://www.w3.org/ns/odrl/2/Policy"
}

example_prohibition_policy = {
    "prohibition": [
        {
            "action": "http://www.w3.org/ns/odrl/2/appendTo",
            "assignee": "https://w3id.org/dpv/dpv-owl#Citizen",
            "target": {
                "source": "http://example.org/datasets/climateChangeData",
                "refinement": [
                    {
                        "leftOperand": "http://example.org/datasets/title",
                        "operator": "http://www.w3.org/ns/odrl/2/eq",
                        "rightOperand": "6"
                    }
                ]
            },
            "constraint": [
                {
                    "leftOperand": "purpose",
                    "operator": "http://www.w3.org/ns/odrl/2/eq",
                    "rightOperand": "https://w3id.org/dpv/dpv-owl#Personalisation"
                }
            ]
        }
    ],
    "uid": "http://example.org/policy-79f7e6ba-daff-4919-940f-a1ad1344a97a",
    "@context": "http://www.w3.org/ns/odrl.jsonld",
    "@type": "http://www.w3.org/ns/odrl/2/Policy"
}

class ScriptPolicy(BaseModel):
    odrl_policy: Dict = Field(
        ...,
        example=example_permission_policy_2
    )
class DataPolicy(BaseModel):
    odrl_policy: Dict = Field(
        ...,
        example=example_prohibition_policy_2
    )

class RequestPolicy(BaseModel):
    dataset_id: str = Field(
        ...,
        example="example_dataset_id"
    )
    script_id: str = Field(
        ...,
        example="example_script_id"
    )

class ConflictReport(BaseModel):
    conflict_details: Union[Dict, str] = Field(..., example="No conflicts")

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# Endpoint: /get_policy/{dataset_id}
@app.get("/get_data_provider_policy/{dataset_id}", response_model=DataPolicy)
async def get_data_provider_policy(dataset_id: str):
    """
    Retrieves the ODRL policy for a specific dataset ID from the policies database.

    Parameters:
    - dataset_id: Path parameter specifying the ID of the dataset for which the policy needs to be retrieved.

    Returns:
    - Success (200 OK): Returns a JSON object containing the ODRL policy for the specified dataset_id: {"odrl_policy": policies[dataset_id]}

    - Failure (404 Not Found): If the specified dataset_id is not found in the policies database.
      Returns an HTTP 404 error with details: "Policy not found"

    Example Usage:
    ```
    GET /get_policy/example_dataset HTTP/1.1
    ```
    Replace example_dataset with the actual dataset ID to retrieve its policy.
    """
    policy = await collection_data.find_one({"dataset_id": dataset_id})
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"odrl_policy": policy["odrl_policy"]}

# Endpoint: /set_policy/{dataset_id}
@app.post("/set_data_provider_policy/{dataset_id}", status_code=201)
async def set_data_provider_policy(dataset_id: str, policy: DataPolicy):
    """
    Sets or updates the ODRL policy for a specific dataset ID in the policies database.

    Parameters:
    - dataset_id: Path parameter specifying the ID of the dataset for which the policy is to be set.
    - policy: Request body containing the new ODRL policy to be set for the dataset.

    Returns:
    - Success (201 Created): Returns a JSON object with a success message indicating the policy was set successfully: {"message": "Policy set successfully"}

    Example Usage:
    ```
    POST /set_policy/example_dataset HTTP/1.1
    Content-Type: application/json

    {
      "odrl_policy": {...}
    }
    ```
    Replace example_dataset with the actual dataset ID and provide the appropriate odrl_policy details in the request body.
    """
    await collection_data.update_one(
        {"dataset_id": dataset_id},
        {"$set": {"odrl_policy": policy.odrl_policy}},
        upsert=True
    )
    return {"message": "Policy set successfully"}

# Endpoint: /remove_policy/{dataset_id}
@app.delete("/remove_data_provider_policy/{dataset_id}")
async def remove_data_provider_policy(dataset_id: str):
    """
    Removes the ODRL policy for a specific dataset ID from the policies database.

    Parameters:
    - dataset_id: Path parameter specifying the ID of the dataset for which the policy is to be removed.

    Returns:
    - Success (200 OK): Returns a JSON object with a success message indicating the policy was removed successfully: {"message": "Policy removed successfully"}

    - Failure (404 Not Found): If the specified dataset_id is not found in the policies database.
      Returns an HTTP 404 error with details: "Policy not found"

    Example Usage:
    ```
    DELETE /remove_policy/example_dataset HTTP/1.1
    ```
    Replace example_dataset with the actual dataset ID to remove its policy.
    """
    result = await collection_data.delete_one({"dataset_id": dataset_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy removed successfully"}

@app.get("/get_data_consumer_policy/{script_id}", response_model=ScriptPolicy)
async def get_data_consumer_policy(script_id: str):
    """
    Retrieves the ODRL policy for a specific script ID from the policies database.

    Parameters:
    - script_id: Path parameter specifying the ID of the script for which the policy needs to be retrieved.

    Returns:
    - Success (200 OK): Returns a JSON object containing the ODRL policy for the specified script_id: {"odrl_policy": policies[script_id]}

    - Failure (404 Not Found): If the specified script_id is not found in the policies database.
      Returns an HTTP 404 error with details: "Policy not found"

    Example Usage:
    ```
    GET /get_policy/example_script HTTP/1.1
    ```
    Replace example_script with the actual script ID to retrieve its policy.
    """
    policy = await collection_script.find_one({"script_id": script_id})
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"odrl_policy": policy["odrl_policy"]}

@app.post("/set_data_consumer_policy/{script_id}", status_code=201)
async def set_data_consumer_policy(script_id: str, policy: ScriptPolicy):
    """
    Sets or updates the ODRL policy for a specific script ID in the policies database.

    Parameters:
    - script_id: Path parameter specifying the ID of the script for which the policy is to be set.
    - policy: Request body containing the new ODRL policy to be set for the script.

    Returns:
    - Success (201 Created): Returns a JSON object with a success message indicating the policy was set successfully: {"message": "Policy set successfully"}

    Example Usage:
    ```
    POST /set_policy/example_script HTTP/1.1
    Content-Type: application/json

    {
      "odrl_policy": {...}
    }
    ```
    Replace example_script with the actual script ID and provide the appropriate odrl_policy details in the request body.
    """
    await collection_script.update_one(
        {"script_id": script_id},
        {"$set": {"odrl_policy": policy.odrl_policy}},
        upsert=True
    )
    return {"message": "Policy set successfully"}

@app.delete("/remove_data_consumer_policy/{script_id}")
async def remove_data_consumer_policy(script_id: str):
    """
    Removes the ODRL policy for a specific script ID from the policies database.

    Parameters:
    - script_id: Path parameter specifying the ID of the script for which the policy is to be removed.

    Returns:
    - Success (200 OK): Returns a JSON object with a success message indicating the policy was removed successfully: {"message": "Policy removed successfully"}

    - Failure (404 Not Found): If the specified script_id is not found in the policies database.
      Returns an HTTP 404 error with details: "Policy not found"

    Example Usage:
    ```
    DELETE /remove_policy/example_script HTTP/1.1
    ```
    Replace example_script with the actual script ID to remove its policy.
    """
    result = await collection_script.delete_one({"script_id": script_id})
    if result["deleted_count"] == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": "Policy removed successfully"}


@app.post("/compare_policies", response_model=ConflictReport)
async def compare_policies(request_policy: RequestPolicy):
    """
    Validates a policy of a script against existing policies for a dataset using ODRL (Open Digital Rights Language).

    Parameters:
    - request_policy: Request body containing the existing dataset_id and script_id
    to validate a script data access request policy against a data provider access policy.

    Returns:
    - Success (200 OK): Access granted if no conflicts are found between the request policy and existing dataset policies.
      Returns a JSON object with a success message: {"message": "Access granted"}

    - Failure (404 Not Found): If the specified dataset_id is not found in the policies database.
      Returns an HTTP 404 error with details: "Policy not found"

    - Conflict (200 OK with ConflictReport): If the request policy conflicts with an existing policy for the dataset.
      Returns a JSON object with conflict details: {"conflict_details": "Request policy conflicts with existing policy"}
    """
    policy_data = await collection_data.find_one({"dataset_id": request_policy.dataset_id})
    policy_script = await collection_script.find_one({"script_id": request_policy.script_id})
    if policy_data is None:
        raise HTTPException(status_code=404, detail="Data policy not found")
    if policy_script is None:
        raise HTTPException(status_code=404, detail="Script policy not found")

    existing_policy_graph = policy_to_graph(policy_data["odrl_policy"])
    request_policy_graph = policy_to_graph(policy_script["odrl_policy"])

    conflict = check_policy_conflict(existing_policy_graph,request_policy_graph)
    print(conflict)
    # matching_nodes = find_matching_nodes(existing_policy_graph, request_policy_graph)
    # print(matching_nodes)
    if bool(conflict):
        return ConflictReport(conflict_details=conflict)
    return ConflictReport(conflict_details="No conflicts")

def policy_to_graph(policy: Dict) -> Graph:
    graph = Graph()
    graph.parse(data=json.dumps(policy), format="json-ld")
    return graph



def find_matching_nodes(existing_policy: Graph, request_policy: Graph) -> bool:
    """
    Find matching nodes between existing and request policies using SPARQL.

    Parameters:
    - existing_policy: RDF graph representing the existing policy (prohibition).
    - request_policy: RDF graph representing the request policy (permission).

    Returns:
    - Boolean indicating if there are matching nodes between the two policies.
    """


    # Prepare the SPARQL query
    query = prepareQuery(sparql_query, initNs={"odrl": ODRL, "dpv": DPV, "rdfs": RDFS})

    # Execute the query on the existing and request policies
    existing_results = set(existing_policy.query(query))
    request_results = set(request_policy.query(query))

    # Extract non-BNode parts of the results for comparison
    def extract_non_bnode_parts(rdf_set):
        return {node for node in rdf_set if not isinstance(node, rdflib.term.BNode)}

    # Extract non-blank nodes
    existing_non_blank_nodes = extract_non_bnode_parts(existing_results)
    request_non_blank_nodes = extract_non_bnode_parts(request_results)

    existing_non_bnode_parts = extract_non_bnode_parts(existing_results)
    request_non_bnode_parts = extract_non_bnode_parts(request_results)
    # Find matching nodes
    matching_nodes = existing_non_blank_nodes.intersection(request_non_blank_nodes)
    # Debug output
    print("Existing Results (non-BNode parts):", existing_non_bnode_parts)
    print("Request Results (non-BNode parts):", request_non_bnode_parts)
    print("Matching Nodes:", matching_nodes)

    # Return whether there are any matching nodes
    if bool(matching_nodes):
        conflicts = []
        for matching_node in matching_nodes:
            conflicts.append({
                'action': matching_node[0],
                'assignee': matching_node[1],
                'target_source': matching_node[2],
                'purpose': matching_node[3]
            })
        return {"conflicts" : matching_nodes}
    else:
        return

def find_matching_nodes2(existing_policy: Graph, request_policy: Graph) -> bool:
    """
    Find matching nodes between existing and request policies using SPARQL.

    Parameters:
    - existing_policy: RDF graph representing the existing policy (prohibition).
    - request_policy: RDF graph representing the request policy (permission).

    Returns:
    - Boolean indicating if there are matching nodes between the two policies.
    """
    # Define the SPARQL query to find matching nodes
    sparql_query = """
    PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
    PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?action ?assignee ?target ?constraint 
    WHERE {
      {
        ?node odrl:action ?action ;
              odrl:assignee ?assignee ;
              odrl:target ?target ;
              odrl:constraint ?constraint .
      }
     
    }
    """

    # Prepare the SPARQL query
    query = prepareQuery(sparql_query, initNs={"odrl": ODRL, "dpv": DPV, "rdfs": RDFS})

    # Execute the query on the existing and request policies
    existing_results = set(existing_policy.query(query))
    request_results = set(request_policy.query(query))

    # Find matching nodes
    matching_nodes = existing_results.intersection(request_results)

    return matching_nodes

def check_policy_conflict(existing_policy: Graph, request_policy: Graph) -> Union[None, str]:
    """
    Checks for conflicts between existing and request policies using SPARQL.

    Parameters:
    - existing_policy: RDF graph representing the existing policy (prohibition).
    - request_policy: RDF graph representing the request policy (permission).

    Returns:
    - Conflict message if conflicts are found, None otherwise.
    """
    # Define the SPARQL query
    sparql_query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
        PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?policy ?conflictingPolicy
            WHERE {
                ?policy a odrl:Policy ;
                        odrl:permission ?permission .
                ?permission odrl:action ?action ;
                            odrl:target ?target ;
                            odrl:constraint ?constraint ;
                            odrl:assignee ?assignee.
            
                ?conflictingPolicy a odrl:Policy ;
                                   odrl:prohibition ?prohibition .
                                   
                ?prohibition odrl:action ?prohibitionAction ;
                             odrl:target ?prohibitionTarget ;
                             odrl:constraint ?prohibitionConstraint ;
                             odrl:assignee ?prohibitionAssignee .
            
                # Hierarchical reasoning for action (including transitive subclasses)
                ?action (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionAction .
                # Hierarchical reasoning for action (including transitive subclasses)
                ?assignee (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionAssignee .
                # Hierarchical reasoning for target (including transitive subclasses)
                ?target (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionTarget .
            
                OPTIONAL {
                    ?constraint odrl:leftOperand ?constraintLeftOperand ;
                                odrl:operator ?constraintOperator ;
                                odrl:rightOperand ?constraintRightOperand .
                    ?prohibitionConstraint odrl:leftOperand ?prohibitionLeftOperand ;
                                           odrl:operator ?prohibitionOperator ;
                                           odrl:rightOperand ?prohibitionRightOperand .
            
                    # Hierarchical reasoning for constraints (including transitive subclasses)
                    ?constraintLeftOperand (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionLeftOperand .
                    ?constraintOperator (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionOperator .
                    ?constraintRightOperand (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionRightOperand .
                }
            
                FILTER (!BOUND(?constraint) || (!BOUND(?constraintLeftOperand) && !BOUND(?prohibitionLeftOperand)) ||
                        (?constraintLeftOperand = ?prohibitionLeftOperand &&
                         ?constraintOperator = ?prohibitionOperator &&
                         ?constraintRightOperand = ?prohibitionRightOperand))
            }

    """

    sparql_query = """
        PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
        PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?policy ?conflictingPolicy
            WHERE {
                ?policy a odrl:Policy ;
                        odrl:permission ?permission .
                ?permission odrl:action ?action ;
                            odrl:target ?target ;
                            odrl:constraint ?constraint ;
                            odrl:assignee ?assignee.
            
                ?conflictingPolicy a odrl:Policy ;
                                   odrl:prohibition ?prohibition .
                                   
                ?prohibition odrl:action ?prohibitionAction ;
                             odrl:target ?prohibitionTarget ;
                             odrl:constraint ?prohibitionConstraint ;
                             odrl:assignee ?prohibitionAssignee .
            
                # Hierarchical reasoning for action (including transitive subclasses)
                ?action (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionAction .
                # Hierarchical reasoning for action (including transitive subclasses)
                ?assignee (rdfs:subClassOf*|^rdfs:subClassOf*) ?prohibitionAssignee .
            }

    """

    # Prepare the SPARQL query
    query = prepareQuery(sparql_query, initNs={"odrl": ODRL, "dpv": DPV, "rdfs": RDFS})
    # Merge the two graphs
    merged_policy = existing_policy + request_policy

    # Execute the query on the merged policy
    results = merged_policy.query(query)
    # Execute the query on the existing and request policies
    # results = existing_policy.query(query)

    # Process results to determine conflicts
    for row in results:
        return f"Conflict detected between policy {row.policy} and conflicting policy {row.conflictingPolicy}"

    return None

def check_policy_conflict_3(existing_policy: Graph, request_policy: Graph) -> Union[None, str]:
    """
    Checks for conflicts between existing and request policies using SPARQL.

    Parameters:
    - existing_policy: RDF graph representing the existing policy (prohibition).
    - request_policy: RDF graph representing the request policy (permission).

    Returns:
    - Conflict message if conflicts are found, None otherwise.
    """
    # Define the SPARQL query
    sparql_query = """
    PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
    PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?policy ?conflictingPolicy
    WHERE {
      ?policy a odrl:Policy ;
              odrl:permission ?permission .
      ?permission odrl:action ?action ;
                  odrl:target ?target ;
                  odrl:constraint ?constraint .

      ?conflictingPolicy a odrl:Policy ;
                         odrl:prohibition ?prohibition .
      ?prohibition odrl:action ?prohibitionAction ;
                   odrl:target ?target ;
                   odrl:constraint ?constraint .

    }
    """

    # Prepare the SPARQL query
    query = prepareQuery(sparql_query, initNs={"odrl": ODRL, "dpv": DPV, "rdfs": RDFS})

    # Execute the query on the existing and request policies
    results = existing_policy.query(query, initBindings={'permission': request_policy})

    # Process results to determine conflicts
    for row in results:
        return f"Conflict detected between policy {row.policy} and conflicting policy {row.conflictingPolicy}"

    return None

def check_policy_conflict_2(existing_policy: Dict, request_policy: Dict) -> Union[None, str]:
    """
    Compares the existing policy (prohibition) and the request policy (permission)
    to determine if there is a conflict. Returns a conflict message if there is a conflict.
    """
    # Convert policies to RDF
    existing_graph = convert_to_rdf(existing_policy)
    request_graph = convert_to_rdf(request_policy)

    # Define the SPARQL query to check for conflicts
    sparql_query = """
    PREFIX odrl: <http://www.w3.org/ns/odrl/2/>
    PREFIX dpv: <https://w3id.org/dpv/dpv-owl#>

    SELECT ?action ?assignee ?target ?purpose
    WHERE {
        ?proh odrl:action ?action ;
              odrl:assignee ?assignee ;
              odrl:target ?target ;
              odrl:constraint ?constraint .
        ?constraint odrl:leftOperand "purpose" ;
                    odrl:operator odrl:eq ;
                    odrl:rightOperand ?purpose .

        ?perm odrl:action ?action ;
              odrl:assignee ?assignee ;
              odrl:target ?target ;
              odrl:constraint ?req_constraint .
        ?req_constraint odrl:leftOperand "purpose" ;
                        odrl:operator odrl:eq ;
                        odrl:rightOperand ?purpose .
    }
    """

    # Check for conflicts using SPARQL
    conflict_results = existing_graph.query(sparql_query, initBindings={'perm': request_graph})

    if conflict_results:
        conflict_message = "Conflicts detected for actions, assignees, and targets with purposes: "
        for row in conflict_results:
            conflict_message += f"Action: {row.action}, Assignee: {row.assignee}, Target: {row.target}, Purpose: {row.purpose}. "
        return conflict_message
    return None

def convert_to_rdf(policy: Dict) -> Graph:
    """
    Converts the given policy dictionary to an RDF graph.
    """
    g = Graph()
    g.parse(data=policy, format="json-ld")
    return g


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define your data models
class ODRLData(BaseModel):
    # Define the structure of your ODRL data here
    pass

@app.get("/")
async def home(request: Request):
    rules = data_helper.get_rules_from_odrl("./media/default_ontology/ODRL22.rdf")
    actors = data_helper.get_actors_from_dpv("./media/default_ontology/dpv.rdf")
    actions = data_helper.get_actions_from_odrl("./media/default_ontology/ODRL22.rdf")
    targets = data_helper.get_dataset_titles_and_uris("./media/default_ontology/Datasets.ttl")
    constraints = data_helper.get_constraints_types_from_odrl("./media/default_ontology/ODRL22.rdf")
    purposes = data_helper.get_purposes_from_dpv("./media/default_ontology/dpv.rdf")
    operators = data_helper.get_operators_from_odrl("./media/default_ontology/ODRL22.rdf")

    rules.append({"label": "Obligation", "uri": "http://www.w3.org/ns/odrl/2/Obligation"})

    return templates.TemplateResponse("odrl_editor.html", {
        "request": request,
        "rules": rules,
        "actions": actions,
        "targets": targets,
        "purposes": purposes,
        "constraints": constraints,
        "operators": operators,
        "actors": actors,
    })

@app.post("/convert_to_odrl")
async def convert_to_odrl(data: List[ODRLData]):
    try:
        # Initialize translator and parse the incoming request data
        translator = LogicTranslator()
        response = [item.dict() for item in data]
        filtered_response = filter_dicts_with_none_values(response)
        odrl = data_helper.convert_list_to_odrl_jsonld_no_user(filtered_response)

        try:
            odrl_parser = ODRLParser()
            policies = odrl_parser.parse_list([odrl])
            logic = translator.translate_policy(policies)
            return {"odrl": odrl, "formal_logic": logic, "data": filtered_response}
        except BaseException as b:
            return {"odrl": odrl}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def has_none_value_on_first_level(d):
    """ Check if dictionary d has at least one None value on the first level """
    return any((value is None) or (value == '' and key == "value") for key, value in d.items())

def filter_dicts_with_none_values(data):
    """
    Recursively filter out dictionaries from data that have at least one None value on the first level.
    Handles nested lists and dictionaries.
    """
    if isinstance(data, list):
        filtered_list = []
        for item in data:
            if isinstance(item, dict):
                if not has_none_value_on_first_level(item):
                    filtered_list.append(filter_dicts_with_none_values(item))
            elif isinstance(item, list):
                filtered_list.append(filter_dicts_with_none_values(item))
            else:
                filtered_list.append(item)
        return filtered_list
    elif isinstance(data, dict):
        filtered_dict = {}
        for key, value in data.items():
            if isinstance(value, dict):
                if not has_none_value_on_first_level(value):
                    filtered_dict[key] = filter_dicts_with_none_values(value)
            elif isinstance(value, list):
                filtered_dict[key] = filter_dicts_with_none_values(value)
            else:
                filtered_dict[key] = value
        return filtered_dict
    else:
        return data
