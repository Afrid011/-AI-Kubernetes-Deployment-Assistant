import sys
import time
from pathlib import Path

# ============================================================
# FIX PYTHON IMPORT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# IMPORTS
# ============================================================

from services.kubernetes_service import (
    deploy_application,
    create_loadbalancer,
    get_deployment_status,
    get_pods,
    get_application_url,
)

# ============================================================
# DEPLOYMENT ORCHESTRATOR
# ============================================================

def deploy_to_kubernetes(
    image,
    app_name,
    namespace,
    replicas=2,
    container_port=80,
    wait_seconds=30,
):

    result = {
        "success": False,
        "deployment": None,
        "service": None,
        "status": None,
        "pods": None,
        "url": None,
        "error": None,
    }

    try:

        print("=" * 60)
        print("KUBERNETES DEPLOYMENT")
        print("=" * 60)

        print(f"Application : {app_name}")
        print(f"Image       : {image}")
        print(f"Namespace   : {namespace}")
        print(f"Replicas    : {replicas}")
        print()

        # ----------------------------------------------------
        # STEP 1 - Deployment
        # ----------------------------------------------------

        print("Creating deployment...")

        result["deployment"] = deploy_application(
            name=app_name,
            image=image,
            namespace=namespace,
            replicas=replicas,
            container_port=container_port,
        )

        # ----------------------------------------------------
        # STEP 2 - Service
        # ----------------------------------------------------

        print("Creating LoadBalancer service...")

        result["service"] = create_loadbalancer(
            name=app_name,
            namespace=namespace,
            port=80,
            target_port=container_port,
        )

        # ----------------------------------------------------
        # STEP 3 - Wait briefly
        # ----------------------------------------------------

        print(f"Waiting {wait_seconds} seconds for rollout...")

        time.sleep(wait_seconds)

        # ----------------------------------------------------
        # STEP 4 - Deployment Status
        # ----------------------------------------------------

        result["status"] = get_deployment_status(
            name=app_name,
            namespace=namespace,
        )

        # ----------------------------------------------------
        # STEP 5 - Pods
        # ----------------------------------------------------

        result["pods"] = get_pods(
            name=app_name,
            namespace=namespace,
        )

        # ----------------------------------------------------
        # STEP 6 - Application URL
        # ----------------------------------------------------

        result["url"] = get_application_url(
            name=app_name,
            namespace=namespace,
        )

        result["success"] = True

        return result

    except Exception as exc:

        result["error"] = str(exc)

        return result


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    deployment = deploy_to_kubernetes(
        image="nginx:latest",
        app_name="website",
        namespace="ai-deployments",
        replicas=2,
        container_port=80,
    )

    print()
    print("=" * 60)
    print("DEPLOYMENT RESULT")
    print("=" * 60)

    print(deployment)

