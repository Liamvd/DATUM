import requests


def send_to_allegrograph(graph, server_url: str, repository: str, username: str, password: str):
    """
    Sends the RDF data to an AllegroGraph repository of choosing.

    Args:
        graph: The rdf graph object to send.
        server_url: The base URL of the AllegroGraph server (e.g., "https://1a2s3d4f5g6h7j8k9l.allegrograph.cloud").
        repository: The name of the target repository (e.g., "projectdata").
        username: Your AllegroGraph username (e.g., "admin").
        password: Your AllegroGraph password (e.g., "wsDedHtJUrjyNtfCkgh").
    """
    if not len(graph):
        print("Graph is empty. Nothing to send.")
        return

    # The repository URL for adding statements
    url = f"{server_url}/repositories/{repository}/statements"

    headers = {
        # Use the correct MIME type for Turtle
        'Content-Type': 'application/x-turtle'
    }

    try:
        response = requests.post(
            url,
            data=graph.encode('utf-8'),
            headers=headers,
            auth=(username, password)
        )

        # Check for success (204 No Content is AllegroGraph's success response)
        if response.status_code == 204:
            print(f"Successfully loaded {len(graph)} triples into repository '{repository}'.")
        else:
            print(f"Error loading data: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred connecting to AllegroGraph: {e}")
