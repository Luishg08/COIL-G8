FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "pytest>=8.0.0" \
    "pytest-json-report>=1.5.0"

CMD ["pytest", "--json-report", "--tb=short", "-q"]
