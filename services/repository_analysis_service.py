import json

from services.mcp_client import (
    call_github_tool
)

from services.repository_analyzer import (
    detect_application
)

from services.ai_analyzer import (
    analyze_with_ai
)


def _extract_result(result):

    for item in result.content:

        if hasattr(item, "text"):

            return json.loads(
                item.text
            )

    return None


async def analyze_repository(
    repository,
    branch
):

    # -----------------------------------------
    # Get repository files
    # -----------------------------------------

    result = await call_github_tool(
        "list_files",
        {
            "repository": repository,
            "path": ""
        }
    )

    files = _extract_result(
        result
    )

    # -----------------------------------------
    # Deterministic analysis
    # -----------------------------------------

    facts = detect_application(
        files
    )

    # -----------------------------------------
    # AI analysis
    # -----------------------------------------

    ai_result = analyze_with_ai(
        repository,
        branch,
        facts,
        files,
    )

    return {
        "repository": repository,
        "branch": branch,
        "facts": facts,
        "ai_analysis": ai_result,
    }

