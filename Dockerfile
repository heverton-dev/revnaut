FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY backend/ ./backend/
COPY data/ ./data/
COPY static/ ./static/
COPY docs/ ./docs/
COPY run_server.py .

EXPOSE 8000

CMD ["python", "run_server.py"]
