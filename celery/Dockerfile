FROM python:3.10

WORKDIR /app

COPY django_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .django_server /app
COPY celery_app.py /app/celery/celery_app.py
COPY tasks.py /app/celery/tasks.py

CMD ["celery", "-A", "celery.celery_app", "worker", "--loglevel=info"]
