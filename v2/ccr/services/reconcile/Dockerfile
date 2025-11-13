FROM python:3.11-slim

# 1) Basic hygiene
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# 2) Workdir and code
WORKDIR /app
COPY v2/ccr/services/reconcile/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire v2 package (so imports like v2.ccr.services.reconcile.app work)
COPY v2 /app/v2
ENV PYTHONPATH=/app

# 3) Start FastAPI with uvicorn, binding to the Cloud Run port
CMD exec uvicorn v2.ccr.services.reconcile.app:app --host 0.0.0.0 --port ${PORT:-8080}
