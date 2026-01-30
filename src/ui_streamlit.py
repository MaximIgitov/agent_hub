from __future__ import annotations

import os

import streamlit as st

from config import settings
from services.api_client import AgentHubApiClient

API_URL = os.getenv("AGENT_HUB_UI_API_URL", "http://localhost:8000")


st.set_page_config(page_title="Agent Hub", layout="wide")
st.title("Agent Hub")

models = settings.available_models or [settings.openrouter_model]
default_model_index = 0
if settings.openrouter_model in models:
    default_model_index = models.index(settings.openrouter_model)


with st.sidebar:
    st.subheader("Create run")
    repo_url = st.text_input("Repo URL", value="")
    issue_number = st.number_input("Issue number", min_value=1, step=1, value=1)
    model = st.selectbox("Model", options=models, index=default_model_index)
    max_iters = st.number_input(
        "Max iterations",
        min_value=1,
        step=1,
        value=settings.default_max_iters,
    )
    if st.button("Run"):
        if not repo_url.strip():
            st.warning("Repo URL is required.")
        else:
            try:
                client = AgentHubApiClient(base_url=API_URL)
                run = client.create_run(
                    {
                        "repo_url": repo_url.strip(),
                        "issue_number": int(issue_number),
                        "model": model,
                        "max_iters": int(max_iters),
                    }
                )
                st.success(f"Run created: {run.get('run_id')}")
            except Exception as exc:
                st.error(f"Failed to create run: {exc}")


def fetch_runs() -> list[dict]:
    try:
        client = AgentHubApiClient(base_url=API_URL)
        return client.list_runs()
    except Exception:
        return []

def fetch_logs(run_id: str) -> dict:
    try:
        client = AgentHubApiClient(base_url=API_URL)
        return client.get_run_logs(run_id)
    except Exception:
        return {"logs": []}

runs = fetch_runs()
st.subheader("Runs")
if not runs:
    st.info("No runs yet.")
else:
    st.dataframe(runs, use_container_width=True)
    run_ids = [run["run_id"] for run in runs]
    selected = st.selectbox("Run details", run_ids)
    if selected:
        logs = fetch_logs(selected).get("logs", [])
        st.subheader("Trajectory logs")
        if logs:
            st.dataframe(logs, use_container_width=True)
        else:
            st.info("No logs yet.")
