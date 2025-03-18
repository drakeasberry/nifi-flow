import os
import json
import requests
import yaml

# GitHub repository info
GITHUB_REPO_URL = "https://api.github.com/repos/drakeasberry/nifi-flow/tree/main/CreateGitVersionedBucket"
FLOW_JSON_FILE = "CreateGitVersionedBucket/NewGitBucket.json"  # Path to your flow JSON file in GitHub or local

# NiFi Registry base URL
NIFI_REGISTRY_URL = "http://localhost:18080/nifi-registry-api"
BUCKETS_YAML_FILE = "buckets.yaml"  # Location of the bucket.yaml file


# Function to fetch the flow JSON from GitHub (or local file)
def fetch_flow_json():
    # If from GitHub (requires access token for private repos)
    headers = {
        "Authorization": "GITHUB_ACCESS_TOKEN"
    }  # If necessary
    response = requests.get(f"{GITHUB_REPO_URL}/{FLOW_JSON_FILE}", headers=headers)
    print(response)
    if response.status_code == 200:
        content = json.loads(response.json()["content"])
        return json.loads(content)
    else:
        raise Exception(f"Error fetching flow JSON from GitHub: {response.status_code}")


# Function to load the current NiFi Registry bucket YAML
def load_buckets_yaml():
    with open(BUCKETS_YAML_FILE, "r") as f:
        return yaml.safe_load(f)


# Function to update buckets.yaml with new flow data
def update_buckets_yaml(flow_data):
    buckets = load_buckets_yaml()

    # Ensure the bucket exists
    bucket = next(
        (
            b
            for b in buckets["buckets"]
            if b["identifier"] == flow_data["flow"]["identifier"]
        ),
        None,
    )
    if not bucket:
        # Create a new bucket if it doesn't exist
        bucket = {
            "identifier": flow_data["flow"]["identifier"],
            "name": flow_data["flow"]["name"],
            "description": flow_data["flow"]["description"],
            "createdTimestamp": flow_data["flow"]["createdTimestamp"],
            "versionCount": 0,
            "flows": [],
        }
        buckets["buckets"].append(bucket)

    # Update or add flow to the bucket
    flow = {
        "identifier": flow_data["flow"]["identifier"],
        "name": flow_data["flow"]["name"],
        "description": flow_data["flow"]["description"],
        "createdTimestamp": flow_data["flow"]["createdTimestamp"],
    }
    bucket["flows"].append(flow)

    # Save the updated YAML
    with open(BUCKETS_YAML_FILE, "w") as f:
        yaml.dump(buckets, f, default_flow_style=False)

    print(f"Bucket '{bucket['name']}' updated in {BUCKETS_YAML_FILE}.")


# Main function
def sync_flow():
    try:
        # Fetch the flow JSON
        flow_data = fetch_flow_json()

        # Update the bucket and flow in the YAML
        update_buckets_yaml(flow_data)

        print("Sync completed successfully.")

    except Exception as e:
        print(f"Error during sync: {str(e)}")


if __name__ == "__main__":
    sync_flow()
