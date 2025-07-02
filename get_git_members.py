import requests

# Replace with your values
GITHUB_TOKEN = "xxxxx"  # Your GitHub personal access token
ORG_NAME = "YOUR ORGANIZATION"  # The name of the GitHub organization
BASE_URL = f"https://api.github.com/orgs/{ORG_NAME}/members"

# Set up headers for GitHub API
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
}

# Function to get all members of the organization
def get_members():
    members = []
    page = 1
    while True:
        url = f'{BASE_URL}?page={page}&per_page=100'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching members: {response.status_code}")
            break

        data = response.json()
        if not data:  # No more members
            break

        members.extend(data)
        page += 1

    return members

# Function to get details of a member (including the name)
def get_member_name(username):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching details for {username}: {response.status_code}")
        return None

    user_data = response.json()
    return user_data.get('name', 'No name available')  # Returns the name or a default message

# Main function to fetch members and print their names
def get_and_print_member_names():
    members = get_members()
    print(f"Total members in the organization: {len(members)}")

    for member in members:
        username = member['login']
        name = get_member_name(username)
        print(f"Username: {username}, Name: {name}")

if __name__ == '__main__':
    get_and_print_member_names()
