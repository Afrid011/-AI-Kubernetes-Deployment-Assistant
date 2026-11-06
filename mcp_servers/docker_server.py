import asyncio
import json
import subprocess

from fastmcp import FastMCP

# ============================================================
# MCP SERVER
# ============================================================

server = FastMCP("Docker MCP Server")


# ============================================================
# HELPER FUNCTION
# ============================================================

def run_command(command: list[str]) -> str:
    """Run a shell command and return stdout."""

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip())

    return process.stdout.strip()


# ============================================================
# MCP TOOLS
# ============================================================

@server.tool
async def docker_version() -> str:
    """
    Return Docker version.
    """
    return run_command(["docker", "--version"])


@server.tool
async def list_images() -> list:
    """
    List Docker images available locally.
    """

    output = run_command(
        [
            "docker",
            "images",
            "--format",
            "{{json .}}",
        ]
    )

    images = []

    if not output:
        return images

    for line in output.splitlines():
        images.append(json.loads(line))

    return images


@server.tool
async def list_containers() -> list:
    """
    List running Docker containers.
    """

    output = run_command(
        [
            "docker",
            "ps",
            "--format",
            "{{json .}}",
        ]
    )

    containers = []

    if not output:
        return containers

    for line in output.splitlines():
        containers.append(json.loads(line))

    return containers

@server.tool()
async def build_image(
    context_path: str,
    image_name: str,
    tag: str = "latest"
):
    """
    Build a Docker image from a build context.
    """

    full_image = (
        f"{image_name}:{tag}"
    )

    command = [
        "docker",
        "build",
        "-t",
        full_image,
        context_path,
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:

        return {
            "success": False,
            "image": full_image,
            "output": process.stdout,
            "error": process.stderr,
        }

    return {
        "success": True,
        "image": full_image,
        "output": process.stdout,
    }
@server.tool()
async def push_image(
    image_name: str,
    tag: str = "latest"
):
    """
    Push a Docker image to Docker Hub.
    """

    full_image = f"{image_name}:{tag}"

    process = subprocess.run(
        [
            "docker",
            "push",
            full_image
        ],
        capture_output=True,
        text=True
    )

    if process.returncode != 0:

        return {
            "success": False,
            "image": full_image,
            "output": process.stdout,
            "error": process.stderr,
        }

    return {
        "success": True,
        "image": full_image,
        "output": process.stdout,
    }
# ============================================================
# MAIN
# ============================================================

async def main():
    await server.run_async(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())


