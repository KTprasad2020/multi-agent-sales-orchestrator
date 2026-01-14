import os
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import ConnectedAgentTool

# 1. Connect to your Foundry Project
# Make sure you have your connection string in an environment variable
project_client = AIProjectClient.from_connection_string(
    conn_str=os.getenv("AZURE_PROJECT_CONNECTION_STRING"), # Added missing comma
    credential=DefaultAzureCredential()
)

# 2. Define the 'Manager'
# Note: Ensure QUALIFIER_AGENT_ID and RESEARCHER_AGENT_ID are 
# copied from your AI Foundry portal 'Agents' tab.
manager_agent = project_client.agents.create_agent(
    model="gpt-4o-mini",
    name="Sales_Manager",
    instructions="You coordinate lead requests. Use 'Lead_Qualifier' for intent and 'Company_Researcher' for details. Summarize both for a final report.",
    tools=[
        ConnectedAgentTool(id="QUALIFIER_AGENT_ID", name="Lead_Qualifier"),
        ConnectedAgentTool(id="RESEARCHER_AGENT_ID", name="Company_Researcher")
    ]
)

# 3. Start a conversation
print("Agent Team Active. Enter a lead:")
user_input = input("> ")
thread = project_client.agents.create_thread()
project_client.agents.create_message(thread_id=thread.id, role="user", content=user_input)

# 4. Run the team and WAIT for the result
run = project_client.agents.create_run(thread_id=thread.id, assistant_id=manager_agent.id)

# 5. NEW: Loop to check if the agent is done
while run.status in ["queued", "in_progress"]:
    time.sleep(1) # Wait 1 second before checking again
    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
    print(f"Status: {run.status}...")

# 6. NEW: Print the final answer
if run.status == "completed":
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print("\n--- Final Report ---")
    print(messages.data[0].content[0].text.value)
