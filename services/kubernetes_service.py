import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MCP_SERVER = str(PROJECT_ROOT / "mcp_servers" / "kubernetes_server.py")

# ============================================================
# MCP CLIENT
# ============================================================

async def _call_tool(tool_name, arguments):

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER],
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

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            parsed = []

            for item in result.content:

                if hasattr(item, "text"):

                    try:
                        parsed.append(json.loads(item.text))
                    except Exception:
                        parsed.append(item.text)

                elif hasattr(item, "data"):
                    parsed.append(item.data)

            if len(parsed) == 1:
                return parsed[0]

            return parsed

# ============================================================
# SYNCHRONOUS WRAPPER
# ============================================================

def call_kubernetes_tool(tool_name, arguments):

    return asyncio.run(
        _call_tool(
            tool_name,
            arguments,
        )
    )

# ============================================================
# SERVICE FUNCTIONS
# ============================================================

def list_namespaces():

    return call_kubernetes_tool(
        "list_namespaces",
        {},
    )


def deploy_application(
    name,
    image,
    namespace,
    replicas,
    container_port,
):

    return call_kubernetes_tool(
        "deploy_application",
        {
            "name": name,
            "image": image,
            "namespace": namespace,
            "replicas": replicas,
            "container_port": container_port,
        },
    )


def get_deployment_status(
    name,
    namespace,
):

    return call_kubernetes_tool(
        "get_deployment_status",
        {
            "name": name,
            "namespace": namespace,
        },
    )


def get_pods(
    name,
    namespace,
):

    return call_kubernetes_tool(
        "get_pods",
        {
            "name": name,
            "namespace": namespace,
        },
    )


def create_loadbalancer(
    name,
    namespace,
    port,
    target_port,
):

    return call_kubernetes_tool(
        "create_loadbalancer",
        {
            "name": name,
            "namespace": namespace,
            "port": port,
            "target_port": target_port,
        },
    )


def get_service(
    name,
    namespace,
):

    return call_kubernetes_tool(
        "get_service",
        {
            "name": name,
            "namespace": namespace,
        },
    )


def get_application_url(
    name,
    namespace,
):

    return call_kubernetes_tool(
        "get_application_url",
        {
            "name": name,
            "namespace": namespace,
        },
    )

# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KUBERNETES MCP CLIENT TEST")
    print("=" * 60)

    try:

        namespaces = list_namespaces()

        print("\nNamespaces:")
        print(namespaces)

    except Exception as e:

        print(f"\nError: {e}")

