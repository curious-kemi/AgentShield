# Import load_dotenv to load configuration values from our .env file
from dotenv import load_dotenv 
import requests

# Import os to access environment variables in Python
import os

# Load the variables from .env into the Python process environment
# We do this because Python doesn't automatically read .env files
load_dotenv()

# Retrieve the URL of our ServiceNow instance
# This tells our application where to send API requests
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")

# Check whether the instance URL was successfully loaded
# bool() returns True if the value exists and is not empty
print(bool(instance_url))

# Retrieve the Client ID of our registered ServiceNow OAuth application
# The Client ID identifies our integration when requesting an access token
client_id = os.getenv("SERVICENOW_CLIENT_ID")

# Check whether the Client ID was loaded without printing the actual value
print(bool(client_id))

# Retrieve the Client Secret associated with our OAuth application
# ServiceNow uses this secret to authenticate our integration
client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")

# Check whether the Client Secret was loaded without exposing it
print(bool(client_secret))

#Python code that will allow your FastAPI backend to authenticate to ServiceNow using OAuth 2.0.
token_url = f"{instance_url}/oauth_token.do"



# Prepare the information needed to request an OAuth access token from ServiceNow.
# We use a Python dictionary because the OAuth request requires named parameters
# (key-value pairs) that ServiceNow can identify.

# client_id: Identifies our registered ServiceNow integration.
# client_secret: Authenticates our integration to ServiceNow.
# grant_type: Tells ServiceNow which OAuth authentication flow we're requesting.
# client_credentials: Requests a token for the backend integration itself,
# rather than for an employee using the AI agent.

# The client ID and secret come from our .env configuration,
# so we don't hardcode the actual credentials into our Python source code.
token_data = {
    "client_id":client_id,
    "client_secret":client_secret,
    "grant_type":"client_credentials"

}

# send this information to ServiceNow's OAuth endpoint and store whatever ServiceNow sends back in response
response = requests.post(token_url, data=token_data, timeout=10)

# Show me whether ServiceNow accepted or rejected the request
print(response.status_code)
access_token = response.json().get("access_token")
print(bool(access_token))


#REQUEST 2

# The f-string automatically pulls the values from the variables
incident_url = f"{instance_url}/api/now/table/incident"

# Step 1: Prepare the ticket details
short_description = input("Enter a short description: ")
description = input("Enter a detailed description: ")

incident_data = {
    "short_description": short_description,
    "description": description
}

# Step 2: Attach the OAuth access token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Step 3: Prepare authentication headers
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Step 4: Create the incident
incident_url = f"{instance_url}/api/now/table/incident"

incident_response = requests.post(
    incident_url,
    headers=headers,
    json=incident_data,
    timeout=10
)

# Step 5: Inspect the result
print("Incident status:", incident_response.status_code)

if incident_response.status_code == 201:
    result = incident_response.json().get("result", {})
    print("Incident created:", result.get("number"))
else:
    print("Incident creation failed. Check ServiceNow permissions and logs.")

print(incident_response.status_code)
print(incident_response.json())