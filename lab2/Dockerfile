FROM python:3.11-slim

# Не пишем .pyc, не буферизуем stdout (удобнее логи)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Сначала зависимости — лучше кешируется
COPY requirements.txt .
RUN pip install -r requirements.txt --index-url https://artifactory.tcsbank.ru/artifactory/api/pypi/python-all/simple

# Затем код
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]