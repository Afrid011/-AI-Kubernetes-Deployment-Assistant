import json

IMPORTANT_FILES = [
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "package.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "manage.py",
    "README.md",
]


def detect_application(files):

    names = {
        item["name"]
        for item in files
    }

    result = {
        "application_type": "Unknown",
        "build_tool": "Unknown",
        "dockerfile": False,
        "docker_compose": False,
        "kubernetes": False,
    }

    if "package.json" in names:

        result["application_type"] = "Node.js"
        result["build_tool"] = "npm"

    elif "pom.xml" in names:

        result["application_type"] = "Java"
        result["build_tool"] = "Maven"

    elif (
        "build.gradle" in names
        or
        "build.gradle.kts" in names
    ):

        result["application_type"] = "Java"
        result["build_tool"] = "Gradle"

    elif (
        "requirements.txt" in names
        or
        "pyproject.toml" in names
    ):

        result["application_type"] = "Python"
        result["build_tool"] = "pip"

    elif "go.mod" in names:

        result["application_type"] = "Go"
        result["build_tool"] = "Go"

    elif "Cargo.toml" in names:

        result["application_type"] = "Rust"
        result["build_tool"] = "Cargo"

    result["dockerfile"] = (
        "Dockerfile" in names
    )

    result["docker_compose"] = (
        "docker-compose.yml" in names
        or
        "docker-compose.yaml" in names
    )

    result["kubernetes"] = any(
        "deployment" in item["name"].lower()
        or
        "service" in item["name"].lower()
        for item in files
    )

    return result
