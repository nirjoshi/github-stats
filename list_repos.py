import requests
import json
import datetime
import time
import csv

from datetime import date

<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
FILENAME = "member5.txt"
PRINT_ENABLED = True

# Replace with your own values
TOKEN = 'xxxxxx' # Your GitHub personal access token
ORG_NAME = 'OrganizationName'  # The name of the GitHub organization
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
FILENAME = "OUTPUT_FILE.csv" # Output CSV file name
PRINT_ENABLED = True

# Replace with your own values
TOKEN = 'YOUR_GITHUB_TOKEN' # GitHub personal access token
ORG_NAME = 'ORGANIZATION_NAME'  # GitHub organization name
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

# GitHub API endpoint
BASE_URL = 'https://api.github.com'
HEADERS = {'Authorization': f'token {TOKEN}'}

# Function to fetch all repositories in the organization
def get_repositories(org_name):
    repos = []
    page = 1
    while True:
        url = f'{BASE_URL}/orgs/{org_name}/repos?per_page=100&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            repo_data = response.json()
            if not repo_data:  # No more repositories
                break
            repos.extend([repo['name'] for repo in repo_data])
            page += 1
        else:
            if PRINT_ENABLED:
                print(f"Error fetching repositories: {response.status_code}")
            break
    return repos


# Main function to orchestrate fetching repos and commits
def main():
    # Step 1: Get all repositories in the organization
    print(f"Fetching repositories for organization: {ORG_NAME}")
    repos = get_repositories(ORG_NAME)

    print(f"Found {len(repos)} repositories.")

    for repo in repos:
        if PRINT_ENABLED:
           print(repo)

if __name__ == "__main__":
    main()
