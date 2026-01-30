# Agent Hub

Agent Hub - это SDLC-агент для GitHub, который ведет задачу от Issue до PR,
прогоняет CI и запускает независимый Reviewer. Статус, логи и отчеты доступны
через API и UI. Вся интеграция построена вокруг GitHub, FastAPI и Actions.

## Ссылки

- UI: `http://89.223.121.170:8501`
- Swagger: `http://89.223.121.170:8000/docs`
- OpenAPI JSON: `http://89.223.121.170:8000/openapi.json`
Примеры:
- PR: `https://github.com/MaximIgitov/flask-sample-app/pull/2`
- Run (API): `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8`
- Логи Run: `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8/logs`
- Отчет Run: `http://89.223.121.170:8000/v1/runs/dcfa4c2c-fb83-4e46-88ab-b6e12a9d2ce8/report`

## Как это работает (по шагам)

1. В репозитории открывается Issue или ставится нужный label.
2. Workflow `Issue to PR` дергает API сервиса и создает новый Run.
3. Оркестратор запускает цепочку агентов: планирование → патчинг → PR.
4. В репозитории появляется PR с изменениями от агента.
5. Workflow `PR CI and Review` запускает линт и тесты, а затем независимого
   Reviewer, который анализирует дифф и публикует отчет.
6. В API и UI видны статусы, логи, отчет ревьюера и ссылки на артефакты.

## Технологии и зачем они здесь

- FastAPI: основной HTTP API. Через него приходят вебхуки GitHub, стартуют
  новые Run и отдаются статусы, логи и отчеты.
- Streamlit: простой UI для операторов. Показывает Runs, логи и результаты.
- GitHub App + Webhooks: принимает события `issues` и `pull_request` и дает
  серверу доступ к репозиториям, комментариям и PR.
- GitHub Actions: автоматизация. Один workflow запускает агент по Issue,
  другой гоняет CI и Reviewer на PR. Отдельный workflow отвечает за деплой.
- OpenRouter: поставщик LLM. Модель выбирается по конфигурации.
- SQLAlchemy + Postgres/SQLite: хранение Runs, статусов и метаданных.
  По умолчанию можно использовать SQLite, в проде - Postgres.
- Redis + ARQ: очередь фоновых задач и управление асинхронными джобами.
- Typer CLI: локальный запуск агента и отладка без GitHub.
- Docker Compose: единый запуск API, UI, БД и очередей.

## Вебхуки GitHub

Webhook URL: `POST /v1/webhooks/github`. Секрет задается в
`AGENT_HUB_GITHUB_WEBHOOK_SECRET`. Вебхук нужен, чтобы автоматически запускать
Run при открытии Issue и синхронизировать статусы с GitHub.

## Интеграция репозитория

В репозитории, который хотите подключить, должны быть workflows из
`.github/workflows/`. Issue workflow запускает Code Agent, PR workflow гоняет
CI и публикует артефакты ревью. Review выполняется строго после CI.

## Деплой по кнопке

Workflow `Deploy to Server` имеет `workflow_dispatch`, поэтому его можно
запустить вручную кнопкой в GitHub Actions. Также деплой происходит на push в
`master`. Внутри выполняется SSH-деплой и перезапуск `docker-compose` на сервере.

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
- `AGENT_HUB_APP_BASE_URL` — base URL для callback-ов
- `AGENT_HUB_UI_BASE_URL` — base URL для UI ссылок
- `AGENT_HUB_REVIEW_MODEL` — модель Reviewer в Actions

## GitHub App

1. Создать GitHub App и включить webhooks.
2. Webhook URL: `POST /v1/webhooks/github`.
3. Секрет: `AGENT_HUB_GITHUB_WEBHOOK_SECRET`.
4. Сгенерировать private key и сохранить.
5. Установить App на демо-репозиторий.

## CLI

```bash
agent issue run --repo https://github.com/org/repo --issue 12 --model google/gemini-3-flash-preview --max-iters 5
agent pr fix --repo https://github.com/org/repo --pr 54
agent local run --path ./repo --issue-text "Add a health endpoint"
```

## Тесты и качество

В проекте есть unit и integration тесты (`tests/unit`, `tests/integration`).
Локально и в CI используется единый набор проверок качества.

```bash
make lint   # ruff + black --check + mypy
make test   # pytest
```

CI запускается на каждом PR и включает линт, тесты и Reviewer. Отчеты ревьюера
публикуются как артефакты workflow.
