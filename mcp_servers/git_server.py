import asyncio
import os
import shutil
import subprocess

from fastmcp import FastMCP

# ============================================================
# MCP SERVER
# ============================================================

server = FastMCP("Git MCP Server")

# ============================================================
# CONFIGURATION
# ============================================================

WORKSPACE = "/root/ai-k8s-workspaces"

# ============================================================
# HELPER FUNCTION
# ============================================================

def run_command(command, cwd=None):
    """
    Run a shell command and return stdout.
    """

    process = subprocess.run(
        command,
        cwd=cwd,
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
async def clone_repository(
    clone_url: str,
    repository_name: str,
    branch: str = "main",
) -> dict:
    """
    Clone a GitHub repository into the AI Kubernetes Assistant workspace.
    """

    os.makedirs(WORKSPACE, exist_ok=True)

    target = os.path.join(WORKSPACE, repository_name)

    if os.path.exists(target):
        shutil.rmtree(target)

    run_command(
        [
            "git",
            "clone",
            "--branch",
            branch,
            "--single-branch",
            clone_url,
            target,
        ]
    )

    return {
        "success": True,
        "repository": repository_name,
        "branch": branch,
        "path": target,
    }


@server.tool
async def repository_status(repository_name: str) -> dict:
    """
    Get Git status for a cloned repository.
    """

    repo_path = os.path.join(WORKSPACE, repository_name)

    if not os.path.exists(repo_path):
        raise RuntimeError(f"Repository '{repository_name}' not found.")

    status = run_command(["git", "status", "--short"], cwd=repo_path)

    return {
        "repository": repository_name,
        "path": repo_path,
        "status": status.splitlines() if status else [],
    }


@server.tool
async def current_branch(repository_name: str) -> str:
    """
    Return the current Git branch.
    """

    repo_path = os.path.join(WORKSPACE, repository_name)

    if not os.path.exists(repo_path):
        raise RuntimeError(f"Repository '{repository_name}' not found.")

    return run_command(
        ["git", "branch", "--show-current"],
        cwd=repo_path,
    )

# ============================================================
# MAIN
# ============================================================

async def main():
    await server.run_async(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())

