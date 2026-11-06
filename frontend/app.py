import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

# ============================================================
# PYTHON PATH FIX
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# SERVICES
# ============================================================

from services.github_service import (
    list_repositories,
    list_branches,
)

from services.repository_analysis_service import (
    analyze_repository,
)

from services.deployment_orchestrator import (
    clone_and_build,
)

from services.deployment_service import (
    deploy_to_kubernetes,
)

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Kubernetes Deployment Assistant",
    page_icon="☸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .hero{
        padding:28px;
        border-radius:18px;
        background:linear-gradient(135deg,#0f172a,#1d4ed8);
        color:white;
        margin-bottom:20px;
    }

    .section{
        border:1px solid #dcdcdc;
        border-radius:14px;
        padding:18px;
        margin-bottom:20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FIXED ASYNC RUNNER
# ============================================================


def run_async(coro):
    """
    Safely execute async code inside Streamlit.
    """

    try:
        asyncio.get_running_loop()

        with ThreadPoolExecutor(max_workers=1) as executor:

            future = executor.submit(
                asyncio.run,
                coro,
            )

            return future.result()

    except RuntimeError:

        return asyncio.run(coro)


# ============================================================
# HELPERS
# ============================================================


def parse_mcp_response(result):

    parsed = []

    if not hasattr(result, "content"):
        return parsed

    for item in result.content:

        if hasattr(item, "text"):

            try:

                data = json.loads(item.text)

                if isinstance(data, list):
                    parsed.extend(data)
                else:
                    parsed.append(data)

            except Exception:

                parsed.append(item.text)

    return parsed


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("☸️ AI K8s Assistant")

    st.markdown("---")

    st.success("GitHub")
    st.success("Docker")
    st.success("Ollama")
    st.success("Kubernetes")

    st.markdown("---")

    st.write("**Provider:** AWS")
    st.write("**Cluster:** Kops")

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

    <h1>☸️ AI Kubernetes Deployment Assistant</h1>

    <p>GitHub → AI → Docker → Kubernetes</p>

    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

m1.metric("GitHub", "Connected")
m2.metric("Docker", "Ready")
m3.metric("Ollama", "llama3.1")
m4.metric("Kubernetes", "Ready")

# ============================================================
# LOAD REPOSITORIES
# ============================================================

if "repositories" not in st.session_state:

    try:

        st.session_state.repositories = parse_mcp_response(
            list_repositories()
        )

    except Exception as e:

        st.session_state.repositories = []

        st.error(e)

repositories = st.session_state.repositories

# ============================================================
# REPOSITORY
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("1️⃣ Select Repository")

repository = st.selectbox(
    "GitHub Repository",
    ["Select repository"] +
    [
        repo["full_name"]
        for repo in repositories
    ]
)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# BRANCH
# ============================================================

branch = "main"

if repository != "Select repository":

    try:

        branches = parse_mcp_response(
            list_branches(repository)
        )

        if branches:

            branch = st.selectbox(
                "Branch",
                branches,
            )

    except Exception:
        pass

# ============================================================
# ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("2️⃣ Repository Analysis")

if st.button(
    "Analyze Repository",
    use_container_width=True,
):

    if repository == "Select repository":

        st.error("Select a repository first.")

    else:

        with st.spinner("Analyzing repository..."):

            st.session_state.analysis = run_async(
                analyze_repository(
                    repository,
                    branch,
                )
            )

if "analysis" in st.session_state:

    analysis = st.session_state.analysis

    facts = analysis["facts"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Application",
        facts["application_type"],
    )

    c2.metric(
        "Build Tool",
        facts["build_tool"],
    )

    c3.metric(
        "Dockerfile",
        "Yes" if facts["dockerfile"] else "No",
    )

    c4.metric(
        "Kubernetes",
        "Yes" if facts["kubernetes"] else "No",
    )

    st.markdown("### AI Analysis")

    ai = analysis["ai_analysis"]

    try:

        st.json(json.loads(ai))

    except Exception:

        st.code(ai)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# BUILD
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("3️⃣ Clone → Generate Dockerfile → Build → Push")

if st.button(
    "Run Deployment Pipeline",
    use_container_width=True,
    type="primary",
):

    if repository == "Select repository":

        st.error("Select a repository first.")

    else:

        clone_url = f"https://github.com/{repository}.git"

        progress = st.progress(0)

        status = st.empty()

        status.info("Running pipeline...")

        progress.progress(25)

        try:

            st.session_state.docker_result = run_async(
                clone_and_build(
                    repository,
                    branch,
                    clone_url,
                )
            )

            progress.progress(100)

            status.success("Pipeline completed.")

        except Exception as e:

            status.error("Pipeline failed.")

            st.exception(e)

if "docker_result" in st.session_state:

    docker = st.session_state.docker_result

    if docker.get("success"):

        st.success("Docker image built successfully.")

        st.code(docker["image"])

    else:

        st.error(docker.get("error"))

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# KUBERNETES
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("4️⃣ Kubernetes Deployment")

docker = st.session_state.get(
    "docker_result",
    {},
)

if docker.get("success"):

    image = docker["image"]

    app_name = st.text_input(
        "Application Name",
        repository.split("/")[-1],
    )

    namespace = st.text_input(
        "Namespace",
        "ai-deployments",
    )

    replicas = st.number_input(
        "Replicas",
        1,
        10,
        2,
    )

    container_port = st.number_input(
        "Container Port",
        1,
        65535,
        80,
    )

    if st.button(
        "Deploy to Kubernetes",
        use_container_width=True,
        type="primary",
    ):

        with st.spinner("Deploying..."):

            st.session_state.k8s = deploy_to_kubernetes(
                image=image,
                app_name=app_name,
                namespace=namespace,
                replicas=int(replicas),
                container_port=int(container_port),
            )

else:

    st.info("Complete the Docker build first.")

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# RESULTS
# ============================================================

if "k8s" in st.session_state:

    result = st.session_state.k8s

    if result.get("error"):

        st.error(result["error"])

    else:

        st.success("Application deployed successfully.")

        tabs = st.tabs(
            [
                "Deployment",
                "Service",
                "Pods",
                "Status",
                "URL",
            ]
        )

        with tabs[0]:
            st.code(str(result.get("deployment")))

        with tabs[1]:
            st.code(str(result.get("service")))

        with tabs[2]:
            st.code(str(result.get("pods")))

        with tabs[3]:
            st.code(str(result.get("status")))

        with tabs[4]:

            if result.get("url"):

                st.success(result["url"])

                st.link_button(
                    "Open Application",
                    result["url"],
                )

            else:

                st.info("Waiting for LoadBalancer...")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    f"AI Kubernetes Deployment Assistant | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

