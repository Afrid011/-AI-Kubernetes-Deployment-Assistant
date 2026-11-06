import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.1:8b",
)


def clean_response(text: str) -> str:
    """
    Extract only Dockerfile content from Ollama response.
    """

    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "")

    lines = text.splitlines()

    docker_lines = []
    started = False

    for line in lines:

        stripped = line.strip()

        if not started:

            if stripped.startswith("FROM"):
                started = True
                docker_lines.append(line)

        else:
            docker_lines.append(line)

    return "\n".join(docker_lines).strip()


def detect_project(files):

    names = {
        os.path.basename(f).lower()
        for f in files
    }

    if "package.json" in names:
        return "node"

    if (
        "requirements.txt" in names
        or "pyproject.toml" in names
    ):
        return "python"

    if "pom.xml" in names:
        return "java-maven"

    if (
        "build.gradle" in names
        or "build.gradle.kts" in names
    ):
        return "java-gradle"

    if "index.html" in names:
        return "static"

    html = any(
        f.lower().endswith(".html")
        for f in names
    )

    if html:
        return "static"

    return "unknown"


def generate_dockerfile(
    project_files,
    project_path,
):

    os.makedirs(
        project_path,
        exist_ok=True,
    )

    project_type = detect_project(
        project_files
    )

    # ========================================================
    # STATIC WEBSITE
    # ========================================================

    if project_type == "static":

        dockerfile = """FROM nginx:alpine

COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx","-g","daemon off;"]
"""

    # ========================================================
    # NODE.JS
    # ========================================================

    elif project_type == "node":

        dockerfile = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["npm","start"]
"""

    # ========================================================
    # PYTHON
    # ========================================================

    elif project_type == "python":

        dockerfile = """FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python","app.py"]
"""

    # ========================================================
    # JAVA MAVEN
    # ========================================================

    elif project_type == "java-maven":

        dockerfile = """FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

COPY . .

RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080

CMD ["java","-jar","app.jar"]
"""

    # ========================================================
    # UNKNOWN -> OLLAMA
    # ========================================================

    else:

        prompt = f"""
Generate ONLY a valid Dockerfile.

Repository files:

{chr(10).join(project_files)}

Rules:
- First line MUST begin with FROM.
- No explanation.
- No markdown.
- No code fences.
- Production-ready Dockerfile.
"""

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()

        dockerfile = clean_response(
            response.json()["response"]
        )

        if not dockerfile.startswith("FROM"):
            raise RuntimeError(
                "Ollama returned an invalid Dockerfile."
            )

    dockerfile_path = os.path.join(
        project_path,
        "Dockerfile",
    )

    with open(
        dockerfile_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(dockerfile + "\n")

    return {
        "success": True,
        "project_type": project_type,
        "dockerfile": dockerfile,
        "path": dockerfile_path,
    }
