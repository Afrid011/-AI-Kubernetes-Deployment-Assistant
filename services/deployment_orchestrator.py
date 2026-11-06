import asyncio
import json
import os
import re
import sys

from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)

from services.dockerfile_generator import generate_dockerfile

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

WORKSPACE = "/root/ai-k8s-workspaces"

DOCKER_USERNAME = os.getenv("DOCKER_USERNAME")
DOCKER_REGISTRY = os.getenv("DOCKER_REGISTRY", "docker.io")

# ============================================================
# GENERIC MCP CLIENT
# ============================================================

async def call_mcp_server(server_file, tool_name, arguments):

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_file],
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

            return await session.call_tool(
                tool_name,
                arguments,
            )


async def call_git_tool(tool_name, arguments):

    return await call_mcp_server(
        "mcp_servers/git_server.py",
        tool_name,
        arguments,
    )


async def call_docker_tool(tool_name, arguments):

    return await call_mcp_server(
        "mcp_servers/docker_server.py",
        tool_name,
        arguments,
    )

# ============================================================
# MCP RESULT PARSER
# ============================================================

def parse_mcp_result(result):
    """
    Convert FastMCP CallToolResult into a Python dictionary.
    """

    if not hasattr(result, "content"):
        return {
            "success": False,
            "error": "Empty MCP response",
        }

    for item in result.content:

        if hasattr(item, "text"):

            text = item.text

            try:
                return json.loads(text)
            except Exception:
                return {
                    "success": False,
                    "error": text,
                }

    return {
        "success": False,
        "error": "Invalid MCP response",
    }

# ============================================================
# HELPERS
# ============================================================

def safe_image_name(repository):

    name = repository.split("/")[-1]
    name = name.replace(".git", "")
    name = name.lower()

    return re.sub(
        r"[^a-z0-9._-]",
        "-",
        name,
    )


def validate_docker_context(workspace_path):

    return os.path.isfile(
        os.path.join(workspace_path, "Dockerfile")
    )

# ============================================================
# CLONE REPOSITORY
# ============================================================

async def clone_repository(
    clone_url,
    repository,
    branch,
):

    repository_name = repository.split("/")[-1]
    repository_name = repository_name.replace(".git", "")

    print()
    print("=" * 60)
    print("CLONING GITHUB REPOSITORY")
    print("=" * 60)
    print(f"Repository : {repository}")
    print(f"Branch     : {branch}")
    print(f"Workspace  : {WORKSPACE}")

    response = await call_git_tool(
        "clone_repository",
        {
            "clone_url": clone_url,
            "repository_name": repository_name,
            "branch": branch,
        },
    )

    parsed = parse_mcp_result(response)

    workspace_path = os.path.join(
        WORKSPACE,
        repository_name,
    )

    return {
        "response": parsed,
        "workspace": workspace_path,
        "repository_name": repository_name,
    }

# ============================================================
# PREPARE APPLICATION
# ============================================================

async def prepare_application(
    repository,
    branch,
    clone_url,
):

    clone = await clone_repository(
        clone_url,
        repository,
        branch,
    )

    workspace = clone["workspace"]

    if not os.path.isdir(workspace):

        raise RuntimeError(
            f"Repository clone failed: {workspace}"
        )

    files = []

    for root, dirs, filenames in os.walk(workspace):

        dirs[:] = [
            d
            for d in dirs
            if d != ".git"
        ]

        for filename in filenames:

            files.append(
                os.path.relpath(
                    os.path.join(root, filename),
                    workspace,
                )
            )

    files.sort()

    dockerfile = os.path.join(
        workspace,
        "Dockerfile",
    )

    dockerfile_source = "repository"

    if not os.path.exists(dockerfile):

        print()
        print("=" * 60)
        print("GENERATING DOCKERFILE")
        print("=" * 60)

        generated = generate_dockerfile(
            files,
            workspace,
        )

        dockerfile_source = generated["project_type"]

        print(
            f"Detected project type : {generated['project_type']}"
        )

        print(
            f"Dockerfile generated at {generated['path']}"
        )

    return {
        "repository": repository,
        "branch": branch,
        "workspace": workspace,
        "files": files,
        "dockerfile_source": dockerfile_source,
    }

# ============================================================
# BUILD & PUSH
# ============================================================

async def build_and_push(
    repository,
    workspace_path,
):

    if not validate_docker_context(workspace_path):

        return {
            "success": False,
            "repository": repository,
            "error": "Dockerfile not found",
        }

    if not DOCKER_USERNAME:

        raise RuntimeError(
            "DOCKER_USERNAME is not configured"
        )

    image_name = (
        f"{DOCKER_USERNAME}/"
        f"{safe_image_name(repository)}"
    )

    tag = "latest"

    full_image = f"{image_name}:{tag}"

    print()
    print("=" * 60)
    print("DOCKER BUILD & PUSH")
    print("=" * 60)
    print(f"Repository : {repository}")
    print(f"Workspace  : {workspace_path}")
    print(f"Image      : {full_image}")
    print()

    # --------------------------------------------------
    # BUILD
    # --------------------------------------------------

    print("Building Docker image...")

    build_response = await call_docker_tool(
        "build_image",
        {
            "context_path": workspace_path,
            "image_name": image_name,
            "tag": tag,
        },
    )

    build_result = parse_mcp_result(build_response)

    if not build_result.get("success", False):

        return {
            "success": False,
            "stage": "build",
            "repository": repository,
            "image": full_image,
            "error": build_result.get(
                "error",
                "Docker build failed",
            ),
            "build": build_result,
        }

    print("Build completed.")

    # --------------------------------------------------
    # PUSH
    # --------------------------------------------------

    print()
    print("Pushing Docker image...")

    push_response = await call_docker_tool(
        "push_image",
        {
            "image_name": image_name,
            "tag": tag,
        },
    )

    push_result = parse_mcp_result(push_response)

    if not push_result.get("success", False):

        return {
            "success": False,
            "stage": "push",
            "repository": repository,
            "image": full_image,
            "error": push_result.get(
                "error",
                "Docker push failed",
            ),
            "build": build_result,
            "push": push_result,
        }

    print("Push completed.")

    return {
        "success": True,
        "repository": repository,
        "workspace": workspace_path,
        "image": full_image,
        "build": build_result,
        "push": push_result,
    }

# ============================================================
# COMPLETE PIPELINE
# ============================================================

async def clone_and_build(
    repository,
    branch,
    clone_url,
):

    app = await prepare_application(
        repository,
        branch,
        clone_url,
    )

    return await build_and_push(
        repository,
        app["workspace"],
    )

# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    async def test():

        result = await clone_and_build(
            repository="Afrid011/website",
            branch="master",
            clone_url="https://github.com/Afrid011/website.git",
        )

        print()
        print("=" * 60)
        print("PIPELINE RESULT")
        print("=" * 60)
        print(json.dumps(result, indent=2))

    asyncio.run(test())

