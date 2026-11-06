import json

from services.ollama_service import (
    ask_ollama
)


def analyze_with_ai(
    repository,
    branch,
    facts,
    files,
):

    prompt = f"""
You are a senior DevOps engineer.

Analyze the following GitHub repository.

Repository:
{repository}

Branch:
{branch}

Repository facts:
{json.dumps(facts, indent=2)}

Files:
{json.dumps(files, indent=2)}

Determine:

1. Application type
2. Programming language
3. Framework
4. Build tool
5. Whether a Dockerfile exists
6. Whether Kubernetes manifests exist
7. Likely application port
8. Recommended Docker strategy
9. Recommended Kubernetes deployment strategy

Return ONLY valid JSON.

Use this structure:

{{
    "application_type": "",
    "language": "",
    "framework": "",
    "build_tool": "",
    "dockerfile": true,
    "kubernetes_manifests": false,
    "application_port": 8080,
    "docker_strategy": "",
    "kubernetes_strategy": "",
    "recommendation": ""
}}
"""

    response = ask_ollama(
        prompt
    )

    return response
