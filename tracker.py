import requests

def get_pull_count(namespace: str, repo: str) -> int:
    """
    Fetches the exact pull count for a given Docker Hub repository.
    """
    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get("pull_count", 0)

if __name__ == "__main__":
    namespace = "lmcache"
    repositories = ["vllm-openai", "lmstack-router"]

    for repo in repositories:
        try:
            count = get_pull_count(namespace, repo)
            print(f"{namespace}/{repo}: {count:,} pulls")
        except requests.HTTPError as e:
            print(f"Failed to fetch pull count for {namespace}/{repo}: {e}")