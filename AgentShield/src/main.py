from fastapi import FastAPI
from pydantic import BaseModel
from AgentShield.src.servicenow import create_servicenow_incident


app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}

# FastAPI need to receive ticket information through an HTTP request

# Tells Pydantic to validate incoming data against that structure.
class IncidentRequest(BaseModel):
    short_description: str
    description: str

# Create a POST endpoint that receives IT incident requests
@app.post("/incidents")
def create_incident(incident: IncidentRequest):

    # Get the short description and description from the incoming
    # HTTP request, then pass them to our ServiceNow integration function.
    # The function creates the ticket in ServiceNow and returns its number.
    incident_number = create_servicenow_incident(
        incident.short_description,
        incident.description
    )

    # Send the incident number back to whoever called this API.
    # FastAPI automatically converts this dictionary into a JSON response.
    return {"incident_number": incident_number}
