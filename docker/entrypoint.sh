#!/bin/bash
set -e
echo "Running database migrations..."
alembic upgrade head
echo "Starting Jobly bot..."
exec python -m jobly.main
