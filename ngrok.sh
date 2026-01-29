#!/usr/bin/env bash
set -euo pipefail

if ! command -v ngrok >/dev/null 2>&1; then
  echo "ngrok not found. Install it and ensure it's in PATH."
  exit 1
fi

ngrok http 8000 >/dev/null 2>&1 &
NGROK_PID=$!

cleanup() {
  kill "$NGROK_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in {1..20}; do
  sleep 0.5
  if curl -sf http://127.0.0.1:4040/api/tunnels >/tmp/ngrok_tunnels.json; then
    break
  fi
done

URL=$(python - <<'PY'
import json, sys
try:
    data = json.load(open("/tmp/ngrok_tunnels.json", "r", encoding="utf-8"))
except Exception:
    print("")
    raise SystemExit(0)
for t in data.get("tunnels", []):
    if t.get("proto") == "https":
        print(t.get("public_url", ""))
        break
PY
)

if [ -z "$URL" ]; then
  echo "Failed to detect ngrok URL. Open http://127.0.0.1:4040 and copy it manually."
  wait "$NGROK_PID"
  exit 1
fi

echo "Webhook URL: ${URL}/v1/webhooks/github"
echo "Press Ctrl+C to stop ngrok."

wait "$NGROK_PID"
