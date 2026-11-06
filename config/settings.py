import os
from dotenv import load_dotenv

load_dotenv()


OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.1:8b"
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
)

GITHUB_USERNAME = os.getenv(
    "GITHUB_USERNAME",
    ""
)

DOCKERHUB_USERNAME = os.getenv(
    "DOCKERHUB_USERNAME",
    ""
)

DOCKERHUB_TOKEN = os.getenv(
    "DOCKERHUB_TOKEN",
    ""
)

KUBECONFIG = os.getenv(
    "KUBECONFIG",
    os.path.expanduser("~/.kube/config")
)

K8S_NAMESPACE = os.getenv(
    "K8S_NAMESPACE",
    "default"
)
