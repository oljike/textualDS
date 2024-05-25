from memgpt import create_client, Admin

# Connect to the server as a user

admin = create_client(supabase=True,
    base_url="https://xlprsctgblztnkbcqeoo.supabase.co",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhscHJzY3RnYmx6dG5rYmNxZW9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNjQ2MzY2NSwiZXhwIjoyMDMyMDM5NjY1fQ.42khHQ9L3se8cWtw44Z35z3BMwJ3ThEbZeMLQlxXAVk")

print(admin.list_agents())
# client = create_client(base_url="https://xlprsctgblztnkbcqeoo.supabase.co",
#                        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhscHJzY3RnYmx6dG5rYmNxZW9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNjQ2MzY2NSwiZXhwIjoyMDMyMDM5NjY1fQ.42khHQ9L3se8cWtw44Z35z3BMwJ3ThEbZeMLQlxXAVk")



# # Send a message to the agent
# agent_id = "ef5ed9ec-4b1b-451e-ab57-82a768500cf8"
# # messages = client.user_message(agent_id=client.list_agents()['agents'][1]['id'], message="Hello, agent!")
# # Create a helper that sends a message and prints the assistant response only
# client.list_sources()
# client.attach_source_to_agent(source_name="blockchain-price", agent_id=agent_id)
#
# def send_message(message: str):
#     """
#     sends a message and prints the assistant output only.
#     :param message: the message to send
#     """
#     response = client.user_message(agent_id=client.list_agents()['agents'][1]['id'], message=message)
#     for r in response:
#         # Can also handle other types "function_call", "function_return", "function_message"
#         if "assistant_message" in r:
#             print("ASSISTANT:", r["assistant_message"])
#         elif "internal_monologue" in r:
#             print("THOUGHTS:", r["internal_monologue"])
#
# # Send a message and see the response
# send_message("what news?")



# postgresql+pg8000://postgres.xlprsctgblztnkbcqeoo:Sovetskaya1@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
# postgres://postgres.xlprsctgblztnkbcqeoo:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres