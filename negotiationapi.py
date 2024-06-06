from fastapi import FastAPI, Header, Path, Body
from typing import List, Dict
from enum import Enum
from pydantic import BaseModel, Field, validator

from fastapi import FastAPI, HTTPException, Header, Body
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

app = FastAPI(
    title="Negotiation Plugin API",
    description="UPCAST Negotiation Plugin API",
    version="1.0",
)


class NegotiationStatus(str, Enum):
    AGREED = 'agreed'
    ACCEPTED = 'accepted'
    VERIFIED = 'verified'
    FINALIZED = 'finalized'
    TERMINATED = 'terminated'
    REQUESTED = 'requested'
    OFFERED = 'offered'

class PolicyType(str, Enum):
    OFFER = 'offer'
    REQUEST = 'request'

class PartyType(str, Enum):
    CONSUMER = 'consumer'
    PRODUCES = 'producer'

class UpcastResourceDescriptionObject(BaseModel):
    id: str
    price: int
    environmental_effect: str
    resource_description: Dict


class UpcastRequestObject(BaseModel):
    id: Optional[str] = None
    type: PolicyType
    consumer_id: Optional[str] = None
    producer_id: str
    data_processing_workflow_object: Dict
    natural_language_document: str
    resource_description_object: UpcastResourceDescriptionObject
    odrl_policy: Dict
    negotiation_id: Optional[str] = None


class UpcastOfferObject(BaseModel):
    id: Optional[str] = None
    type: PolicyType
    consumer_id: str
    producer_id: Optional[str] = None
    data_processing_workflow_object: Dict
    natural_language_document: str
    resource_description_object: UpcastResourceDescriptionObject
    odrl_policy: Dict
    negotiation_id: Optional[str] = None


class UpcastNegotiationObject(BaseModel):
    id: Optional[str] = None
    consumer_id: str
    producer_id: str
    negotiation_status: NegotiationStatus
    resource_description: Dict
    dpw: Dict  # Data Process Workflow
    nlp: str  # Natural Language Part
    conflict_status: str  # Any detected conflict
    negotiations: List[Dict]  # List of UPCAST Request or UPCAST Offer
    class Config:
        use_enum_values = True  # Ensures the enum values are used instead of the enum type


class UpcastContractObject(BaseModel):
    id: Optional[str] = None
    corresponding_parties: Dict
    data_processing_workflow_object: Dict
    natural_language_document: str
    resource_description_object: Dict
    metadata: Dict
    status: str
    negotiation_id: str

def pydantic_to_dict(obj):
    if isinstance(obj, list):
        return [pydantic_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: pydantic_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, BaseModel):
        return pydantic_to_dict(obj.dict())
    if isinstance(obj, Enum):
        return obj.value
    return obj

user = "semih"
password = "a8Spt66DKqGh2V0T"
host = "cluster0.btnpvyy.mongodb.net"
MONGO_DETAILS = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.upcast
negotiations_collection = db.negotiations
requests_collection = db.requests
offers_collection = db.offers
contracts_collection = db.contracts

@app.post("/negotiation/create", summary="Create a negotiation", response_model=UpcastNegotiationObject)
async def create_upcast_negotiation(
        user_id: str = Header(..., description="The ID of the user"),
        body: UpcastRequestObject = Body(..., description="The request object")
):
    # Assign a new UUID if negotiation_id is None, in one line
    negotiation_id = body.negotiation_id or str(uuid.uuid4())
#    negotiation_id = str(uuid.uuid4())  # Generate a unique negotiation ID
    conflict_status = "no conflict"

    negotiation = UpcastNegotiationObject(
        id=negotiation_id,
        consumer_id=body.consumer_id,
        producer_id=body.producer_id,
        negotiation_status=NegotiationStatus.REQUESTED,
        resource_description=body.resource_description_object.dict(),
        dpw=body.data_processing_workflow_object,
        nlp=body.natural_language_document,
        conflict_status=conflict_status,
        negotiations=[body.dict()]
    )

    result = await negotiations_collection.insert_one(pydantic_to_dict(negotiation))
    if result.inserted_id:
        return negotiation

    raise HTTPException(status_code=500, detail="Negotiation could not be created")


