import asyncio

from services.mcp_client import (
    call_github_tool
)


def list_repositories():

    result = asyncio.run(
        call_github_tool(
            "list_repositories",
            {}
        )
    )

    return result


def get_repository(
    repository: str
):

    result = asyncio.run(
        call_github_tool(
            "get_repository",
            {
                "repository": repository
            }
        )
    )

    return result


def list_branches(
    repository: str
):

    result = asyncio.run(
        call_github_tool(
            "list_branches",
            {
                "repository": repository
            }
        )
    )

    return result

