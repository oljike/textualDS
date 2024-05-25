import requests

# Your Supabase project URL
base_url = "https://xlprsctgblztnkbcqeoo.supabase.co"

# Your table endpoint (replace 'agents' with your actual table name)
endpoint = '/rest/v1/agents'

# Your headers with the secret token (Service Role Key)
headers = {
    'apikey': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhscHJzY3RnYmx6dG5rYmNxZW9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNjQ2MzY2NSwiZXhwIjoyMDMyMDM5NjY1fQ.42khHQ9L3se8cWtw44Z35z3BMwJ3ThEbZeMLQlxXAVk", # For the API key
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhscHJzY3RnYmx6dG5rYmNxZW9vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNjQ2MzY2NSwiZXhwIjoyMDMyMDM5NjY1fQ.42khHQ9L3se8cWtw44Z35z3BMwJ3ThEbZeMLQlxXAVk",  # For the authorization header
    'Content-Type': 'application/json'  # Content type for the request
}

# Make the GET request to the /rest/v1/agents endpoint
response = requests.get(f"{base_url}{endpoint}", headers=headers)

# Check the response status code and content
if response.status_code == 200:
    print("Request was successful!")
    print(response.json())
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
