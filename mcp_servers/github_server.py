import os

from dotenv import load_dotenv
from github import Github
from fastmcp import FastMCP

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not configured")

github = Github(GITHUB_TOKEN)

# MCP Server
server = FastMCP("GitHub MCP Server")

@server.tool()
async def list_files(
    repository: str,
    path: str = ""
) -> list:
    """
    List files and directories in a GitHub repository.
    """

    repo = github.get_repo(repository)

    contents = repo.get_contents(path)

    files = []

    for item in contents:

        files.append(
            {
                "name": item.name,
                "path": item.path,
                "type": item.type,
                "size": item.size,
            }
        )

    return files


@server.tool()
async def get_file(
    repository: str,
    path: str
) -> dict:
    """
    Get the contents of a file from GitHub.
    """

    repo = github.get_repo(repository)

    file = repo.get_contents(path)

    if isinstance(file, list):
        raise RuntimeError(
            f"{path} is a directory, not a file"
        )

    content = file.decoded_content.decode(
        "utf-8",
        errors="replace"
    )

    return {
        "path": file.path,
        "size": file.size,
        "content": content,
    }
@server.tool
async def list_repositories() -> list:
    """
    List GitHub repositories accessible by the configured account.
    """

    user = github.get_user()

    repositories = []

    for repo in user.get_repos(sort="updated"):
        repositories.append(
            {
                "name": repo.name,
                "full_name": repo.full_name,
                "private": repo.private,
                "default_branch": repo.default_branch,
                "clone_url": repo.clone_url,
                "html_url": repo.html_url,
                "description": repo.description,
            }
        )

    return repositories


@server.tool
async def get_repository(repository: str) -> dict:
    """
    Get information about a specific GitHub repository.
    """

    repo = github.get_repo(repository)

    return {
        "name": repo.name,
        "full_name": repo.full_name,
        "private": repo.private,
        "default_branch": repo.default_branch,
        "clone_url": repo.clone_url,
        "html_url": repo.html_url,
        "description": repo.description,
    }


@server.tool
async def list_branches(repository: str) -> list:
    """
    List branches for a GitHub repository.
    """

    repo = github.get_repo(repository)

    branches = []

    for branch in repo.get_branches():
        branches.append(branch.name)

    return branches


async def main():
    await server.run_async(transport="stdio")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

