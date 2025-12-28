#!/bin/bash
# Render startup script

# Run database migrations if needed (uncomment when you have migrations)
# alembic upgrade head

# Start the application with gunicorn for production
gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} src.main:app
