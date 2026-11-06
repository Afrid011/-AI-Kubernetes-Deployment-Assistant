import asyncio
import sys

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "mcp_servers/docker_server.py"
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
                "DOCKER MCP TOOLS"
            )
            print(
                "================"
            )

            tools = await session.list_tools()

            for tool in tools.tools:

                print(
                    f"- {tool.name}"
                )

            print()
            print(
                "Docker version:"
            )

            result = await session.call_tool(
                "docker_version",
                {}
            )

            print(result)

            print()
            print(
                "Docker images:"
            )

            result = await session.call_tool(
                "list_images",
                {}
            )

            print(result)


if __name__ == "__main__":

    asyncio.run(main())
