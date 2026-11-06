import asyncio
import sys

from mcp import (
    ClientSession,
    StdioServerParameters
)

from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "mcp_servers/kubernetes_server.py"
        ]
    )

    async with stdio_client(
        server_params
    ) as (
        read_stream,
        write_stream
    ):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            print()
            print("=" * 60)
            print("KUBERNETES MCP")
            print("=" * 60)

            tools = await session.list_tools()

            for tool in tools.tools:

                print(
                    f"- {tool.name}"
                )

            print()
            print(
                "Testing Kubernetes..."
            )

            result = await session.call_tool(
                "list_namespaces",
                {}
            )

            print()

            for content in result.content:

                print(
                    content.text
                )


if __name__ == "__main__":

    asyncio.run(main())
