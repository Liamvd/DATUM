from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()


def send_to_allegrograph(rdf_file_path, server_url, repo_name, username, password):
    # Define AllegroGraph repository URL
    repository_url = f"https://{server_url}/repositories/{repo_name}/statements"
    # Open RDF
    with open(rdf_file_path, 'rb') as rdf_file:
        # Set headers
        headers = {
            'Content-Type': 'application/rdf+xml'
        }

        # Send RDF data to AllegroGraph
        response = requests.post(
            repository_url,
            headers=headers,
            data=rdf_file,
            auth=(username, password)
        )

    # Check response
    if response.status_code == 204:
        print("RDF data successfully uploaded to AllegroGraph.")
    else:
        print(f"Failed to upload RDF data. Status code: {response.status_code}, Response: {response.text}")


send_to_allegrograph(
    rdf_file_path='output/metadata.rdf',
    server_url=os.getenv('ag_url'),
    repo_name=os.getenv('ag_repo'),
    username=os.getenv("ag_admin"),
    password=os.getenv("ag_password")
)