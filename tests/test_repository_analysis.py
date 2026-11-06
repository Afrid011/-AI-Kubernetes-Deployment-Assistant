import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.repository_analysis_service import (
    analyze_repository,
)

REPOSITORY = "Afrid011/website"
BRANCH = "main"


async def main():

    print()
    print("=" * 60)
    print("AI REPOSITORY ANALYSIS")
    print("=" * 60)

    print()
    print("Repository:", REPOSITORY)
    print("Branch:", BRANCH)

    print()
    print("Analyzing repository...")

    result = await analyze_repository(
        REPOSITORY,
        BRANCH,
    )

    print()
    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())