@app.get("/negotiation/{negotiation_id}", summary="Get a negotiation", response_model=UpcastNegotiationObject)
async def get_upcast_negotiation(
        negotiation_id: str = Path(..., description="The ID of the negotiation"),
        user_id: str = Header(..., description="The ID of the user")
):
    negotiation = await negotiations_collection.find_one({"id": negotiation_id})
    if negotiation:
        return UpcastNegotiationObject(**negotiation)

    raise HTTPException(status_code=404, detail="Negotiation not found")



@app.get("/negotiation", summary="Get negotiations", response_model=List[UpcastNegotiationObject])
async def get_upcast_negotiations(
    user_id: str = Header(..., description="The ID of the user")
):
    negotiations = await negotiations_collection.find({"$or": [{"consumer_id": user_id}, {"producer_id": user_id}]}).to_list(length=None)
    if not negotiations:
        raise HTTPException(status_code=404, detail="No negotiations found for this user")
    return [UpcastNegotiationObject(**negotiation) for negotiation in negotiations]



@app.put("/negotiation/{negotiation_id}", summary="Update a negotiation")
async def update_upcast_negotiation(
    negotiation_id: str = Path(..., description="The ID of the negotiation"),
    user_id: str = Header(..., description="The ID of the user"),
    body: UpcastNegotiationObject = Body(..., description="The negotiation object")
):
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id},
        {"$set": pydantic_to_dict(body)}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Negotiation not found or you do not have permission to update this negotiation")

    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Negotiation update failed")

    return {"message": "Negotiation updated successfully", "negotiation_id": negotiation_id}



@app.delete("/negotiation/{negotiation_id}", summary="Delete a negotiation")
async def delete_upcast_negotiation(
    negotiation_id: str = Path(..., description="The ID of the negotiation"),
    user_id: str = Header(..., description="The ID of the user")
):
    # Delete the negotiation
    delete_result = await negotiations_collection.delete_one(
        {"id": negotiation_id, "$or": [{"consumer_id": user_id}, {"producer_id": user_id}]}
    )

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Negotiation not found or you do not have permission to delete this negotiation")

    # Delete corresponding requests
    await requests_collection.delete_many({"negotiation_id": negotiation_id})

    # Delete corresponding offers
    await offers_collection.delete_many({"negotiation_id": negotiation_id})

    return {"message": "Negotiation and corresponding requests and offers deleted successfully", "negotiation_id": negotiation_id}


# New endpoint
@app.get("/negotiation/{negotiation_id}/last-policy", summary="Get the last policy", response_model=Dict)
async def get_last_policy(
        negotiation_id: str = Path(..., description="The ID of the negotiation"),
        user_id: str = Header(..., description="The ID of the user")
):
    negotiation = await negotiations_collection.find_one({"id": negotiation_id, "$or": [{"consumer_id": user_id}, {"producer_id": user_id}]})
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    negotiations_list = negotiation.get("negotiations", [])
    if not negotiations_list:
        raise HTTPException(status_code=404, detail="No policies found in the negotiations")

    last_policy = negotiations_list[-1]
    return last_policy

@app.post("/negotiation/terminate/{negotiation_id}", summary="Terminate a negotiation")
async def terminate_upcast_negotiation(
    negotiation_id: str = Path(..., description="The ID of the negotiation"),
    user_id: str = Header(..., description="The ID of the user")
):
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id, "$or": [{"consumer_id": user_id}, {"producer_id": user_id}]},
        {"$set": {"negotiation_status": NegotiationStatus.TERMINATED.value}}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Negotiation not found or you do not have permission to terminate this negotiation")

    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Negotiation termination failed")

    return {"message": "Negotiation terminated successfully", "negotiation_id": negotiation_id}


