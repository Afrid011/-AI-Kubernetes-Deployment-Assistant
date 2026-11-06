
import sys
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

from services.deployment_service import (
    deploy_to_kubernetes,
)

# ============================================================
# TEST CONFIGURATION
# ============================================================

IMAGE = "trainerreyaz/website:latest"
APP_NAME = "website"
NAMESPACE = "ai-deployments"
REPLICAS = 2
CONTAINER_PORT = 80

# ============================================================
# RUN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("KUBERNETES DEPLOYMENT TEST")
    print("=" * 60)

    try:

        result = deploy_to_kubernetes(
            image=IMAGE,
            app_name=APP_NAME,
            namespace=NAMESPACE,
            replicas=REPLICAS,
            container_port=CONTAINER_PORT,
        )

        print()
        print("=" * 60)
        print("DEPLOYMENT RESULT")
        print("=" * 60)

        for key, value in result.items():

            print(f"\n===== {key.upper()} =====")

            if isinstance(value, (dict, list)):
                import json
                print(json.dumps(value, indent=2))
            else:
                print(value)

    except Exception as e:

        print()
        print("=" * 60)
        print("DEPLOYMENT FAILED")
        print("=" * 60)
        print(f"Error: {e}")
