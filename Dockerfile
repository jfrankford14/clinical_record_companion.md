FROM python:3.11-slim
WORKDIR /app
# Copy the demo project directory
COPY clinical-record-companion /app/clinical-record-companion
ENV PYTHONPATH=/app/clinical-record-companion
# Default shows CLI help; override with arguments as needed
CMD ["python", "-m", "clinical_record_companion", "--help"]