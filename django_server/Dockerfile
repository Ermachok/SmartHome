FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc python3-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir netifaces

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s \
  CMD curl -f http://localhost:8000/ || exit 1
