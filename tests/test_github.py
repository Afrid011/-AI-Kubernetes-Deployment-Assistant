import os

from dotenv import load_dotenv
from github import Github


load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    raise RuntimeError(
        "GITHUB_TOKEN is not configured in .env"
    )


github = Github(token)

user = github.get_user()

print()
print("GitHub authentication successful")
print("----------------------------------")
print("User:", user.login)

print()
print("Repositories")
print("------------")

for repo in user.get_repos():

    print(
        f"- {repo.full_name}"
    )
