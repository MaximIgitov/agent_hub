from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re

import httpx

from config import settings
from github.client import GitHubClient
from github.permissions_policy import REVIEW_POLICY
from llm.openrouter import OpenRouterClient


def parse_repo(repo_full: str) -> tuple[str, str]:
    parts = repo_full.split("/")
    if len(parts) != 2:
        return "", ""
    return parts[0], parts[1]


def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return {}


def extract_issue_number(text: str) -> int:
    match = re.search(r"issue\\s+#(\\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def build_prompt(pr: dict, files: list[dict], ci_summary: str) -> str:
    patches = []
    for file in files:
        filename = file.get("filename", "")
        patch = file.get("patch", "")
        if patch:
            patch = patch[:1500]
        patches.append(f"File: {filename}\n{patch}")
    diff_block = "\n\n".join(patches[:20])
    return (
        "You are a senior reviewer. Analyze the PR against the issue requirements.\n"
        "Return a JSON object with keys: verdict (approve/comment/request_changes), "
        "summary, issues (list), risks (list), required_changes (list).\n"
        "Be concise.\n\n"
        f"PR title: {pr.get('title','')}\n"
        f"PR body:\n{pr.get('body','')}\n\n"
        f"CI summary:\n{ci_summary}\n\n"
        f"Diffs:\n{diff_block}\n"
    )


async def main() -> None:
    token = os.getenv("GITHUB_TOKEN", "")
    repo_full = os.getenv("GITHUB_REPOSITORY", "")
    pr_number = int(os.getenv("PR_NUMBER", "0") or "0")
    if not token or not repo_full or pr_number <= 0:
        print("Missing GITHUB_TOKEN, GITHUB_REPOSITORY or PR_NUMBER.")
        return

    owner, repo = parse_repo(repo_full)
    if not owner or not repo:
        print("Invalid GITHUB_REPOSITORY format.")
        return

    if not settings.openrouter_api_key:
        print("Missing AGENT_HUB_OPENROUTER_API_KEY.")
        return

    github = GitHubClient(token=token, policy=REVIEW_POLICY)
    pr = await github.get_pull_request(owner, repo, pr_number)
    files = await github.list_pull_files(owner, repo, pr_number)

    report_path = Path("report.md")
    ci_summary = (
        report_path.read_text(encoding="utf-8")
        if report_path.exists()
        else "CI summary not available in workspace."
    )

    llm = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=os.getenv("AGENT_HUB_REVIEW_MODEL", settings.openrouter_model),
    )
    prompt = build_prompt(pr, files, ci_summary)
    response = await llm.complete(prompt, correlation_id=str(pr_number))
    verdict = extract_json(response.content) or {
        "verdict": "comment",
        "summary": "Reviewer output could not be parsed.",
        "issues": [],
        "risks": [],
        "required_changes": [],
    }

    summary = verdict.get("summary", "")
    issues = verdict.get("issues", [])
    risks = verdict.get("risks", [])
    required = verdict.get("required_changes", [])
    verdict_label = verdict.get("verdict", "comment")

    report = [
        "# Review Summary",
        f"- verdict: {verdict_label}",
        f"- summary: {summary}",
        "",
        "## Issues",
        "\n".join(f"- {item}" for item in issues) or "- none",
        "",
        "## Risks",
        "\n".join(f"- {item}" for item in risks) or "- none",
        "",
        "## Required changes",
        "\n".join(f"- {item}" for item in required) or "- none",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    Path("verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    comment_body = "\n".join(report)
    await github.create_comment(pr.get("comments_url", ""), comment_body)

    event = "COMMENT"
    if verdict_label == "approve":
        event = "APPROVE"
    elif verdict_label == "request_changes":
        event = "REQUEST_CHANGES"
    reviews_url = f"{pr.get('url', '')}/reviews"
    await github.create_review(reviews_url, comment_body, event)

    if verdict_label == "request_changes":
        agent_hub_url = os.getenv("AGENT_HUB_URL", "").rstrip("/")
        issue_number = extract_issue_number(pr.get("body", "")) or pr_number
        repo_url = pr.get("base", {}).get("repo", {}).get("html_url", "")
        if agent_hub_url and repo_url and issue_number > 0:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"{agent_hub_url}/v1/runs/issue/retry",
                    json={"repo_url": repo_url, "issue_number": issue_number},
                )


if __name__ == "__main__":
    asyncio.run(main())
