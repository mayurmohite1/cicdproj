#syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY ./app .

RUN pip install --no-cache-dir -r /app/api/requirements.txt
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]