import requests
import csv
import os
from datetime import datetime

def get_pull_count(namespace: str, repo: str) -> int:
    """
    Fetches the exact pull count for a given Docker Hub repository.
    """
    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get("pull_count", 0)

def save_to_csv(namespace: str, repo: str, pull_count: int, csv_file: str = "pull_counts.csv"):
    """
    Saves the pull count data to a CSV file with timestamp.
    """
    file_exists = os.path.isfile(csv_file)
    timestamp = datetime.now().isoformat()
    
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is new
        if not file_exists:
            writer.writerow(['timestamp', 'namespace', 'repository', 'pull_count'])
        writer.writerow([timestamp, namespace, repo, pull_count])

if __name__ == "__main__":
    namespace = "lmcache"
    repositories = ["vllm-openai", "lmstack-router"]

    for repo in repositories:
        try:
            count = get_pull_count(namespace, repo)
            print(f"{namespace}/{repo}: {count:,} pulls")
            save_to_csv(namespace, repo, count)
            print(f"Saved {namespace}/{repo} data to CSV")
        except requests.HTTPError as e:
            print(f"Failed to fetch pull count for {namespace}/{repo}: {e}")
        except Exception as e:
            print(f"Error saving data for {namespace}/{repo}: {e}")