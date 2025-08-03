# docker/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY ../backend/requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ../backend .

CMD ["gunicorn", "credit_system.wsgi:application", "--bind", "0.0.0.0:8000"]
