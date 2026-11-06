import asyncio
import sys

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "mcp_servers/github_server.py"
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

            print()
            print(
                "AVAILABLE GITHUB MCP TOOLS"
            )
            print(
                "=========================="
            )

            tools = await session.list_tools()

            for tool in tools.tools:

                print(
                    f"- {tool.name}: "
                    f"{tool.description}"
                )

            print()
            print(
                "Fetching repositories..."
            )

            result = await session.call_tool(
                "list_repositories",
                {}
            )

            print()
            print(result)


if __name__ == "__main__":

    asyncio.run(main())
