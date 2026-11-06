#!/usr/bin/env python3

import shutil
import subprocess
from importlib.metadata import version


def command_exists(command):
    return shutil.which(command) is not None


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return result.stdout.strip()

        return result.stderr.strip()

    except Exception as e:
        return str(e)


print("=" * 50)
print("AI KUBERNETES ASSISTANT")
print("ENVIRONMENT CHECK")
print("=" * 50)


# --------------------------------------------------
# Python
# --------------------------------------------------

print("\nPython")

python_path = shutil.which("python")

if python_path:
    print(f"  PATH: {python_path}")
    print(f"  VERSION: {run_command('python --version')}")
else:
    print("  FAILED")


# --------------------------------------------------
# Git
# --------------------------------------------------

print("\nGit")

if command_exists("git"):
    print(f"  PATH: {shutil.which('git')}")
    print(f"  VERSION: {run_command('git --version')}")
else:
    print("  FAILED")


# --------------------------------------------------
# Docker
# --------------------------------------------------

print("\nDocker")

if command_exists("docker"):
    print(f"  PATH: {shutil.which('docker')}")
    print(f"  VERSION: {run_command('docker --version')}")

    print("\nDocker containers:")
    print(run_command("docker ps"))

else:
    print("  FAILED")


# --------------------------------------------------
# kubectl
# --------------------------------------------------

print("\nkubectl")

if command_exists("kubectl"):
    print(f"  PATH: {shutil.which('kubectl')}")
    print(f"  VERSION: {run_command('kubectl version --client --output=yaml | head -20')}")

else:
    print("  FAILED")


# --------------------------------------------------
# Kubernetes
# --------------------------------------------------

print("\nKubernetes nodes:")

if command_exists("kubectl"):
    print(run_command("kubectl get nodes"))

    print("\nKubernetes namespaces:")
    print(run_command("kubectl get namespaces"))

else:
    print("kubectl not available")


# --------------------------------------------------
# Ollama
# --------------------------------------------------

print("\nOllama")

if command_exists("ollama"):
    print(f"  PATH: {shutil.which('ollama')}")
    print(f"  VERSION: {run_command('ollama --version')}")

    print("\nOllama models:")
    print(run_command("ollama list"))

else:
    print("  FAILED")


# --------------------------------------------------
# MCP
# --------------------------------------------------

print("\nMCP")

try:

    mcp_version = version("mcp")

    print(f"  MCP SDK VERSION: {mcp_version}")

    from mcp.server import MCPServer

    print("  MCPServer: OK")

    from mcp import ClientSession

    print("  ClientSession: OK")

except Exception as e:

    print(f"  MCP SDK: FAILED - {e}")


# --------------------------------------------------
# FastMCP check
# --------------------------------------------------

print("\nMCP API")

try:

    from mcp.server.fastmcp import FastMCP

    print("  FastMCP: AVAILABLE")

except ModuleNotFoundError:

    print("  FastMCP: NOT USED (MCP 2.x API)")

except Exception as e:

    print(f"  FastMCP check: {e}")


print("\n" + "=" * 50)
print("ENVIRONMENT CHECK COMPLETE")
print("=" * 50)
