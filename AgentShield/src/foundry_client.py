import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentReference
from azure.ai.projects.models import FunctionTool
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


load_dotenv()

# Mock ServiceNow incident creation function
def mock_create_incident(short_description: str, description: str):
    return {
        "status": "simulated",
        "short_description": short_description,
        "description": description,
        "message": "Test only. No ServiceNow incident was created."
    }


# Connect to Microsoft foundry 
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

print("Foundry client initialized")


# 2. Retrieve your existing agent configuration

agent = project_client.agents.get_version(
    agent_name="AgentShield-HR-IT",
    agent_version="3"
)

print("Existing agent definition:")
print(agent.definition)

for tool in agent.definition.tools:
    print(tool)




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

# keep AgentShield's existing tools while adding your new ServiceNow function tool
tools = list(agent.definition.tools) + [incident_tool]

#new_agent = project_client.agents.create_version(
 #   agent_name="AgentShield-HR-IT",
 #   definition=PromptAgentDefinition(
  #      model=agent.definition.model,
  #      instructions=agent.definition.instructions,
  #     tools=tools,
   # ),
#)

# print("New AgentShield version:", new_agent.version)

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

    print("\nAgent response:")
    print(response.output_text)

    # print("\nFunction calls:")
    # for item in response.output:
    #     if item.type == "function_call":
    #         print("Function:", item.name)
    #         print("Arguments:", item.arguments)
    #         print("Call ID:", item.call_id)

#     print("\nFull response output:")

# for item in response.output:
#     print(item)

    # create an empty list 
    input_list: ResponseInputParam = []


    # Execute the python function
    for item in response.output:
        if item.type == "function_call":
            if item.name == "create_incident":
                arguments = json.loads(item.arguments)
                result = mock_create_incident(**arguments)

                print(result)

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