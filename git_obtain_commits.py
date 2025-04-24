# This script fetches the number of user-ids from "input_members.txt" and
# queries the GitHub API to get the number of commits, additions, and deletions
# made by each user in a given organization between two branches of each repository in the organization.

# It uses the GitHub API to get commit details and caches the results to avoid
# redundant API calls. The script also checks the rate limit of the API and waits
# if necessary. The results are printed to the console.



import requests
import json
import datetime
import time
import csv
import pickle  # For optional disk caching

from datetime import datetime



# ----------------------------- CONFIG -----------------------------
FILENAME = "input_members.txt"
TOKEN = 'xxxxxx'  # Replace with secure token
ORG_NAME = 'org-name' # Replace with your organization name
START_ISO_DATE = "2025-02-08T00:00:00Z" 
END_ISO_DATE = "2025-04-09T00:00:00Z"
#END_ISO_DATE = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z" # End date in ISO 8601 format

BASE_URL = 'https://api.github.com'
HEADERS = {'Authorization': f'token {TOKEN}'}
DEBUG = False

# Optional: Enable saving/loading cache
USE_DISK_CACHE = True
CACHE_FILE = "commit_cache.pkl"
BRANCH1 = 'main' # Replace with your main branch
BRANCH2 = 'feature' # Replace with your feature branch
# ------------------------------------------------------------------

commit_cache = {}

# Load commit cache from disk if enabled
if USE_DISK_CACHE:
    try:
        with open(CACHE_FILE, 'rb') as f:
            commit_cache = pickle.load(f)
    except FileNotFoundError:
        commit_cache = {}

# Check rate limit and sleep if near exhaustion
def check_and_wait_rate_limit():
    url = f'{BASE_URL}/rate_limit'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Warning: Could not fetch rate limit. Status: {response.status_code}")
        return
    data = response.json()
    remaining = data['rate']['remaining']
    reset_time = data['rate']['reset']
    if remaining < 50:  # Be conservative
        wait_seconds = reset_time - int(time.time()) + 5
        print(f"Rate limit almost exceeded. Sleeping for {wait_seconds} seconds.")
        time.sleep(wait_seconds)

        
# Function to get commits from a repo for a specific branch and user in a date range
def get_commits_for_branch(repo_name, branch, username):

    if DEBUG:
        print(f"Fetching commits for branch '{branch}' by '{username}'...")

    commits = {}
    page = 1
    while True:
        check_and_wait_rate_limit()
        url = (
            f'{BASE_URL}/repos/{ORG_NAME}/{repo_name}/commits'
            f'?sha={branch}&author={username}'
            f'&since={START_ISO_DATE}&until={END_ISO_DATE}'
            f'&per_page=100&page={page}'
        )
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching commits for branch {branch}: {response.status_code}")
            break
        commits_data = response.json()
        if not commits_data:
            break
        for commit in commits_data:
            commits[commit['sha']] = commit
        page += 1
    return commits

# Function to get unique commits between two branches for a specific user
def get_user_unique_commits_between_branches(repo_name, branch1, branch2, username):

    commits_branch1 = get_commits_for_branch(repo_name, branch1, username)
    commits_branch2 = get_commits_for_branch(repo_name, branch2, username)


    all_unique_commits = {**commits_branch1, **commits_branch2} 
    
    if DEBUG:
        print(f"Total unique commits for {username} between branches '{branch1}' and '{branch2}': {len(all_unique_commits)}")  
    
    return all_unique_commits


# Function to get all repositories for the organization

def get_repositories(org_name):
    repos = []
    page = 1
    while True:
        check_and_wait_rate_limit()
        url = f'{BASE_URL}/orgs/{org_name}/repos?per_page=100&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            break
        repo_data = response.json()
        if not repo_data:
            break
        repos.extend([repo['name'] for repo in repo_data])
        page += 1
    return repos

# Function to get commits for a specific user in a repository in a date range
def get_commits(repo_name, username):
    commits = []
    page = 1
    while True:
        check_and_wait_rate_limit()
        url = f'{BASE_URL}/repos/{ORG_NAME}/{repo_name}/commits?author={username}&since={START_ISO_DATE}&until={END_ISO_DATE}&per_page=100&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error fetching commits for {repo_name}: {response.status_code}")
            break
        commits_data = response.json()
        if not commits_data:
            break
        commits.extend(commits_data)
        page += 1
    return commits

# Function to get commit details for a specific SHA in a repository
def get_commit_details(sha, repo):
    key = (repo, sha)
    if DEBUG:
        print(f"--Key: {key}, SHA: {sha}, Repo: {repo}")
    if key in commit_cache:
        return commit_cache[key]

    check_and_wait_rate_limit()
    url = f'{BASE_URL}/repos/{ORG_NAME}/{repo}/commits/{sha}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching commit details for {sha}: {response.status_code}")
        return None
    
    if DEBUG:
        print(f"Fetching commit details for {sha} in {repo}...")

    data = response.json()
    commit_cache[key] = data
    return data

def main():

    start_time = datetime.now()
    print("Script started at:", start_time)

    member_rows = []
    with open(FILENAME, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            member_rows.append(row)

    repos = get_repositories(ORG_NAME)
    print(f"Found {len(repos)} repositories.")

    for user_index in member_rows:
        user = user_index[0]
        name = user_index[1]
        print(f"\n Git-User: {name} ({user})")

        total_additions = 0
        total_deletions = 0
        total_commits = 0

        for repo in repos:
           
            commits = get_user_unique_commits_between_branches(repo, BRANCH1, BRANCH2, user)

            if DEBUG:
                print(f"  Unique commits for {user} in {repo}: {len(commits)}")

            if not commits:
                continue
            print(f"  Repo: {repo}")
            for sha in commits:
                
                details = get_commit_details(sha, repo)

                if not details:
                    continue
                
                for file in details.get('files', []):
                    total_additions += file.get('additions', 0)
                    total_deletions += file.get('deletions', 0)
                    #if DEBUG:
                    print(f" Add: {file['additions']} | Delete: {file['deletions']} in {file['filename']}")
                total_commits += 1

        """ print(f"Summary for {name}:")
        print(f"  Commits: {total_commits}")
        print(f"  Additions: {total_additions}")
        print(f"  Deletions: {total_deletions}") """

        print(f"User: {name}: Commits: {total_commits}: Additions: {total_additions} : Deletions: {total_deletions}\n")

    end_time = datetime.now()
    print("Script ended at:", end_time)

    duration = end_time - start_time
    print("Total execution time:", duration)

    # Save cache to disk
    if USE_DISK_CACHE:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(commit_cache, f)

if __name__ == "__main__":
    main()
