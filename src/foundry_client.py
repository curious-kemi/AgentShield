import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentReference
from azure.ai.projects.models import FunctionTool
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam
from servicenow import create_incident


load_dotenv()


# Connect to Microsoft foundry 
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

print("Foundry client initialized")

# Define the function for the model 
# we are defining what an incident creation function expects
incident_tool = FunctionTool(
    name="create_incident",
    description="Create an IT support incident in ServiceNow",
    parameters={
        "type": "object",
        "properties": {
            "short_description": {
                "type": "string",
                "description": "Short summary of the IT issue"
            },
            "description": {
                "type": "string",
                "description": "Detailed explanation of the IT issue"
            }
        },
        "required": ["short_description", "description"],
        "additionalProperties": False
    },
    strict=True
)

 # the code is responsible for sending the user's question to your Foundry agent and getting a response.
user_message = input("Ask AgentShield: ")

with project_client.get_openai_client() as openai_client:
    # Create a conversation for multi-turn interaction
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        input=user_message,
        conversation=conversation.id,
        extra_body={
            "agent_reference": AgentReference(
                name="AgentShield-HR-IT",
                version="4"
            ).as_dict()
        }
    )

    if response.output_text:
        print("Agent response:", response.output_text)


    # create an empty list 
    input_list: ResponseInputParam = []

    # Execute the python function
    for item in response.output:
        if item.type == "function_call":
            if item.name == "create_incident":
                arguments = json.loads(item.arguments)
                result = create_incident(**arguments)

               # print(result)

                # This prepares the result to be sent back to Foundry.
                # add the mock function's result to that list.
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps(result),
                    )
                )

    # Send the function result back to AgentShield
    # Make the second responses.create() call
    if input_list:
        response = openai_client.responses.create(
            input=input_list,
            conversation=conversation.id,
            extra_body={
                "agent_reference": AgentReference(
                    name="AgentShield-HR-IT",
                    version="4"
                ).as_dict()
            }
        )

        print("Agent response:", response.output_text)