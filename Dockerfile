FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY timelog/ timelog/

RUN pip install --no-cache-dir .

EXPOSE 8888

CMD ["python", "-m", "uvicorn", "timelog.api:app", "--host", "0.0.0.0", "--port", "8888"]
