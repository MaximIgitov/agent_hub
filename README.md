# Agent Hub

Система SDLC‑агента для GitHub: Issue → план → патч → PR → CI → независимый
Reviewer → статус и логи в API и UI. Все взаимодействия через GitHub и FastAPI.

## Демо (живые ссылки)

- UI: `http://89.223.121.170:8501`
- Swagger: `http://89.223.121.170:8000/docs`
- OpenAPI JSON: `http://89.223.121.170:8000/openapi.json`
- PR демо: `https://github.com/MaximIgitov/flask-sample-app/pull/2`
- Run (API): `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8`
- Логи Run: `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8/logs`
- Отчёт Run: `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8/report`

## Быстрый старт

```bash
docker-compose up -d
```

API по умолчанию: `http://localhost:8000/docs`, UI: `http://localhost:8501`.

## Конфигурация

Переменные окружения:

- `AGENT_HUB_OPENROUTER_API_KEY` — ключ OpenRouter
- `AGENT_HUB_OPENROUTER_MODEL` — модель по умолчанию
- `AGENT_HUB_AVAILABLE_MODELS` — список моделей для UI
- `AGENT_HUB_GITHUB_WEBHOOK_SECRET` — секрет вебхуков GitHub App
- `AGENT_HUB_GITHUB_TOKEN` — токен для Code Agent
- `AGENT_HUB_DATABASE_URL` — SQLAlchemy async URL
- `AGENT_HUB_REDIS_URL` — Redis URL
- `AGENT_HUB_DEFAULT_MAX_ITERS` — лимит итераций
- `AGENT_HUB_APP_BASE_URL` — base URL для callback’ов
- `AGENT_HUB_UI_BASE_URL` — base URL для UI ссылок
- `AGENT_HUB_REVIEW_MODEL` — модель Reviewer в Actions

## GitHub App (кратко)

1. Создать GitHub App и включить webhooks.
2. Webhook URL: `POST /v1/webhooks/github`.
3. Секрет: `AGENT_HUB_GITHUB_WEBHOOK_SECRET`.
4. Сгенерировать private key и сохранить.
5. Установить App на демо‑репозиторий.

## Интеграция репозитория

Подключить workflow из `.github/workflows/`. Issue workflow запускает Code Agent,
PR workflow гоняет CI и публикует артефакты ревью. Review выполняется строго после CI.

## CLI

```bash
agent issue run --repo https://github.com/org/repo --issue 12 --model google/gemini-3-flash-preview --max-iters 5
agent pr fix --repo https://github.com/org/repo --pr 54
agent local run --path ./repo --issue-text "Add a health endpoint"
```

## Тесты

```bash
make lint
make test
```
