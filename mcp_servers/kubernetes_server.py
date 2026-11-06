import asyncio
import json
import subprocess

from fastmcp import FastMCP

# ============================================================
# MCP SERVER
# ============================================================

server = FastMCP("kubernetes-mcp")

# ============================================================
# HELPER
# ============================================================

def run_kubectl(args):
    result = subprocess.run(
        ["kubectl"] + args,
        capture_output=True,
        text=True,
    )
    return result


# ============================================================
# TOOL: LIST NAMESPACES
# ============================================================

@server.tool
async def list_namespaces():
    """List Kubernetes namespaces."""

    result = run_kubectl(["get", "namespaces", "-o", "json"])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    data = json.loads(result.stdout)

    return [
        item["metadata"]["name"]
        for item in data["items"]
    ]


# ============================================================
# TOOL: DEPLOY APPLICATION
# ============================================================

@server.tool
async def deploy_application(
    name: str,
    image: str,
    namespace: str,
    replicas: int,
    container_port: int,
):
    """Deploy a Docker image to Kubernetes."""

    run_kubectl(["create", "namespace", namespace])

    deployment = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {namespace}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: {name}
        image: {image}
        imagePullPolicy: Always
        ports:
        - containerPort: {container_port}
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
"""

    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=deployment,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


# ============================================================
# TOOL: GET DEPLOYMENT STATUS
# ============================================================

@server.tool
async def get_deployment_status(
    name: str,
    namespace: str,
):
    """Get Kubernetes deployment status."""

    result = run_kubectl([
        "get",
        "deployment",
        name,
        "-n",
        namespace,
        "-o",
        "json",
    ])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    data = json.loads(result.stdout)

    return data.get("status", {})


# ============================================================
# TOOL: GET PODS
# ============================================================

@server.tool
async def get_pods(
    name: str,
    namespace: str,
):
    """Get pods for an application."""

    result = run_kubectl([
        "get",
        "pods",
        "-n",
        namespace,
        "-l",
        f"app={name}",
        "-o",
        "wide",
    ])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


# ============================================================
# TOOL: CREATE LOADBALANCER
# ============================================================

@server.tool
async def create_loadbalancer(
    name: str,
    namespace: str,
    port: int,
    target_port: int,
):
    """Create a Kubernetes LoadBalancer service."""

    service = f"""
apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {namespace}
spec:
  type: LoadBalancer
  selector:
    app: {name}
  ports:
  - name: http
    port: {port}
    targetPort: {target_port}
    protocol: TCP
"""

    result = subprocess.run(
        ["kubectl", "apply", "-f", "-"],
        input=service,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


# ============================================================
# TOOL: GET SERVICE
# ============================================================

@server.tool
async def get_service(
    name: str,
    namespace: str,
):
    """Get Kubernetes service information."""

    result = run_kubectl([
        "get",
        "service",
        name,
        "-n",
        namespace,
        "-o",
        "json",
    ])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return json.loads(result.stdout)


# ============================================================
# TOOL: GET APPLICATION URL
# ============================================================

@server.tool
async def get_application_url(
    name: str,
    namespace: str,
):
    """Get the external LoadBalancer URL."""

    result = run_kubectl([
        "get",
        "service",
        name,
        "-n",
        namespace,
        "-o",
        "json",
    ])

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    data = json.loads(result.stdout)

    ingress = (
        data.get("status", {})
            .get("loadBalancer", {})
            .get("ingress", [])
    )

    if not ingress:
        return "LoadBalancer is still provisioning."

    item = ingress[0]

    address = item.get("hostname") or item.get("ip")

    return f"http://{address}"


# ============================================================
# MAIN
# ============================================================

async def main():
    await server.run_async(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main())

