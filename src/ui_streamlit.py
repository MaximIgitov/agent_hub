from __future__ import annotations

import os

import streamlit as st

from services.api_client import AgentHubApiClient

API_URL = os.getenv("AGENT_HUB_UI_API_URL", "http://localhost:8000")


st.set_page_config(page_title="Agent Hub", layout="wide")
st.title("Agent Hub")


def fetch_runs() -> list[dict]:
    try:
        client = AgentHubApiClient(base_url=API_URL)
        return client.list_runs()
    except Exception:
        return []


runs = fetch_runs()
st.subheader("Runs")
if not runs:
    st.info("No runs yet.")
else:
    st.dataframe(runs, use_container_width=True)
