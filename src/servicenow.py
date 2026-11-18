from dotenv import load_dotenv 
import requests
import os

load_dotenv()

# Load credentials
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
client_id = os.getenv("SERVICENOW_CLIENT_ID")
client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")

# Construct OAuth URL
token_url = f"{instance_url}/oauth_token.do"


# we want to request a token when our backend needs to communicate with ServiceNow
def get_access_token():

    # Prepare token_data
    token_data = {
    "client_id":client_id,
    "client_secret":client_secret,
    "grant_type":"client_credentials"

    }

    # Request OAuth token
    response = requests.post(token_url, data=token_data, timeout=10)

    # Check response
    response.raise_for_status()

    access_token = response.json().get("access_token")

    if not access_token:
        raise RuntimeError("ServiceNow did not return an access token")

    # Return token
    return access_token

#  Build the incident-creation function
def create_servicenow_incident(short_description, description):
    access_token = get_access_token()

    # Construct incident URL
    incident_url = f"{instance_url}/api/now/table/incident"

    # Prepare incident_data
    incident_data = {
    "short_description": short_description,
    "description": description
    }

    # Prepare headers containing access_token
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
    }

    # Send POST request to ServiceNow
    incident_response = requests.post(
    incident_url,
    headers=headers,
    json=incident_data,
    timeout=10
    )

    # Check response
    incident_response.raise_for_status()

    result = incident_response.json().get("result", {})
    incident_number = result.get("number")

    # return an error message if no incident number
    if not incident_number:
        raise RuntimeError("ServiceNow did not return an incident number")

    return incident_number