@app.post("/consumer/request/new", summary="Create a new request")
async def create_new_upcast_request(
    user_id: str = Header(..., description="The ID of the user"),
    body: UpcastRequestObject = Body(..., description="The request object")
):
    body.id = body.id or str(uuid.uuid4())
    body.consumer_id = user_id
    await requests_collection.insert_one(body.dict())
    return {"request_id": body.id}

@app.get("/consumer/request/{request_id}", summary="Get an existing request", response_model=UpcastRequestObject)
async def get_upcast_request(
    request_id: str = Path(..., description="The ID of the request"),
    user_id: str = Header(..., description="The ID of the user")
):
    request = await requests_collection.find_one({"id": request_id})
    if request:
        return UpcastRequestObject(**request)
    else:
        raise HTTPException(status_code=404, detail="Request not found")


@app.put("/consumer/request/update", summary="Update an existing request")
async def update_upcast_request(
    user_id: str = Header(..., description="The ID of the user"),
    body: UpcastRequestObject = Body(..., description="The request object")
):
    await requests_collection.replace_one({"id": body.id}, body.dict())
    return {"message": "Request updated successfully", "request_id": body.id}


@app.post("/consumer/request/send", summary="Send a request for an existing negotiation")
async def send_upcast_request(
    user_id: str = Header(..., description="The ID of the user"),
    negotiation_id: str = Header(None, description="The ID of the negotiation"),
    body: UpcastRequestObject = Body(..., description="The offer object")
):
    if not negotiation_id:  # If negotiation_id is empty, create a new negotiation
        negotiation_id = str(uuid.uuid4())  # Generate a new negotiation ID
        negotiation = UpcastNegotiationObject(
            id=negotiation_id,
            consumer_id=user_id,
            producer_id=body.producer_id,  # Assuming producer_id is available in the request object
            negotiation_status=NegotiationStatus.REQUESTED,
            resource_description=body.resource_description_object.dict(),
            dpw=body.data_processing_workflow_object,
            nlp=body.natural_language_document,
            conflict_status="",  # Initialize with an empty string
            negotiations=[body.dict()]  # Add the request to negotiations list
        )
        await negotiations_collection.insert_one(negotiation.dict())
    else:
        # Update existing negotiation by appending the request to negotiations list
        await negotiations_collection.update_one(
            {"id": negotiation_id},
            {"$push": {"negotiations": body.dict()}}
        )
    return {"message": "Request sent successfully", "request_id": body.id, "negotiation_id": negotiation_id}


@app.delete("/consumer/request/{request_id}", summary="Delete a request")
async def delete_upcast_request(
        request_id: str = Path(..., description="The ID of the request"),
        user_id: str = Header(..., description="The ID of the user")
):
    # Find the request
    request = await requests_collection.find_one({"id": request_id})

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Delete the request
    delete_result = await requests_collection.delete_one({"id": request_id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404,
                            detail="Request not found or you do not have permission to delete this request")

    # If the request is part of a negotiation, remove it from the negotiation's negotiations field
    if request.get("negotiation_id"):
        await negotiations_collection.update_one(
            {"id": request["negotiation_id"]},
            {"$pull": {"negotiations": {"id": request_id}}}
        )

    return {"message": "Request deleted successfully", "request_id": request_id}



@app.get("/consumer/offer", summary="Get available offers", response_model=UpcastOfferObject)
async def get_upcast_offers(
        offer_id: str = Path(..., description="The ID of the offer"),
        user_id: str = Header(..., description="The ID of the user")
):
    offers = await offers_collection.find({
        "$or": [
            {"negotiation_id": {"$exists": False}},
            {"negotiation_id": ""}
        ]
    }).to_list(length=None)

    if not offers:
        raise HTTPException(status_code=404, detail="No offers found for this user")

    return [UpcastOfferObject(**offer) for offer in offers]


@app.post("/consumer/offer/accept", summary="Accept a request")
async def accept_upcast_request(
        user_id: str = Header(..., description="The ID of the user"),
        offer_id: str = Header(..., description="The ID of the offer")
):
    # Get the offer from the database
    offer = await offers_collection.find_one({"id": offer_id})

    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Get the negotiation ID associated with the offer
    negotiation_id = offer.get("negotiation_id")

    if negotiation_id is None:
        raise HTTPException(status_code=400, detail="Negotiation ID not found in the offer")

    # Update the negotiation status to "accepted" in the database
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id},
        {"$set": {"negotiation_status": NegotiationStatus.ACCEPTED.value}}
    )

    # Check if the negotiation was updated successfully
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update negotiation status")

    return {"message": "Offer accepted successfully", "offer_id": offer_id}

