FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY test ./test
COPY conftest.py pytest.ini ./

# Créer un utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD ["python", "src/main.py"]
