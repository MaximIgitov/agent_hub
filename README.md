# Agent Hub

Production-minded SDLC coding agent system with GitHub integration, async FastAPI
backend, CLI, and a minimal UI.

## Quick start

```bash
docker-compose up -d
```

API is available at `http://localhost:8000/docs`. Streamlit UI runs at
`http://localhost:8501`.

## Configuration

Environment variables:

- `AGENT_HUB_OPENROUTER_API_KEY` - OpenRouter key
- `AGENT_HUB_OPENROUTER_MODEL` - Default model (e.g. `google/gemini-3-flash-preview`)
- `AGENT_HUB_AVAILABLE_MODELS` - Comma-separated model list for UI selection
- `AGENT_HUB_GITHUB_WEBHOOK_SECRET` - GitHub App webhook secret
- `AGENT_HUB_GITHUB_TOKEN` - GitHub token for Code Agent operations
- `AGENT_HUB_DATABASE_URL` - SQLAlchemy async URL
- `AGENT_HUB_REDIS_URL` - Redis URL
- `AGENT_HUB_DEFAULT_MAX_ITERS` - Default max iterations
- `AGENT_HUB_APP_BASE_URL` - Base URL for callbacks
- `AGENT_HUB_UI_BASE_URL` - Base URL for UI links
- `AGENT_HUB_REVIEW_MODEL` - Reviewer model override (Actions)

## GitHub App setup (summary)

1. Create a GitHub App and enable webhooks.
2. Set webhook URL to `POST /v1/webhooks/github`.
3. Store webhook secret in `AGENT_HUB__GITHUB_WEBHOOK_SECRET`.
4. Generate a private key and store it securely.
5. Install the app on the demo repo.

## Demo repo wiring

Add workflows from `.github/workflows/` to the target repo. The issue workflow can
notify the backend or run the CLI container. The PR workflow runs CI and uploads
artifacts for review. Review happens only after CI completes.

## Reports

- API run report: `GET /v1/runs/{run_id}/report`
- Run logs: `GET /v1/runs/{run_id}/logs`
- CI/Review artifacts: `report.md` and `verdict.json` in GitHub Actions

## Sample issue pack

Create 3-5 issues in the demo repo (small features + bug fixes), then run:

```bash
python -m cli issue run --repo https://github.com/org/repo --issue 12 --model google/gemini-3-flash-preview --max-iters 5
```

Generate a run report from API logs and artifacts.

## CLI usage

```bash
agent issue run --repo https://github.com/org/repo --issue 12 --model google/gemini-3-flash-preview --max-iters 5
agent pr fix --repo https://github.com/org/repo --pr 54
agent local run --path ./repo --issue-text "Add a health endpoint"
```

## Tests

```bash
make lint
make test
```