#
# @app.post("/consumer/offer/accept", summary="Accept a request")
# async def accept_upcast_request(
#     user_id: str = Header(..., description="The ID of the user"),
#     offer_id: str = Header(..., description="The ID of the request")
# ):
#     return {"message": "Offer accepted successfully", "offer_id": offer_id}


@app.post("/consumer/offer/verify", summary="Verify a request")
async def verify_upcast_request(
        user_id: str = Header(..., description="The ID of the user"),
        offer_id: str = Header(..., description="The ID of the request")
):
    # Get the offer from the database
    offer = await offers_collection.find_one({"id": offer_id})

    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Get the negotiation ID associated with the offer
    negotiation_id = offer.get("negotiation_id")

    if negotiation_id is None:
        raise HTTPException(status_code=400, detail="Negotiation ID not found in the offer")

    # Update the negotiation status to "verified" in the database
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id},
        {"$set": {"negotiation_status": NegotiationStatus.VERIFIED.value}}
    )

    # Check if the negotiation was updated successfully
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update negotiation status")

    return {"message": "Offer verified successfully", "offer_id": offer_id}


@app.post("/producer/offer/new", summary="Create a new offer")
async def create_new_upcast_offer(
        user_id: str = Header(..., description="The ID of the user"),
        body: UpcastOfferObject = Body(..., description="The offer object")
):
    # Generate a unique offer ID
    offer_id = body.id or str(uuid.uuid4())

    # Change the policy type to "offer"
    body.type = PolicyType.OFFER

    # Add user_id to the offer object
    body.producer_id = user_id

    # Save the offer to MongoDB
    await offers_collection.insert_one(body.dict())

    return {"offer_id": offer_id}

@app.post("/producer/offer/send", summary="Send a new offer")
async def send_new_upcast_offer(
        user_id: str = Header(..., description="The ID of the user"),
        body: UpcastOfferObject = Body(..., description="The offer object")
):
    # Generate a unique offer ID
    offer_id = str(uuid.uuid4())

    # Change the policy type to "offer"
    body.type = PolicyType.OFFER

    # Add user_id to the offer object
    body.producer_id = user_id

    # Save the offer to MongoDB
    await offers_collection.insert_one(body.dict())

    # Update the negotiations list under the existing negotiation with the negotiation ID
    negotiation_id = body.negotiation_id
    if negotiation_id:
        update_result = await negotiations_collection.update_one(
            {"id": negotiation_id},
            {"$push": {"negotiations": body.dict()}}
        )

        # Check if the negotiation was updated successfully
        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update negotiation with new offer")

    return {"offer_id": offer_id}


# @app.post("/producer/offer/new", summary="Create a new offer")
# async def create_new_upcast_offer(
#     user_id: str = Header(..., description="The ID of the user"),
#     body: UpcastOfferObject = Body(..., description="The offer object")
# ):
#     offer_id = "generated-id"  # Placeholder for actual negotiation ID generation
#     return {"offer_id": offer_id}


