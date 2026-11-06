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

from services.kubernetes_service import (
    list_namespaces,
    get_pods,
)

# ============================================================
# TEST
# ============================================================

print("=" * 60)
print("KUBERNETES SERVICE TEST")
print("=" * 60)

try:
    print("\nNamespaces:\n")
    print(list_namespaces())

    print("\nWebsite pods:\n")
    print(
        get_pods(
            "website",
            "ai-deployments",
        )
    )

except Exception as e:
    print("\nERROR")
    print("=" * 60)
    print(e)


