#!/bin/bash
# Render startup script

# Run database migrations if needed (uncomment when you have migrations)
# alembic upgrade head

# Start the application with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
