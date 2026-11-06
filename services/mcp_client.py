import sys

from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_github_tool(
    tool_name: str,
    arguments: dict,
):

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

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            return result

