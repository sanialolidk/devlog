FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -e .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "devlog.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
