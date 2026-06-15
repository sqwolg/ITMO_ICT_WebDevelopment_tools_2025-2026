#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo "Локальный предпросмотр: mkdocs serve"
echo "Публикация на GitHub Pages: mkdocs gh-deploy"

if [[ "${1:-}" == "--deploy" ]]; then
  mkdocs gh-deploy --force
else
  mkdocs build --strict
  echo "Сборка завершена: $ROOT/site"
fi
