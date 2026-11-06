import asyncio
import sys

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "mcp_servers/git_server.py"
        ],
    )

    async with stdio_client(
        server_params
    ) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            print(
                "GIT MCP TOOLS"
            )

            for tool in tools.tools:

                print(
                    f"- {tool.name}"
                )

            result = await session.call_tool(
                "clone_repository",
                {
                    "clone_url":
                        "https://github.com/Afrid011/website.git",

                    "repository_name":
                        "test-repository",

                    "branch":
                        "master"
                }
            )

            print(result)


if __name__ == "__main__":

    asyncio.run(main())