@app.get("/producer/offer/{offer_id}", summary="Get an existing offer", response_model=UpcastOfferObject)
async def get_upcast_offer(
        offer_id: str = Path(..., description="The ID of the offer"),
        user_id: str = Header(..., description="The ID of the user")
):
    # Retrieve the offer from the database using the provided offer_id
    offer = await offers_collection.find_one({"id": offer_id})

    # Check if the offer exists
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    return UpcastOfferObject(**offer)


@app.delete("/offer/{offer_id}", summary="Delete an offer")
async def delete_upcast_offer(
        offer_id: str = Path(..., description="The ID of the offer"),
        user_id: str = Header(..., description="The ID of the user")
):
    # Find the offer
    offer = await offers_collection.find_one({"id": offer_id})

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Delete the offer
    delete_result = await offers_collection.delete_one({"id": offer_id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404,
                            detail="Offer not found or you do not have permission to delete this offer")

    # If the offer is part of a negotiation, remove it from the negotiation's negotiations field
    if offer.get("negotiation_id"):
        await negotiations_collection.update_one(
            {"id": offer["negotiation_id"]},
            {"$pull": {"negotiations": {"id": offer_id}}}
        )

    return {"message": "Offer deleted successfully", "offer_id": offer_id}



@app.post("/producer/request/agree", summary="Agree on a request")
async def accept_upcast_offer(
        user_id: str = Header(..., description="The ID of the user"),
        request_id: str = Header(..., description="The ID of the request")
):
    # Get the request from the database
    request = await requests_collection.find_one({"id": request_id})

    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get the negotiation ID associated with the request
    negotiation_id = request.get("negotiation_id")

    if negotiation_id is None:
        raise HTTPException(status_code=400, detail="Negotiation ID not found in the request")

    # Update the negotiation status to "agree" in the database
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id},
        {"$set": {"negotiation_status": NegotiationStatus.AGREED.value}}
    )

    # Check if the negotiation was updated successfully
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update negotiation status")

    return {"message": "Request agreed successfully", "request_id": request_id}


@app.post("/producer/offer/finalize", summary="Accept an offer")
async def finalize_upcast_offer(
        user_id: str = Header(..., description="The ID of the user"),
        offer_id: str = Header(..., description="The ID of the offer")
):
    # Get the offer from the database
    offer = await offers_collection.find_one({"id": offer_id})

    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Get the negotiation ID associated with the offer
    negotiation_id = offer.get("negotiation_id")

    if negotiation_id is None:
        raise HTTPException(status_code=400, detail="Negotiation ID not found in the offer")

    # Update the negotiation status to "finalized" in the database
    update_result = await negotiations_collection.update_one(
        {"id": negotiation_id},
        {"$set": {"negotiation_status": NegotiationStatus.FINALIZED.value}}
    )

    # Check if the negotiation was updated successfully
    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update negotiation status")

    return {"message": "Offer finalized successfully", "offer_id": offer_id}

#
# @app.post("/producer/offer/finalize", summary="Accept an offer")
# async def accept_upcast_offer(
#     user_id: str = Header(..., description="The ID of the user"),
#     offer_id: str = Header(..., description="The ID of the offer")
# ):
#     return {"message": "Offer finalized successfully", "offer_id": offer_id}


@app.get("/contract/{negotiation_id}", summary="Get a contract (Under Construction)")
async def get_upcast_contract(
    negotiation_id: str = Path(..., description="The ID of the negotiation"),
    user_id: str = Header(..., description="The ID of the user")
):
    # Under Construction
    return {"message": "This endpoint is under construction"}


@app.post("/contract/sign", summary="Sign a contract (Under Construction)")
async def sign_upcast_contract(
    user_id: str = Header(..., description="The ID of the user"),
    body: UpcastContractObject = Body(..., description="The contract sign object")
):
    # Under Construction
    return {"message": "This endpoint is under construction"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
