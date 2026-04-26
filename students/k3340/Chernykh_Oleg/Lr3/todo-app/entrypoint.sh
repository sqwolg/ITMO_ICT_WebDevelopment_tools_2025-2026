#!/bin/sh

set -e

echo "Running migrations..."
poetry run aerich upgrade

echo "Starting application..."
exec poetry run todo_app
