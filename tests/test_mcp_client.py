import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_servers/test_server.py"],
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            print()
            print("AVAILABLE MCP TOOLS")
            print("===================")

            tools = await session.list_tools()

            for tool in tools.tools:
                print(
                    f"- {tool.name}: "
                    f"{tool.description}"
                )

            print()
            print("Calling hello...")

            result = await session.call_tool(
                "hello",
                {"name": "Reyaz"},
            )

            print(result)

            print()
            print("Calling add_numbers...")

            result = await session.call_tool(
                "add_numbers",
                {
                    "a": 10,
                    "b": 20,
                },
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())
